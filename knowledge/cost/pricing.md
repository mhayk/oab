# Indicative price table

> **Checked: 2026-08-09.** Prices are indicative, provider-neutral order-of-magnitude figures for
> estimation only. They are not quotes. Verify against your provider's current pricing before
> budgeting.
>
> CI warns when this file is more than 6 months old and fails at 12 months
> (`tools/check_price_staleness.py`). Undated prices rot, and a stale number stated confidently
> does more damage than no number.

Figures are monthly, in GBP, and describe *classes* of service rather than named products. OAB is
vendor-neutral: these are inputs to the `cost` calculator, not recommendations.

## Compute

| Class | Spec | GBP/month |
| :-- | :-- | --: |
| Small managed app instance | 0.5–1 vCPU, 512 MB–1 GB | 5–15 |
| Medium managed app instance | 2 vCPU, 4 GB | 30–50 |
| Large managed app instance | 4 vCPU, 8 GB | 70–120 |
| Small virtual machine | 2 vCPU, 4 GB | 15–25 |
| Serverless function | per million invocations, 256 MB, 200 ms | 0.20–0.60 |

## Databases

| Class | Spec | GBP/month |
| :-- | :-- | --: |
| Smallest managed relational | shared CPU, 1 GB RAM, 10 GB storage | 10–20 |
| Small managed relational | 2 vCPU, 8 GB RAM, 100 GB | 120–200 |
| Medium managed relational, multi-AZ | 4 vCPU, 16 GB, 500 GB, replicated | 400–600 |
| Read replica | same class as the primary | equal to primary |
| Managed key-value cache | 1–2 GB | 30–70 |
| Managed document database | 2 vCPU, 8 GB | 120–250 |

## Storage and transfer

| Class | Unit | GBP |
| :-- | :-- | --: |
| Object storage | per GB/month | 0.015–0.025 |
| Block storage (SSD) | per GB/month | 0.08–0.12 |
| Backup storage | per GB/month | 0.02–0.05 |
| **Origin egress** | **per GB** | **0.04–0.09** |
| Edge/CDN egress | per GB | 0.005–0.02 |
| Cross-zone transfer | per GB | 0.008–0.015 |

Origin egress is bold because it is the line that most often surprises. At scale it can exceed the
entire compute bill; see the worked example in `docs/design/08-technology-and-worked-examples.md` §36,
where 85% edge offload saves roughly $35,000/month.

## Queues, streams, observability

| Class | Unit | GBP |
| :-- | :-- | --: |
| Managed queue | per million requests | 0.30–0.50 |
| Managed event stream | per broker-hour, small | 0.08–0.15 |
| Log ingestion | per GB ingested | 0.40–2.00 |
| Metrics | per 100 custom series/month | 0.05–0.15 |
| Error tracking | small team plan | 20–80 |

Log ingestion is priced per GB and log volume grows superlinearly with traffic, which makes
observability the classic unbudgeted cost. Budget it explicitly at design time.

## Operational cost

Not a price table entry, but the line that decides most small-system architecture:

```
operational_cost_per_month = complexity_points × hours_per_point × loaded_hourly_rate
```

Defaults: **4 hours per point per month**, **£60/hour loaded** — roughly **£240 per complexity
point per month**. See `frameworks/complexity-budget/` for how points are counted, and note that
those constants are judgement rather than measurement.

## How to update

1. Check current published pricing for two or three providers in each class.
2. Record the **range**, not a point estimate.
3. Update the `Checked` date at the top.
4. Never name a provider as a recommendation — these are estimation inputs.
