# threadwatch

JavaScript SDK for [ThreadWatch](https://github.com/eugene001dayne/thread-watch) — cross-layer pipeline vigilance for the Thread Suite.

## Install

```bash
npm install threadwatch
```

## Quick start

```javascript
const ThreadWatch = require("threadwatch");
const tw = new ThreadWatch(); // defaults to https://thread-watch.onrender.com

// Send signals from each Thread Suite tool
await tw.ingestIronThread({ status: "passed", confidenceScore: 0.92, latencyMs: 210 });
await tw.ingestTestThread({ passRate: 0.85, regression: false, avgLatencyMs: 340 });
await tw.ingestPromptThread({ passRate: 0.91, avgLatencyMs: 280, avgCostUsd: 0.00018 });
await tw.ingestChainThread({ contractPassed: true, confidence: 0.88, piiDetected: false });
await tw.ingestPolicyThread({ passed: true, violationCount: 0, hasCritical: false });
```

## Anomaly detection

```javascript
const result = await tw.ingestIronThread({
  status: "failed",
  confidenceScore: 0.10,
  latencyMs: 9000
});

if (result.anomaly_count > 0) {
  for (const anomaly of result.anomalies_detected) {
    console.log(anomaly.severity);            // "critical"
    console.log(anomaly.diagnosis_category);  // "performance_degradation"
    console.log(anomaly.recommended_action);  // plain-English guidance
  }
}
```

## Webhooks and alerts

```javascript
await tw.createWebhook("My Alert", "https://hooks.slack.com/your-url", "warning");

const alerts = await tw.getWatchAlerts({ acknowledged: false });
await tw.acknowledgeAlert(alertId);
```

## External signal monitoring

```javascript
await tw.pollProviders();

await tw.createExternalSignal({
  signalType: "provider_incident",
  source: "anthropic",
  title: "Anthropic API elevated latency",
  severity: "warning"
});

await tw.correlate(2); // window in hours
```

## Cross-tool correlation

```javascript
const chains = await tw.crossToolCorrelate(60); // window in minutes
const analysis = await tw.analyzeAnomaly(anomalyId);
const health = await tw.pipelineHealth(1);

console.log(health.pipeline_health_score); // 0.0–1.0
console.log(health.pipeline_status);       // "healthy", "degraded", "critical"
```

## All methods

```javascript
// Signal ingestion
tw.ingestIronThread({ status, confidenceScore, latencyMs, ... })
tw.ingestTestThread({ passRate, regression, driftDetected, ... })
tw.ingestPromptThread({ passRate, avgLatencyMs, avgCostUsd, ... })
tw.ingestChainThread({ contractPassed, confidence, piiDetected, ... })
tw.ingestPolicyThread({ passed, violationCount, hasCritical, ... })

// Signals and baselines
tw.getSignals(tool, limit)
tw.getBaselines(tool)
tw.recomputeBaselines()

// Anomalies and diagnoses
tw.getAnomalies({ tool, severity, resolved, limit })
tw.resolveAnomaly(anomalyId)
tw.anomalySummary()
tw.getDiagnoses({ tool, category, severity, resolved, limit })
tw.getDiagnosis(anomalyId)

// Alerts and webhooks
tw.createWebhook(name, url, minSeverity)
tw.listWebhooks()
tw.deleteWebhook(webhookId)
tw.getWatchAlerts({ tool, severity, acknowledged, limit })
tw.acknowledgeAlert(alertId)

// External signals
tw.pollProviders()
tw.createExternalSignal({ signalType, source, title, ... })
tw.listExternalSignals({ source, limit })
tw.correlate(windowHours)

// Cross-tool correlation
tw.crossToolCorrelate(windowMinutes)
tw.analyzeAnomaly(anomalyId)
tw.listCausalChains({ resolved, limit })
tw.pipelineHealth(windowHours)

// Status
tw.stats()
tw.health()
```

## Live API

`https://thread-watch.onrender.com`

## Part of the Thread Suite

- [Iron-Thread](https://github.com/eugene001dayne/iron-thread)
- [TestThread](https://github.com/eugene001dayne/test-thread)
- [PromptThread](https://github.com/eugene001dayne/prompt-thread)
- [ChainThread](https://github.com/eugene001dayne/chain-thread)
- [PolicyThread](https://github.com/eugene001dayne/policy-thread)
- [ThreadWatch](https://github.com/eugene001dayne/thread-watch)

## License

Apache 2.0