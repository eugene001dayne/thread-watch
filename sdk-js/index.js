const fetch = require("node-fetch");

class ThreadWatch {
  constructor(baseUrl = "https://thread-watch.onrender.com") {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  async _request(method, path, body = null) {
    const options = { method, headers: { "Content-Type": "application/json" } };
    if (body) options.body = JSON.stringify(body);
    const res = await fetch(`${this.baseUrl}${path}`, options);
    if (!res.ok) throw new Error(`ThreadWatch error: ${res.status} ${await res.text()}`);
    return res.json();
  }

  ingestIronThread({ status, confidenceScore = null, latencyMs = null, runId = null, schemaId = null, autoCorrected = false, metadata = {} }) {
    return this._request("POST", "/signals/iron-thread", {
      status, confidence_score: confidenceScore, latency_ms: latencyMs,
      run_id: runId, schema_id: schemaId, auto_corrected: autoCorrected, metadata
    });
  }

  ingestTestThread({ passRate = null, regression = false, driftDetected = false, suiteId = null, runId = null, piiDetectedCount = 0, avgLatencyMs = null, signalType = "test_run", metadata = {} }) {
    return this._request("POST", "/signals/testthread", {
      pass_rate: passRate, regression, drift_detected: driftDetected,
      suite_id: suiteId, run_id: runId, pii_detected_count: piiDetectedCount,
      avg_latency_ms: avgLatencyMs, signal_type: signalType, metadata
    });
  }

  ingestPromptThread({ passRate = null, avgLatencyMs = null, avgCostUsd = null, alertFired = false, driftDetected = false, promptId = null, signalType = "prompt_run", metadata = {} }) {
    return this._request("POST", "/signals/promptthread", {
      pass_rate: passRate, avg_latency_ms: avgLatencyMs, avg_cost_usd: avgCostUsd,
      alert_fired: alertFired, drift_detected: driftDetected, prompt_id: promptId,
      signal_type: signalType, metadata
    });
  }

  ingestChainThread({ contractPassed = true, confidence = null, piiDetected = false, hitlEscalated = false, chainId = null, envelopeId = null, signalType = "handoff_envelope", metadata = {} }) {
    return this._request("POST", "/signals/chainthread", {
      contract_passed: contractPassed, confidence, pii_detected: piiDetected,
      hitl_escalated: hitlEscalated, chain_id: chainId, envelope_id: envelopeId,
      signal_type: signalType, metadata
    });
  }

  ingestPolicyThread({ passed = true, violationCount = 0, hasCritical = false, escalated = false, interactionId = null, signalType = "policy_evaluation", metadata = {} }) {
    return this._request("POST", "/signals/policythread", {
      passed, violation_count: violationCount, has_critical: hasCritical,
      escalated, interaction_id: interactionId, signal_type: signalType, metadata
    });
  }

  getSignals(tool = null, limit = 50) {
    const params = new URLSearchParams({ limit });
    if (tool) params.append("tool", tool);
    return this._request("GET", `/signals?${params}`);
  }

  getBaselines(tool = null) {
    const q = tool ? `?tool=${tool}` : "";
    return this._request("GET", `/baselines${q}`);
  }

  recomputeBaselines() {
    return this._request("POST", "/baselines/recompute");
  }

  stats() { return this._request("GET", "/dashboard/stats"); }
  health() { return this._request("GET", "/health"); }

  getAnomalies({ tool = null, severity = null, resolved = null, limit = 50 } = {}) {
    const params = new URLSearchParams({ limit });
    if (tool) params.append("tool", tool);
    if (severity) params.append("severity", severity);
    if (resolved !== null) params.append("resolved", resolved);
    return this._request("GET", `/anomalies?${params}`);
  }

  resolveAnomaly(anomalyId) {
    return this._request("PATCH", `/anomalies/${anomalyId}/resolve`);
  }

  anomalySummary() {
    return this._request("GET", "/anomalies/summary");
  }

  getDiagnoses({ tool = null, category = null, severity = null, resolved = null, limit = 50 } = {}) {
    const params = new URLSearchParams({ limit });
    if (tool) params.append("tool", tool);
    if (category) params.append("category", category);
    if (severity) params.append("severity", severity);
    if (resolved !== null) params.append("resolved", resolved);
    return this._request("GET", `/diagnoses?${params}`);
  }

  getDiagnosis(anomalyId) {
    return this._request("GET", `/diagnoses/${anomalyId}`);
  }

createWebhook(name, url, minSeverity = "warning") {
    return this._request("POST", "/webhooks", { name, url, min_severity: minSeverity });
  }

  listWebhooks() {
    return this._request("GET", "/webhooks");
  }

  deleteWebhook(webhookId) {
    return this._request("DELETE", `/webhooks/${webhookId}`);
  }

  getWatchAlerts({ tool = null, severity = null, acknowledged = null, limit = 50 } = {}) {
    const params = new URLSearchParams({ limit });
    if (tool) params.append("tool", tool);
    if (severity) params.append("severity", severity);
    if (acknowledged !== null) params.append("acknowledged", acknowledged);
    return this._request("GET", `/watch-alerts?${params}`);
  }

  acknowledgeAlert(alertId) {
    return this._request("PATCH", `/watch-alerts/${alertId}/acknowledge`);
  }
}

module.exports = ThreadWatch;