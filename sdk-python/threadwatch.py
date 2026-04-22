import httpx
from typing import Optional, Dict, Any


class ThreadWatch:
    def __init__(self, base_url: str = "https://thread-watch.onrender.com"):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(base_url=self.base_url)

    def ingest_iron_thread(self, status: str, confidence_score: float = None,
                           latency_ms: int = None, run_id: str = None,
                           schema_id: str = None, auto_corrected: bool = False,
                           metadata: Dict = {}):
        r = self.client.post("/signals/iron-thread", json={
            "status": status, "confidence_score": confidence_score,
            "latency_ms": latency_ms, "run_id": run_id,
            "schema_id": schema_id, "auto_corrected": auto_corrected, "metadata": metadata
        })
        r.raise_for_status()
        return r.json()

    def ingest_testthread(self, pass_rate: float = None, regression: bool = False,
                          drift_detected: bool = False, suite_id: str = None,
                          run_id: str = None, pii_detected_count: int = 0,
                          avg_latency_ms: float = None, signal_type: str = "test_run",
                          metadata: Dict = {}):
        r = self.client.post("/signals/testthread", json={
            "pass_rate": pass_rate, "regression": regression,
            "drift_detected": drift_detected, "suite_id": suite_id,
            "run_id": run_id, "pii_detected_count": pii_detected_count,
            "avg_latency_ms": avg_latency_ms, "signal_type": signal_type, "metadata": metadata
        })
        r.raise_for_status()
        return r.json()

    def ingest_promptthread(self, pass_rate: float = None, avg_latency_ms: float = None,
                            avg_cost_usd: float = None, alert_fired: bool = False,
                            drift_detected: bool = False, prompt_id: str = None,
                            signal_type: str = "prompt_run", metadata: Dict = {}):
        r = self.client.post("/signals/promptthread", json={
            "pass_rate": pass_rate, "avg_latency_ms": avg_latency_ms,
            "avg_cost_usd": avg_cost_usd, "alert_fired": alert_fired,
            "drift_detected": drift_detected, "prompt_id": prompt_id,
            "signal_type": signal_type, "metadata": metadata
        })
        r.raise_for_status()
        return r.json()

    def ingest_chainthread(self, contract_passed: bool = True, confidence: float = None,
                           pii_detected: bool = False, hitl_escalated: bool = False,
                           chain_id: str = None, envelope_id: str = None,
                           signal_type: str = "handoff_envelope", metadata: Dict = {}):
        r = self.client.post("/signals/chainthread", json={
            "contract_passed": contract_passed, "confidence": confidence,
            "pii_detected": pii_detected, "hitl_escalated": hitl_escalated,
            "chain_id": chain_id, "envelope_id": envelope_id,
            "signal_type": signal_type, "metadata": metadata
        })
        r.raise_for_status()
        return r.json()

    def ingest_policythread(self, passed: bool = True, violation_count: int = 0,
                            has_critical: bool = False, escalated: bool = False,
                            interaction_id: str = None, signal_type: str = "policy_evaluation",
                            metadata: Dict = {}):
        r = self.client.post("/signals/policythread", json={
            "passed": passed, "violation_count": violation_count,
            "has_critical": has_critical, "escalated": escalated,
            "interaction_id": interaction_id, "signal_type": signal_type, "metadata": metadata
        })
        r.raise_for_status()
        return r.json()

    def get_signals(self, tool: str = None, limit: int = 50):
        params = {"limit": limit}
        if tool:
            params["tool"] = tool
        r = self.client.get("/signals", params=params)
        r.raise_for_status()
        return r.json()

    def get_baselines(self, tool: str = None):
        params = {}
        if tool:
            params["tool"] = tool
        r = self.client.get("/baselines", params=params)
        r.raise_for_status()
        return r.json()

    def recompute_baselines(self):
        r = self.client.post("/baselines/recompute")
        r.raise_for_status()
        return r.json()

    def stats(self):
        r = self.client.get("/dashboard/stats")
        r.raise_for_status()
        return r.json()

    def health(self):
        r = self.client.get("/health")
        r.raise_for_status()
        return r.json()

    def get_anomalies(self, tool: str = None, severity: str = None,
                      resolved: bool = None, limit: int = 50):
        params = {"limit": limit}
        if tool:
            params["tool"] = tool
        if severity:
            params["severity"] = severity
        if resolved is not None:
            params["resolved"] = str(resolved).lower()
        r = self.client.get("/anomalies", params=params)
        r.raise_for_status()
        return r.json()

    def resolve_anomaly(self, anomaly_id: str):
        r = self.client.patch(f"/anomalies/{anomaly_id}/resolve")
        r.raise_for_status()
        return r.json()

    def anomaly_summary(self):
        r = self.client.get("/anomalies/summary")
        r.raise_for_status()
        return r.json()

    def get_diagnoses(self, tool: str = None, category: str = None,
                      severity: str = None, resolved: bool = None, limit: int = 50):
        params = {"limit": limit}
        if tool: params["tool"] = tool
        if category: params["category"] = category
        if severity: params["severity"] = severity
        if resolved is not None: params["resolved"] = str(resolved).lower()
        r = self.client.get("/diagnoses", params=params)
        r.raise_for_status()
        return r.json()

    def get_diagnosis(self, anomaly_id: str):
        r = self.client.get(f"/diagnoses/{anomaly_id}")
        r.raise_for_status()
        return r.json()

    def create_webhook(self, name: str, url: str, min_severity: str = "warning"):
        r = self.client.post("/webhooks", json={
            "name": name, "url": url, "min_severity": min_severity
        })
        r.raise_for_status()
        return r.json()

    def list_webhooks(self):
        r = self.client.get("/webhooks")
        r.raise_for_status()
        return r.json()

    def delete_webhook(self, webhook_id: str):
        r = self.client.delete(f"/webhooks/{webhook_id}")
        r.raise_for_status()
        return r.json()

    def get_watch_alerts(self, tool: str = None, severity: str = None,
                         acknowledged: bool = None, limit: int = 50):
        params = {"limit": limit}
        if tool: params["tool"] = tool
        if severity: params["severity"] = severity
        if acknowledged is not None: params["acknowledged"] = str(acknowledged).lower()
        r = self.client.get("/watch-alerts", params=params)
        r.raise_for_status()
        return r.json()

    def acknowledge_alert(self, alert_id: str):
        r = self.client.patch(f"/watch-alerts/{alert_id}/acknowledge")
        r.raise_for_status()
        return r.json()