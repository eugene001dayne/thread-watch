# ThreadWatch

**Cross-layer pipeline vigilance for the Thread Suite.**

ThreadWatch is the roof of the Thread Suite. Each Thread Suite tool watches one layer — Iron-Thread watches output structure, TestThread watches agent behavior, PromptThread watches prompt performance, ChainThread watches handoffs, PolicyThread watches compliance. ThreadWatch watches all of them simultaneously.

When multiple tools show anomalies at the same time, ThreadWatch finds the causal chain, identifies the root layer, and tells you where to look first.

## Live API

`https://thread-watch.onrender.com` · [API Docs](https://thread-watch.onrender.com/docs)

## Install

```bash
pip install threadwatch
npm install threadwatch
```

## What it does

**Signal ingestion** — accepts structured signals from all five Thread Suite tools. Every signal is stored and used to build baselines per metric per tool.

**Anomaly detection** — on every signal, observed metrics are compared against the historical baseline using Welford's online algorithm. Deviations beyond 2 standard deviations are flagged as warnings. Beyond 3 sigma: critical.

**Diagnosis engine** — every anomaly is classified into one of seven categories and paired with a plain-English recommended action. Categories: `structural_degradation`, `behavioral_drift`, `prompt_degradation`, `coordination_failure`, `compliance_breach`, `performance_degradation`, `cost_spike`.

**Watch alerts and webhooks** — every anomaly generates an alert record. Configured webhooks receive the full diagnosis payload instantly. Severity-scoped: configure webhooks to fire on warning, critical, or both.

**External signal monitoring** — polls Anthropic, OpenAI, and Google status pages for active incidents. When an external event coincides with pipeline anomalies, ThreadWatch correlates them: "this anomaly may be explained by the Anthropic API incident detected 14 minutes ago."

**Cross-tool correlation** — scans the pipeline for anomalies across multiple tools in a time window. Groups them into causal chains using the pipeline flow map. When iron-thread fails and chainthread fails shortly after, ThreadWatch identifies iron-thread as the root cause and tells you to fix it first.

**Pipeline health score** — a single 0.0–1.0 score across the entire pipeline, weighted by tool position and anomaly density. Statuses: `healthy`, `degraded`, `critical`.

## API endpoints
GET  /                                    Status + version
GET  /health                              Health check
POST /signals/iron-thread                 Ingest Iron-Thread signal
POST /signals/testthread                  Ingest TestThread signal
POST /signals/promptthread                Ingest PromptThread signal
POST /signals/chainthread                 Ingest ChainThread signal
POST /signals/policythread                Ingest PolicyThread signal
GET  /signals                             List signals (filterable by tool)
GET  /baselines                           All computed baselines
POST /baselines/recompute                 Recompute baselines from history
GET  /anomalies                           List anomalies
GET  /anomalies/summary                   Anomaly counts by tool, severity, category
PATCH /anomalies/{id}/resolve             Mark anomaly resolved
GET  /diagnoses                           Anomalies with full diagnosis context
GET  /diagnoses/{id}                      Full detail on one anomaly
POST /webhooks                            Register webhook
GET  /webhooks                            List webhooks
DELETE /webhooks/{id}                     Deactivate webhook
GET  /watch-alerts                        List fired alerts
PATCH /watch-alerts/{id}/acknowledge      Acknowledge alert
POST /external-signals                    Register external event manually
GET  /external-signals                    List external signals
POST /external-signals/poll               Poll Anthropic, OpenAI, Google status pages
GET  /external-signals/correlate          Correlate anomalies with external events
GET  /correlate/cross-tool                Find causal chains across tools
POST /correlate/cross-tool/analyze        Analyze one anomaly for upstream/downstream context
GET  /causal-chains                       List stored causal chains
GET  /pipeline/health                     Pipeline health score
GET  /dashboard/stats                     Full dashboard stats

## Python SDK

```python
from threadwatch import ThreadWatch

tw = ThreadWatch()

tw.ingest_iron_thread(status="passed", confidence_score=0.92, latency_ms=210)

result = tw.ingest_iron_thread(status="failed", confidence_score=0.10, latency_ms=9000)
# result["anomalies_detected"] contains diagnosis + recommended action

health = tw.pipeline_health()
print(health["pipeline_health_score"])  # 0.0–1.0
```

## JavaScript SDK

```javascript
const ThreadWatch = require("threadwatch");
const tw = new ThreadWatch();

await tw.ingestIronThread({ status: "passed", confidenceScore: 0.92, latencyMs: 210 });

const health = await tw.pipelineHealth();
console.log(health.pipeline_health_score);
```

## The Thread Suite

| Tool | Mission | Install |
|------|---------|---------|
| [Iron-Thread](https://github.com/eugene001dayne/iron-thread) | Output structure validation | `pip install iron-thread` |
| [TestThread](https://github.com/eugene001dayne/test-thread) | Agent behavior testing | `pip install testthread` |
| [PromptThread](https://github.com/eugene001dayne/prompt-thread) | Prompt versioning and performance | `pip install promptthread` |
| [ChainThread](https://github.com/eugene001dayne/chain-thread) | Agent handoff verification | `pip install chainthread` |
| [PolicyThread](https://github.com/eugene001dayne/policy-thread) | Production compliance monitoring | `pip install policythread` |
| [ThreadWatch](https://github.com/eugene001dayne/thread-watch) | Cross-layer pipeline vigilance | `pip install threadwatch` |

## Built by

Eugene Dayne Mawuli · GitHub: [eugene001dayne](https://github.com/eugene001dayne) · Accra, Ghana

## License

Apache 2.0