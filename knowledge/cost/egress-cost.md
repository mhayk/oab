---
id: egress-cost
title: Egress Cost
description: >-
  Data transfer out of a provider is routinely the largest and most surprising line on an
  infrastructure invoice, and edge offload is usually the biggest single saving available.
category: cost
tags: [cost, bandwidth, cdn, egress]
maturity: reviewed
confidence: high
applies_at_stage: ["2", "3", "4", "5"]
related: [operational-cost-model, observability-cost]
complexity_cost: 1
trade_offs:
  - gains: "Edge offload commonly removes 70-90 percent of origin egress at a fraction of the per-GB price"
    costs: "One more component; cache invalidation to reason about; a second place where stale content can live"
    when_worth_it: >-
      Above roughly 1 TB/month of egress, or wherever payloads are media-heavy. Below a few
      hundred GB/month the saving does not repay the component.
failure_modes:
  - mode: "Egress never computed during design"
    symptom: "Invoice dominated by a line nobody modelled"
    detection: "Transfer charges exceeding compute charges"
    mitigation: "Compute egress in every capacity analysis where a material payload is served"
  - mode: "Cross-zone traffic ignored"
    symptom: "Internal traffic billed at per-GB rates between availability zones"
    detection: "Inter-zone transfer appearing as a distinct invoice line"
    mitigation: "Keep chatty components zone-local; measure inter-zone volume"
  - mode: "Cache configured to bypass on cookies or query strings"
    symptom: "Edge hit rate far below expectation; origin egress barely reduced"
    detection: "Edge hit rate under 50 percent for static assets"
    mitigation: "Normalise cache keys; strip irrelevant query parameters and cookies"
triggers:
  - metric: "egress volume"
    comparator: ">"
    threshold: 1
    unit: "TB/month"
    window: "sustained over 2 months"
    action: "Compute the cost of edge offload against current origin egress pricing"
anti_patterns:
  - "Serving user-uploaded media directly from application instances"
  - "Assuming internal traffic is free"
references:
  - title: "Cloud provider data transfer pricing"
    type: official-docs
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

Providers charge for bytes leaving their network, typically £0.04–0.09 per GB, while edge delivery
costs £0.005–0.02 per GB. Ingress is usually free, which is why the cost is invisible until traffic
grows.

```
egress_per_month = avg_rps × avg_payload_bytes × 2,592,000
cost             = origin_gb × origin_price + edge_gb × edge_price
```

## When it applies

Whenever a material payload is served. Compute it in every capacity analysis — it takes one
calculation and it is the line most often missed.

Worked example at scale: 50,000 requests/second at 8 KB is about **1 PB/month**. At £0.05/GB that is
roughly **£52,000/month**. With 85% edge offload it falls to about **£17,000** — a saving larger
than the entire compute fleet of a mid-sized service.

## When it does not apply

**Below a few hundred GB/month.** Free tiers typically cover it, and a CDN's complexity point is
not repaid.

**For API responses that are small and personalised.** A JSON API returning 2 KB of per-user data
cannot be edge-cached usefully. Egress still costs money, but offload is not the lever — payload
size is.

**Where the provider does not charge for it.** Some providers include generous or unlimited
transfer. Check before modelling it as a cost.

## How it works

Three separate lines are commonly conflated:

| Line | Typical price | Notes |
| :-- | :-- | :-- |
| Internet egress from origin | £0.04–0.09/GB | The big one |
| Edge/CDN egress | £0.005–0.02/GB | What offload converts it to |
| Cross-zone / cross-region | £0.008–0.015/GB | Internal, and invisible until the invoice arrives |

Cross-zone charges surprise teams who spread a chatty service across availability zones for
redundancy and pay per-GB for every internal call.

## Trade-offs

An edge cache is one managed component (1 point) and a new place stale content can live. Against
that it removes the majority of the largest invoice line. Above about 1 TB/month the trade is
overwhelmingly favourable.

## Failure modes

The most common operational failure is a cache configured so that it almost never hits: varying on
cookies, session identifiers, or tracking query parameters. A CDN with a 20% hit rate costs money
and saves nothing.

## Measurement

Track egress GB/month split by origin and edge, and edge hit rate by content type. Static assets
should be above 90%; below 50% indicates a cache-key problem rather than a traffic problem.

## Alternatives

| Approach | When to prefer |
| :-- | :-- |
| Edge cache | Default above ~1 TB/month, or any media-heavy payload |
| Reduce payload size | Small personalised API responses; often larger wins than offload |
| Provider with included transfer | When it does not compromise other requirements |

## References

Prices summarised from published provider documentation; see `_pricing.md` for the dated table.
