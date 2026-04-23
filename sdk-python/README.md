# threadwatch

Python SDK for [ThreadWatch](https://github.com/eugene001dayne/thread-watch) — cross-layer pipeline vigilance for the Thread Suite.

ThreadWatch watches all five Thread Suite tools simultaneously, detects anomalies across layers, diagnoses what went wrong, fires alerts, and finds causal chains when multiple tools fail together.

## Install

```bash
pip install threadwatch
```

## Quick start

```python
from threadwatch import ThreadWatch

tw = ThreadWatch()  # defaults to https://thread-watch.onrender.com

# Send a signal from Iron-Thread
tw.ingest_iron_thread(status="passed", confidence_score=0.92, latency_ms=210)

# Send a signal from TestThread
tw.ingest_testthread(pass_rate=0.85, regression=False, avg_latency_ms=340)

# Send a signal from PromptThread
tw.ingest_promptthread(pass_rate=0.91, avg_latency_ms=280, avg_cost_usd=0.00018)

# Send a signal from ChainThread
tw.ingest_chainthread(contract_passed=True, confidence=0.88, pii_detected=False)

# Send a signal from PolicyThread
tw.ingest_policythread(passed=True, violation_count=0, has_critical=False)
```

## Anomaly detection

ThreadWatch automatically detects anomalies on every signal. Once a metric has 5+ samples in its baseline, deviations beyond 2 standard deviations are flagged as warnings, 3+ as critical.

```python
result = tw.ingest_iron_thread(status="failed", confidence_score=0.10, latency_ms=9000)

if result["anomaly_count"] > 0:
    for anomaly in result["anomalies_detected"]:
        print(anomaly["severity"])            # "critical"
        print(anomaly["diagnosis_category"])  # "performance_degradation"
        print(anomaly["recommended_action"])  # plain-English guidance
```

## Watch alerts and webhooks

```python
# Register a webhook to receive alerts
tw.create_webhook(
    name="My Slack Alert",
    url="https://hooks.slack.com/your-url",
    min_severity="warning"
)

# List unacknowledged alerts
alerts = tw.get_watch_alerts(acknowledged=False)

# Acknowledge an alert
tw.acknowledge_alert(alert_id="alert-uuid")
```

## External signal monitoring

```python
# Poll Anthropic, OpenAI, and Google status pages
tw.poll_providers()

# Register a manual external event
tw.create_external_signal(
    signal_type="provider_incident",
    source="anthropic",
    title="Anthropic API elevated latency",
    severity="warning",
    status="investigating"
)

# Correlate pipeline anomalies with external events
tw.correlate(window_hours=2)
```

## Cross-tool correlation

```python
# Find causal chains across tools in the last 60 minutes
tw.cross_tool_correlate(window_minutes=60)

# Analyze one anomaly for upstream causes and downstream effects
tw.analyze_anomaly(anomaly_id="anomaly-uuid")

# Pipeline health score (0.0–1.0)
health = tw.pipeline_health(window_hours=1)
print(health["pipeline_health_score"])  # e.g. 0.85
print(health["pipeline_status"])        # "healthy", "degraded", or "critical"
```

## All methods

```python
# Signal ingestion
tw.ingest_iron_thread(status, confidence_score, latency_ms, ...)
tw.ingest_testthread(pass_rate, regression, drift_detected, ...)
tw.ingest_promptthread(pass_rate, avg_latency_ms, avg_cost_usd, ...)
tw.ingest_chainthread(contract_passed, confidence, pii_detected, ...)
tw.ingest_policythread(passed, violation_count, has_critical, ...)

# Signals and baselines
tw.get_signals(tool, limit)
tw.get_baselines(tool)
tw.recompute_baselines()

# Anomalies and diagnoses
tw.get_anomalies(tool, severity, resolved, limit)
tw.resolve_anomaly(anomaly_id)
tw.anomaly_summary()
tw.get_diagnoses(tool, category, severity, resolved, limit)
tw.get_diagnosis(anomaly_id)

# Alerts and webhooks
tw.create_webhook(name, url, min_severity)
tw.list_webhooks()
tw.delete_webhook(webhook_id)
tw.get_watch_alerts(tool, severity, acknowledged, limit)
tw.acknowledge_alert(alert_id)

# External signals
tw.poll_providers()
tw.create_external_signal(signal_type, source, title, ...)
tw.list_external_signals(source, limit)
tw.correlate(window_hours)

# Cross-tool correlation
tw.cross_tool_correlate(window_minutes)
tw.analyze_anomaly(anomaly_id)
tw.list_causal_chains(resolved, limit)
tw.pipeline_health(window_hours)

# Status
tw.stats()
tw.health()
```

## Live API

`https://thread-watch.onrender.com` — free tier, cold start on first request after inactivity.

## Part of the Thread Suite

ThreadWatch is the roof of the Thread Suite — a portfolio of open-source AI agent reliability tools.

- [Iron-Thread](https://github.com/eugene001dayne/iron-thread) — output structure validation
- [TestThread](https://github.com/eugene001dayne/test-thread) — agent behavior testing
- [PromptThread](https://github.com/eugene001dayne/prompt-thread) — prompt versioning and performance
- [ChainThread](https://github.com/eugene001dayne/chain-thread) — agent handoff verification
- [PolicyThread](https://github.com/eugene001dayne/policy-thread) — production compliance monitoring
- [ThreadWatch](https://github.com/eugene001dayne/thread-watch) — cross-layer pipeline vigilance

## License

Apache 2.0