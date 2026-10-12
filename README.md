# Campaign Performance — Week 01

A local Streamlit dashboard for synthetic campaign performance. Upload a CSV, filter by date/campaign/channel, compare performance, and download filtered records.

## Run locally

Python 3.9–3.13 is supported by the pinned V1 stack.

```bash
cd Week-01-project
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address 127.0.0.1
```

Open http://localhost:8501. Choose **Sample dataset** or **Upload CSV** in the sidebar. Uploads stay in memory and are not saved to disk. No Salesforce connection or credentials are needed for V1.

## CSV contract

Required columns: `date,campaign_id,campaign_name,channel,spend,clicks,purchases,revenue`.

- One row per campaign/channel/day; duplicate keys are rejected.
- Dates use `YYYY-MM-DD`. Identifiers, names, and channels must be populated.
- Numeric values must be finite and nonnegative. Clicks and purchases must be whole numbers.
- Each campaign ID has one consistent name. Additional columns are ignored.
- All amounts use **USD**, a V1 implementation assumption. Do not mix currencies.
- Purchases mean Closed Won opportunities. Revenue is the full opportunity amount assigned to its first campaign touch and recorded on its close date.
- Uploaded aggregates must already follow this attribution rule; the dashboard cannot reconstruct or verify touches from the eight-column CSV.

Spend/clicks represent daily activity; purchases/revenue represent close-date outcomes, potentially from earlier touches. Same-day ROAS therefore combines activity and closing outcomes, not a customer-cohort measurement. Cost per click = spend/clicks; cost per purchase = spend/purchases; ROAS = revenue/spend. Ratios use aggregated totals; zero denominators display N/A. Purchase-to-click conversion rate is omitted because closing purchases can originate from earlier dates.

## Synthetic supporting data

The sample selector now defaults to **June–September 2026 (all four months)**. Choose a single month in **Sample period**, or download the selected file directly from the sidebar. To import a file yourself, select **Upload CSV** and choose one of these files from `data/`:

| Period | Performance CSV | Daily rows |
| --- | --- | ---: |
| June 2026 | `sample_campaign_performance_2026_06.csv` | 73 |
| July 2026 | `sample_campaign_performance_2026_07.csv` | 145 |
| August 2026 | `sample_campaign_performance_2026_08.csv` | 71 |
| September 2026 | `sample_campaign_performance_2026_09.csv` | 135 |
| All four months | `sample_campaign_performance_2026_06_to_09.csv` | 424 |

Only June, July, August, and September 2026 are generated. All four months have been refreshed to show distinct scenarios; previously downloaded CSVs must be downloaded again to receive these changes. The original `sample_campaign_performance.csv` remains a September-only compatibility copy. Campaign names and IDs remain consistent across months, including the illustrative name Autumn Launch.

- **June:** Smaller budget and intermittent LinkedIn/email activity — 73 records, 45 purchases.
- **July:** Broader activity, a mid-month push, and additional Meta placements for Product Discovery — 145 records, 125 purchases. Meta leads purchases.
- **August:** Campaign pauses and weaker click efficiency — 71 records, 62 purchases. YouTube leads purchases, while overall ROAS drops.
- **September:** More late-month activity and strong email outcomes — 135 records, 188 purchases. ROAS recovers.

Active campaign schedules determine row counts. Missing rows mean no recorded activity/outcomes for that campaign/channel/day in these samples. Weekend effects, daily noise, budget shifts, win rates, and deal sizes vary. These are illustrative scenarios, not forecasts or real-world benchmarks.

Month-specific `sample_opportunities_2026_MM.csv` and `sample_campaign_touches_2026_MM.csv` preserve the opportunity and interaction records for an auditable Salesforce migration. Opportunity counts vary by month: 110 June, 210 July, 190 August, and 260 September; each opportunity has two or three touches. Combined supporting files end in `_2026_06_to_09.csv`; opportunity and touch IDs are unique across months. There are 420 Closed Won opportunities across the four months. Supporting files are not dashboard uploads. Synthetic touches and closing outcomes stay within their respective months; cross-month journeys can be added later.

First touch is the earliest linked touch on or before the close date; ties use `touch_id` order. Closed Lost records are excluded. Closed Won opportunities without an eligible touch remain unattributed. Synthetic touches link directly to opportunity IDs; V2 must define actual Salesforce contact/opportunity linkage. The dataset includes no personal data.

Regenerate and test:

```bash
python scripts/generate_sample_data.py
python -m unittest discover -s tests -v
```

## Structure and V2

`app.py` connects the interface to `src/campaign_dashboard/`. Sources read external data; transforms normalize it; validation checks its contract; metrics calculate summaries; charts build figures; UI modules render Streamlit controls and results. These boundaries allow a Salesforce source/transform to produce the same reporting format later.

The planned V2 model uses standard Campaign records with a related custom Campaign Performance object for daily measures, and standard Opportunities/Campaign Influence for first-touch reporting. Salesforce configuration, authentication, influence-model implementation, and customer touch relationships remain future work.

`PROJECT_CONTEXT.md` records decisions and remaining questions. `.gitignore` excludes the virtual environment, credentials, and caches. Git publication is a later step.
