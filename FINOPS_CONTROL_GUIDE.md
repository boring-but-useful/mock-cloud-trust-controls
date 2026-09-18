# FinOps Control Guide

This guide explains the reasoning behind the mock FinOps controls. The examples are synthetic and provider-neutral at the control layer.

## What The Controls Cover

### MCTC-COST-01: Allocation And Ownership

The first question is not "How do we cut the bill?" It is "Can we explain the bill and identify who can act on it?"

Useful evidence includes:

- amortized cost by service, account or project, environment, and owner
- tag or label coverage and the percentage of unallocated spend
- documented rules for shared costs such as observability, networking, and platform services
- an ownership map that connects billing dimensions to accountable teams

Allocation does not need to be perfect before it becomes useful. The important operational signals are the unallocated percentage, its trend, and whether gaps have owners.

### MCTC-COST-02: Budgets, Forecasts, And Anomalies

Budgets are detection and coordination controls, not hard service limits. A useful design combines:

- budget and forecast thresholds at meaningful scopes
- anomaly detection for unexpected changes that static thresholds may miss
- routed notifications with an accountable responder
- a triage record explaining expected growth, deployment changes, abuse, configuration errors, or pricing effects

An alert that nobody owns is not an operating control. Thresholds should be tuned so teams receive actionable signals rather than recurring noise.

### MCTC-COST-03: Optimization With Reliability Guardrails

Optimization recommendations are inputs to engineering decisions, not automatic instructions. Review them against:

- utilization over representative peak and quiet periods
- latency, saturation, availability, recovery, and growth requirements
- stateful-service and failover headroom
- implementation and rollback risk
- expected savings and the time needed to realize them
- commitment coverage, utilization, term, and break-even assumptions

Low-risk cleanup may be automated. Rightsizing stateful or latency-sensitive systems usually needs load evidence, staged change, and post-change validation.

## AWS And GCP Evidence Mapping

| Need | AWS example | Google Cloud example | Common evidence |
|---|---|---|---|
| Allocation | Cost and Usage Report, cost allocation tags | Cloud Billing export, labels | Ownership map and shared-cost rules |
| Budgets and anomalies | AWS Budgets, Cost Anomaly Detection | Cloud Billing budgets and export analysis | Forecast review and response ticket |
| Optimization | Cost Optimization Hub, Compute Optimizer | Recommender | Utilization telemetry and decision record |
| Commitments | Savings Plans and Reserved Instance reporting | Committed use discount reporting | Approval, coverage, utilization, and break-even review |

The service names differ, but the control questions remain stable: what is expected, what was observed, who owns the decision, what risk constrains action, and how will the result be verified?

## Interview Walkthrough

A compact way to discuss the design:

> I would start by making spend attributable, because optimization without ownership becomes a report nobody can act on. Then I would add budgets, forecasts, and anomaly routing so material variance reaches an accountable team. For optimization, I would combine provider recommendations with service telemetry and change-management evidence. I would automate low-risk cleanup, but I would not blindly rightsize stateful or latency-sensitive systems without peak-load, resilience, and rollback analysis. I would track both savings and reliability outcomes so FinOps does not become cost cutting at the expense of the platform.

Useful follow-up questions:

- How much spend is currently allocated to a team, service, and environment?
- Are shared platform costs charged back, shown back, or centrally funded?
- Who receives budget and anomaly alerts, and what happens next?
- Which cost drivers are growing faster than customer or transaction volume?
- How are Savings Plans, reservations, or committed use decisions approved?
- Which workloads intentionally retain headroom because of latency, resilience, or peak-demand requirements?
- Are cost changes reviewed alongside security, performance, and reliability changes?

## Main Trade-Offs

- Detailed allocation improves accountability but creates tagging and data-maintenance work.
- Aggressive anomaly thresholds detect more changes but increase alert noise.
- Higher commitment coverage can reduce unit cost but increases forecast and lock-in risk.
- Rightsizing can reduce waste but may reduce burst, failover, or recovery headroom.
- Chargeback creates direct accountability but can encourage local optimization; showback is gentler but may create weaker incentives.

The goal is not the lowest possible bill. The goal is explainable spend, timely decisions, efficient architecture, and business value without unmanaged reliability or security risk.
