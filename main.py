from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import httpx
import os
import math
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def get_client():
    return httpx.Client(base_url=f"{SUPABASE_URL}/rest/v1", headers=HEADERS)

app = FastAPI(
    title="ThreadWatch",
    description="Cross-layer pipeline vigilance for the Thread Suite.",
    version="0.3.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Models ───────────────────────────────────────────────────────────────────

class IronThreadSignal(BaseModel):
    run_id: Optional[str] = None
    schema_id: Optional[str] = None
    status: str
    confidence_score: Optional[float] = None
    latency_ms: Optional[int] = None
    auto_corrected: Optional[bool] = False
    metadata: Optional[Dict[str, Any]] = {}

class TestThreadSignal(BaseModel):
    suite_id: Optional[str] = None
    run_id: Optional[str] = None
    pass_rate: Optional[float] = None
    regression: Optional[bool] = False
    pii_detected_count: Optional[int] = 0
    avg_latency_ms: Optional[float] = None
    drift_detected: Optional[bool] = False
    signal_type: Optional[str] = "test_run"
    metadata: Optional[Dict[str, Any]] = {}

class PromptThreadSignal(BaseModel):
    prompt_id: Optional[str] = None
    pass_rate: Optional[float] = None
    avg_latency_ms: Optional[float] = None
    avg_cost_usd: Optional[float] = None
    alert_fired: Optional[bool] = False
    drift_detected: Optional[bool] = False
    signal_type: Optional[str] = "prompt_run"
    metadata: Optional[Dict[str, Any]] = {}

class ChainThreadSignal(BaseModel):
    chain_id: Optional[str] = None
    envelope_id: Optional[str] = None
    contract_passed: Optional[bool] = True
    confidence: Optional[float] = None
    pii_detected: Optional[bool] = False
    hitl_escalated: Optional[bool] = False
    signal_type: Optional[str] = "handoff_envelope"
    metadata: Optional[Dict[str, Any]] = {}

class PolicyThreadSignal(BaseModel):
    interaction_id: Optional[str] = None
    passed: Optional[bool] = True
    violation_count: Optional[int] = 0
    has_critical: Optional[bool] = False
    escalated: Optional[bool] = False
    signal_type: Optional[str] = "policy_evaluation"
    metadata: Optional[Dict[str, Any]] = {}

# ─── Metric extraction ────────────────────────────────────────────────────────

def extract_metrics(source_tool: str, payload: Dict) -> Dict[str, float]:
    metrics = {}

    if source_tool == "iron-thread":
        status = payload.get("status", "failed")
        metrics["pass_rate"] = 1.0 if status == "passed" else (0.5 if status == "corrected" else 0.0)
        if payload.get("confidence_score") is not None:
            metrics["confidence_score"] = float(payload["confidence_score"])
        if payload.get("latency_ms") is not None:
            metrics["latency_ms"] = float(payload["latency_ms"])

    elif source_tool == "testthread":
        if payload.get("pass_rate") is not None:
            metrics["pass_rate"] = float(payload["pass_rate"])
        if payload.get("avg_latency_ms") is not None:
            metrics["latency_ms"] = float(payload["avg_latency_ms"])
        metrics["regression_rate"] = 1.0 if payload.get("regression") else 0.0
        metrics["drift_rate"] = 1.0 if payload.get("drift_detected") else 0.0

    elif source_tool == "promptthread":
        if payload.get("pass_rate") is not None:
            metrics["pass_rate"] = float(payload["pass_rate"])
        if payload.get("avg_latency_ms") is not None:
            metrics["latency_ms"] = float(payload["avg_latency_ms"])
        if payload.get("avg_cost_usd") is not None:
            metrics["cost_usd"] = float(payload["avg_cost_usd"])
        metrics["alert_rate"] = 1.0 if payload.get("alert_fired") else 0.0
        metrics["drift_rate"] = 1.0 if payload.get("drift_detected") else 0.0

    elif source_tool == "chainthread":
        metrics["contract_pass_rate"] = 1.0 if payload.get("contract_passed", True) else 0.0
        if payload.get("confidence") is not None:
            metrics["confidence"] = float(payload["confidence"])
        metrics["pii_rate"] = 1.0 if payload.get("pii_detected") else 0.0
        metrics["hitl_rate"] = 1.0 if payload.get("hitl_escalated") else 0.0

    elif source_tool == "policythread":
        metrics["pass_rate"] = 1.0 if payload.get("passed", True) else 0.0
        if payload.get("violation_count") is not None:
            metrics["violation_count"] = float(payload["violation_count"])
        metrics["critical_rate"] = 1.0 if payload.get("has_critical") else 0.0
        metrics["escalation_rate"] = 1.0 if payload.get("escalated") else 0.0

    return metrics

# ─── Diagnosis engine ─────────────────────────────────────────────────────────

def diagnose(source_tool: str, metric_name: str,
             observed_value: float, baseline_mean: float) -> tuple:
    direction = "high" if observed_value > baseline_mean else "low"

    if source_tool == "iron-thread":
        if metric_name == "pass_rate" and direction == "low":
            return "structural_degradation", (
                "AI outputs are failing structure validation more than usual. "
                "Check if the upstream model changed or if the prompt was modified recently."
            )
        if metric_name == "confidence_score" and direction == "low":
            return "structural_degradation", (
                "Validated outputs are statistically anomalous. Values are passing schema "
                "but look different from historical norms — possible model drift or data shift."
            )
        if metric_name == "latency_ms" and direction == "high":
            return "performance_degradation", (
                "Iron-Thread validation latency is spiking. Check if auto-correction is "
                "triggering more frequently or if the Gemini API is responding slowly."
            )

    elif source_tool == "testthread":
        if metric_name == "pass_rate" and direction == "low":
            return "behavioral_drift", (
                "Agent is failing more behavioral tests than baseline. Run the full test suite "
                "manually and check for recent prompt or model changes."
            )
        if metric_name == "regression_rate" and direction == "high":
            return "behavioral_drift", (
                "Regression detected — agent is performing worse than a previous run. "
                "Compare current and previous test results to isolate newly failing cases."
            )
        if metric_name == "drift_rate" and direction == "high":
            return "behavioral_drift", (
                "Production monitoring is detecting behavioral drift. The agent's live "
                "behavior has diverged from its tested behavior. Review recent interactions."
            )
        if metric_name == "latency_ms" and direction == "high":
            return "performance_degradation", (
                "Agent response latency is spiking. Check if the agent's underlying model "
                "or external tools are experiencing delays."
            )

    elif source_tool == "promptthread":
        if metric_name == "pass_rate" and direction == "low":
            return "prompt_degradation", (
                "Prompt pass rate has dropped. Check if the prompt was recently modified "
                "or if the model is behaving differently on this prompt version."
            )
        if metric_name == "alert_rate" and direction == "high":
            return "prompt_degradation", (
                "PromptThread alerts are firing more than usual. Check alert configs for "
                "pass rate, latency, and cost thresholds — one may have been crossed repeatedly."
            )
        if metric_name == "drift_rate" and direction == "high":
            return "prompt_degradation", (
                "World drift detected — the model may now be wrong about facts this prompt "
                "relies on. Review drift anchor results in PromptThread dashboard."
            )
        if metric_name == "cost_usd" and direction == "high":
            return "cost_spike", (
                "Prompt cost per run is spiking. Check if outputs are getting longer, "
                "if token usage has increased, or if the model being called has changed."
            )
        if metric_name == "latency_ms" and direction == "high":
            return "performance_degradation", (
                "Prompt execution latency is spiking. Check model provider status "
                "and whether prompt complexity has increased recently."
            )

    elif source_tool == "chainthread":
        if metric_name == "contract_pass_rate" and direction == "low":
            return "coordination_failure", (
                "Agent handoffs are failing contract validation more than usual. Check which "
                "agent pairs are failing and review their contract field requirements."
            )
        if metric_name == "hitl_rate" and direction == "high":
            return "coordination_failure", (
                "More handoffs are escalating to human review than baseline. An upstream agent "
                "may be producing outputs that consistently fail contract assertions."
            )
        if metric_name == "pii_rate" and direction == "high":
            return "coordination_failure", (
                "PII is being detected in handoff payloads more frequently than usual. "
                "Review which agents are handling sensitive data and verify redaction is configured."
            )
        if metric_name == "confidence" and direction == "low":
            return "coordination_failure", (
                "Handoff confidence scores are dropping. Check if confidence decay across hops "
                "is compounding, or if source agents are returning lower-quality outputs."
            )

    elif source_tool == "policythread":
        if metric_name == "pass_rate" and direction == "low":
            return "compliance_breach", (
                "More production interactions are violating policies than baseline. Review "
                "recent violations in PolicyThread and check if a new interaction pattern has emerged."
            )
        if metric_name == "critical_rate" and direction == "high":
            return "compliance_breach", (
                "Critical severity policy violations are spiking. Immediate review required — "
                "check PolicyThread violations filtered by severity: critical."
            )
        if metric_name == "escalation_rate" and direction == "high":
            return "compliance_breach", (
                "Policy escalations are firing more than usual. Adaptive escalation rules may "
                "be triggering repeatedly — review PolicyThread escalation configs."
            )
        if metric_name == "violation_count" and direction == "high":
            return "compliance_breach", (
                "Violation count per interaction is rising. A single interaction may be "
                "triggering multiple policies simultaneously — check for overlapping rules."
            )

    # Generic fallbacks
    if metric_name == "latency_ms" and direction == "high":
        return "performance_degradation", (
            f"Latency spike detected on {source_tool}. Check service health "
            "and upstream dependencies for slowdowns."
        )

    return "unknown_anomaly", (
        f"Anomaly detected on {source_tool}/{metric_name}. "
        f"Observed {observed_value:.4f} vs baseline mean {baseline_mean:.4f}. "
        "Investigate recent changes to this layer."
    )

# ─── Baseline update (Welford's online algorithm) ─────────────────────────────

def update_baselines(source_tool: str, metrics: Dict[str, float]):
    for metric_name, new_value in metrics.items():
        client = get_client()
        try:
            resp = client.get(
                "/baselines",
                params={
                    "metric_name": f"eq.{metric_name}",
                    "source_tool": f"eq.{source_tool}",
                    "select": "*"
                }
            )
            existing = resp.json() if resp.status_code == 200 else []

            if existing:
                row = existing[0]
                n = row["sample_count"]
                old_mean = row["mean_value"] or 0.0
                old_std = row["std_deviation"] or 0.0

                n_new = n + 1
                delta = new_value - old_mean
                new_mean = old_mean + delta / n_new
                delta2 = new_value - new_mean
                old_m2 = (old_std ** 2) * n if n > 1 else 0.0
                new_m2 = old_m2 + delta * delta2
                new_std = math.sqrt(new_m2 / n_new) if n_new > 1 else 0.0

                client.patch(
                    f"/baselines?id=eq.{row['id']}",
                    json={
                        "mean_value": new_mean,
                        "std_deviation": new_std,
                        "sample_count": n_new,
                        "last_updated": datetime.now(timezone.utc).isoformat()
                    }
                )
            else:
                client.post("/baselines", json={
                    "metric_name": metric_name,
                    "source_tool": source_tool,
                    "mean_value": new_value,
                    "std_deviation": 0.0,
                    "sample_count": 1,
                    "last_updated": datetime.now(timezone.utc).isoformat()
                })
        finally:
            client.close()

# ─── Anomaly detection + diagnosis ───────────────────────────────────────────

MIN_SAMPLES_FOR_DETECTION = 5
WARNING_SIGMA = 2.0
CRITICAL_SIGMA = 3.0

def detect_anomalies(source_tool: str, metrics: Dict[str, float]) -> List[Dict]:
    detected = []
    client = get_client()
    try:
        for metric_name, observed_value in metrics.items():
            resp = client.get(
                "/baselines",
                params={
                    "metric_name": f"eq.{metric_name}",
                    "source_tool": f"eq.{source_tool}",
                    "select": "*"
                }
            )
            if resp.status_code != 200:
                continue
            rows = resp.json()
            if not rows:
                continue

            baseline = rows[0]
            sample_count = baseline.get("sample_count", 0)
            if sample_count < MIN_SAMPLES_FOR_DETECTION:
                continue

            mean = baseline.get("mean_value", 0.0) or 0.0
            std = baseline.get("std_deviation", 0.0) or 0.0

            if std < 0.0001:
                continue

            sigma = abs(observed_value - mean) / std

            if sigma >= WARNING_SIGMA:
                severity = "critical" if sigma >= CRITICAL_SIGMA else "warning"
                category, recommended_action = diagnose(
                    source_tool, metric_name, observed_value, mean
                )

                anomaly_record = {
                    "source_tool": source_tool,
                    "metric_name": metric_name,
                    "observed_value": observed_value,
                    "baseline_mean": mean,
                    "baseline_std": std,
                    "deviation_sigma": round(sigma, 3),
                    "severity": severity,
                    "diagnosis_category": category,
                    "recommended_action": recommended_action,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }

                write_client = get_client()
                try:
                    write_resp = write_client.post("/anomalies", json=anomaly_record)
                    written = write_resp.json()[0] if write_resp.status_code in (200, 201) else {}
                finally:
                    write_client.close()

                detected.append({
                    "anomaly_id": written.get("id"),
                    "metric": metric_name,
                    "observed": observed_value,
                    "mean": round(mean, 4),
                    "sigma": round(sigma, 3),
                    "severity": severity,
                    "diagnosis_category": category,
                    "recommended_action": recommended_action
                })
    finally:
        client.close()

    return detected

# ─── Core ingestion ───────────────────────────────────────────────────────────

def _ingest(source_tool: str, signal_type: str, payload: Dict) -> Dict:
    client = get_client()
    try:
        resp = client.post("/pipeline_signals", json={
            "source_tool": source_tool,
            "signal_type": signal_type,
            "payload": payload,
            "recorded_at": datetime.now(timezone.utc).isoformat()
        })
        row = resp.json()[0] if resp.status_code in (200, 201) else {}
    finally:
        client.close()

    metrics = extract_metrics(source_tool, payload)
    anomalies = detect_anomalies(source_tool, metrics)
    update_baselines(source_tool, metrics)

    result = {
        "received": True,
        "signal_id": row.get("id"),
        "source_tool": source_tool,
        "signal_type": signal_type,
        "metrics_tracked": list(metrics.keys()),
        "anomalies_detected": anomalies,
        "anomaly_count": len(anomalies)
    }

    if anomalies:
        severities = [a["severity"] for a in anomalies]
        result["highest_severity"] = "critical" if "critical" in severities else "warning"
        categories = list({a["diagnosis_category"] for a in anomalies})
        result["diagnosis_categories"] = categories

    return result

# ─── Status endpoints ─────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "tool": "ThreadWatch",
        "version": "0.3.0",
        "status": "running",
        "description": "Cross-layer pipeline vigilance for the Thread Suite.",
        "layers_watched": ["iron-thread", "testthread", "promptthread", "chainthread", "policythread"]
    }

@app.get("/health")
def health():
    try:
        client = get_client()
        resp = client.get("/pipeline_signals", params={"select": "id", "limit": "1"})
        db_ok = resp.status_code == 200
        client.close()
    except Exception:
        db_ok = False
    return {"status": "ok" if db_ok else "degraded", "database": "connected" if db_ok else "unreachable"}

# ─── Signal ingestion endpoints ───────────────────────────────────────────────

@app.post("/signals/iron-thread")
def ingest_iron_thread(signal: IronThreadSignal):
    return _ingest("iron-thread", "validation_run", signal.model_dump())

@app.post("/signals/testthread")
def ingest_testthread(signal: TestThreadSignal):
    payload = signal.model_dump()
    return _ingest("testthread", payload.get("signal_type", "test_run"), payload)

@app.post("/signals/promptthread")
def ingest_promptthread(signal: PromptThreadSignal):
    payload = signal.model_dump()
    return _ingest("promptthread", payload.get("signal_type", "prompt_run"), payload)

@app.post("/signals/chainthread")
def ingest_chainthread(signal: ChainThreadSignal):
    payload = signal.model_dump()
    return _ingest("chainthread", payload.get("signal_type", "handoff_envelope"), payload)

@app.post("/signals/policythread")
def ingest_policythread(signal: PolicyThreadSignal):
    payload = signal.model_dump()
    return _ingest("policythread", payload.get("signal_type", "policy_evaluation"), payload)

# ─── Signal retrieval ─────────────────────────────────────────────────────────

@app.get("/signals")
def list_signals(
    tool: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200)
):
    client = get_client()
    params = {"select": "*", "order": "recorded_at.desc", "limit": str(limit)}
    if tool:
        params["source_tool"] = f"eq.{tool}"
    resp = client.get("/pipeline_signals", params=params)
    client.close()
    signals = resp.json() if resp.status_code == 200 else []
    return {"signals": signals, "count": len(signals)}

# ─── Baselines ────────────────────────────────────────────────────────────────

@app.get("/baselines")
def get_baselines(tool: Optional[str] = Query(None)):
    client = get_client()
    params = {"select": "*", "order": "source_tool.asc,metric_name.asc"}
    if tool:
        params["source_tool"] = f"eq.{tool}"
    resp = client.get("/baselines", params=params)
    client.close()
    return {"baselines": resp.json() if resp.status_code == 200 else []}

@app.post("/baselines/recompute")
def recompute_baselines():
    tools = ["iron-thread", "testthread", "promptthread", "chainthread", "policythread"]
    recomputed = {}
    client = get_client()

    for tool in tools:
        resp = client.get(
            "/pipeline_signals",
            params={"source_tool": f"eq.{tool}", "order": "recorded_at.desc",
                    "limit": "100", "select": "payload"}
        )
        if resp.status_code != 200:
            recomputed[tool] = {"error": "fetch failed"}
            continue

        signals = resp.json()
        if not signals:
            recomputed[tool] = {"signal_count": 0, "metrics_recomputed": []}
            continue

        metric_values: Dict[str, list] = {}
        for s in signals:
            for k, v in extract_metrics(tool, s.get("payload", {})).items():
                metric_values.setdefault(k, []).append(v)

        for metric_name, values in metric_values.items():
            n = len(values)
            mean = sum(values) / n
            std = math.sqrt(sum((v - mean) ** 2 for v in values) / n) if n > 1 else 0.0

            check = client.get("/baselines", params={
                "metric_name": f"eq.{metric_name}", "source_tool": f"eq.{tool}", "select": "id"
            })
            existing = check.json() if check.status_code == 200 else []
            data = {
                "metric_name": metric_name, "source_tool": tool,
                "mean_value": mean, "std_deviation": std,
                "sample_count": n, "last_updated": datetime.now(timezone.utc).isoformat()
            }
            if existing:
                client.patch(f"/baselines?id=eq.{existing[0]['id']}", json=data)
            else:
                client.post("/baselines", json=data)

        recomputed[tool] = {"signal_count": len(signals), "metrics_recomputed": list(metric_values.keys())}

    client.close()
    return {"recomputed": True, "results": recomputed}

# ─── Anomaly endpoints ────────────────────────────────────────────────────────

@app.get("/anomalies")
def list_anomalies(
    tool: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    resolved: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=200)
):
    client = get_client()
    params = {"select": "*", "order": "created_at.desc", "limit": str(limit)}
    if tool:
        params["source_tool"] = f"eq.{tool}"
    if severity:
        params["severity"] = f"eq.{severity}"
    if resolved is not None:
        params["resolved"] = f"eq.{str(resolved).lower()}"
    resp = client.get("/anomalies", params=params)
    client.close()
    anomalies = resp.json() if resp.status_code == 200 else []
    return {"anomalies": anomalies, "count": len(anomalies)}

@app.patch("/anomalies/{anomaly_id}/resolve")
def resolve_anomaly(anomaly_id: str):
    client = get_client()
    try:
        resp = client.patch(
            f"/anomalies?id=eq.{anomaly_id}",
            json={"resolved": True, "resolved_at": datetime.now(timezone.utc).isoformat()}
        )
        rows = resp.json() if resp.status_code == 200 else []
        if not rows:
            return {"error": "anomaly not found"}
        return {"resolved": True, "anomaly_id": anomaly_id}
    finally:
        client.close()

@app.get("/anomalies/summary")
def anomaly_summary():
    client = get_client()
    try:
        all_resp = client.get("/anomalies", params={"select": "*", "resolved": "eq.false"})
        all_anomalies = all_resp.json() if all_resp.status_code == 200 else []

        by_tool = {}
        by_severity = {"warning": 0, "critical": 0}
        by_metric = {}
        by_category = {}

        for a in all_anomalies:
            tool = a.get("source_tool", "unknown")
            sev = a.get("severity", "warning")
            metric = a.get("metric_name", "unknown")
            category = a.get("diagnosis_category", "unknown")

            if tool not in by_tool:
                by_tool[tool] = {"warning": 0, "critical": 0, "total": 0}
            by_tool[tool][sev] += 1
            by_tool[tool]["total"] += 1
            by_severity[sev] += 1
            by_metric[metric] = by_metric.get(metric, 0) + 1
            by_category[category] = by_category.get(category, 0) + 1

        most_flagged = sorted(by_metric.items(), key=lambda x: x[1], reverse=True)[:5]
        top_categories = sorted(by_category.items(), key=lambda x: x[1], reverse=True)

        return {
            "total_unresolved": len(all_anomalies),
            "by_severity": by_severity,
            "by_tool": by_tool,
            "by_diagnosis_category": by_category,
            "top_diagnosis_categories": [{"category": c, "count": n} for c, n in top_categories],
            "most_flagged_metrics": [{"metric": m, "count": c} for m, c in most_flagged]
        }
    finally:
        client.close()

# ─── Diagnosis endpoints ──────────────────────────────────────────────────────

@app.get("/diagnoses")
def list_diagnoses(
    tool: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    resolved: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=200)
):
    client = get_client()
    params = {
        "select": "*",
        "order": "created_at.desc",
        "limit": str(limit),
        "diagnosis_category": "not.is.null"
    }
    if tool:
        params["source_tool"] = f"eq.{tool}"
    if category:
        params["diagnosis_category"] = f"eq.{category}"
    if severity:
        params["severity"] = f"eq.{severity}"
    if resolved is not None:
        params["resolved"] = f"eq.{str(resolved).lower()}"
    resp = client.get("/anomalies", params=params)
    client.close()
    diagnoses = resp.json() if resp.status_code == 200 else []
    return {"diagnoses": diagnoses, "count": len(diagnoses)}

@app.get("/diagnoses/{anomaly_id}")
def get_diagnosis(anomaly_id: str):
    client = get_client()
    try:
        resp = client.get(
            "/anomalies",
            params={"id": f"eq.{anomaly_id}", "select": "*"}
        )
        rows = resp.json() if resp.status_code == 200 else []
        if not rows:
            return {"error": "anomaly not found"}
        a = rows[0]
        return {
            "anomaly_id": a.get("id"),
            "source_tool": a.get("source_tool"),
            "metric_name": a.get("metric_name"),
            "observed_value": a.get("observed_value"),
            "baseline_mean": a.get("baseline_mean"),
            "baseline_std": a.get("baseline_std"),
            "deviation_sigma": a.get("deviation_sigma"),
            "severity": a.get("severity"),
            "diagnosis_category": a.get("diagnosis_category"),
            "recommended_action": a.get("recommended_action"),
            "resolved": a.get("resolved"),
            "created_at": a.get("created_at")
        }
    finally:
        client.close()

# ─── Dashboard ────────────────────────────────────────────────────────────────

@app.get("/dashboard/stats")
def dashboard_stats():
    tools = ["iron-thread", "testthread", "promptthread", "chainthread", "policythread"]
    client = get_client()

    total_resp = client.get("/pipeline_signals", params={"select": "id"})
    total = len(total_resp.json()) if total_resp.status_code == 200 else 0

    anomaly_resp = client.get("/anomalies", params={"select": "id", "resolved": "eq.false"})
    total_anomalies = len(anomaly_resp.json()) if anomaly_resp.status_code == 200 else 0

    critical_resp = client.get("/anomalies", params={
        "select": "id", "resolved": "eq.false", "severity": "eq.critical"
    })
    critical_anomalies = len(critical_resp.json()) if critical_resp.status_code == 200 else 0

    category_resp = client.get("/anomalies", params={
        "select": "diagnosis_category", "resolved": "eq.false"
    })
    category_counts = {}
    if category_resp.status_code == 200:
        for row in category_resp.json():
            cat = row.get("diagnosis_category", "unknown")
            if cat:
                category_counts[cat] = category_counts.get(cat, 0) + 1
    top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:3]

    per_tool = {}
    for tool in tools:
        count_resp = client.get("/pipeline_signals", params={"source_tool": f"eq.{tool}", "select": "id"})
        count = len(count_resp.json()) if count_resp.status_code == 200 else 0

        latest_resp = client.get("/pipeline_signals", params={
            "source_tool": f"eq.{tool}", "order": "recorded_at.desc",
            "limit": "1", "select": "recorded_at,signal_type"
        })
        latest = latest_resp.json()[0] if latest_resp.status_code == 200 and latest_resp.json() else None

        baseline_resp = client.get("/baselines", params={"source_tool": f"eq.{tool}", "select": "id"})
        baseline_count = len(baseline_resp.json()) if baseline_resp.status_code == 200 else 0

        tool_anomaly_resp = client.get("/anomalies", params={
            "source_tool": f"eq.{tool}", "resolved": "eq.false", "select": "id"
        })
        tool_anomalies = len(tool_anomaly_resp.json()) if tool_anomaly_resp.status_code == 200 else 0

        per_tool[tool] = {
            "signal_count": count,
            "metrics_baselined": baseline_count,
            "unresolved_anomalies": tool_anomalies,
            "last_signal_at": latest.get("recorded_at") if latest else None,
            "last_signal_type": latest.get("signal_type") if latest else None
        }

    client.close()
    return {
        "total_signals": total,
        "tools_watched": len(tools),
        "total_unresolved_anomalies": total_anomalies,
        "critical_anomalies": critical_anomalies,
        "top_diagnosis_categories": [{"category": c, "count": n} for c, n in top_categories],
        "per_tool": per_tool
    }