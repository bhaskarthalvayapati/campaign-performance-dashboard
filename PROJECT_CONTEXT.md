# Gen Academy Mastering Agentic AI — Week 01 Project

Last updated: October 11, 2026.

## Working instructions

- Implementation is authorized: the user requested generating V1 code and testing locally on October 11, 2026. Earlier brainstorming-only restrictions are superseded for this build.
- Generate and test V1 locally. Do not push to GitHub during this step.
- Explicit build authorization received: “Alright let us start now on the build and test it locally, before we push it to the Git. Start generating the code for v1”.
- Discuss questions and trade-offs one decision at a time.
- Treat architectural suggestions as provisional until explicitly confirmed.
- Frequently update this file to preserve context, confirmed decisions, proposals, and unresolved questions. The user explicitly authorized these documentation updates during brainstorming.
- On resuming, read this file and continue from the current discussion rather than restarting discovery.

## Project purpose and user-stated choices

- Build a campaign performance data application for the Week 01 project.
- Use Streamlit and run the application locally on the user's Mac through localhost.
- Version one accepts CSV uploads directly in the application and visualizes the uploaded data.
- Start with a small, synthetic dataset; a large or real dataset is unnecessary.
- Include charts, filters, tables, and dashboard visualizations. Initial styling can be simple.
- Explore iterative prompting and additional analysis workflows over time.
- Optionally add AI-powered interactions or summaries toward the end; these are not a committed version-one requirement.
- Use Codex throughout the project interaction.
- Eventually publish the project in a public GitHub repository, learn the Git workflow, and share it with Gen Academy participants, including Aishwarya, Arvind, and the TAs. No GitHub publication has occurred or is currently authorized as an immediate action.

## Desired campaign information

The user wants to explore spend, audience targeting, clicks, email opens and bounces, conversions, actual purchases, and conversion performance by platform. Example channels mentioned include Email, YouTube, LinkedIn, and Meta. Exact metrics and definitions remain undecided.

## Confirmed version-one data structure

The user accepted the illustrative daily dataset as suitable for version one.

- One row per campaign, per channel, per day.
- Initial columns: `date`, `campaign_id`, `campaign_name`, `channel`, `spend`, `clicks`, `purchases`, and `revenue`.
- Example campaigns: Autumn Launch across Meta and LinkedIn, and Customer Winback through Email. These are illustrative synthetic examples, not required campaign names.
- Daily records can be grouped into campaign/channel totals and support daily trend charts.
- Currency and precise metric definitions still need confirmation. The sample described purchases as attributed purchases; the attribution approach is not yet confirmed.

## Additional data model proposals — not yet confirmed

- One row per campaign, per channel, per day.
- A campaign can run across multiple channels, each represented by separate daily rows.
- Earlier suggestions included `impressions` and generic `conversions`. These are not part of the accepted initial eight-column sample; discuss additions separately.
- Suggested email-specific columns: `emails_sent`, `emails_delivered`, `unique_opens`, `unique_email_clicks`, and `emails_bounced`.
- Fields that do not apply to a channel would be blank. Zero would mean a measured count of zero.
- Calculate derived metrics from uploaded counts rather than storing redundant rates. Aggregate rates should use summed numerators and denominators rather than averages of row-level rates.

### Definitions to resolve

- Whether conversions mean purchases only or include other outcomes.
- Whether conversion counts are attributed by individual platforms or represent deduplicated business outcomes. Platform-attributed conversions may overlap across channels.
- How intended audience size (users targeted) differs from actual reach, and which measures to include.
- Whether common `clicks` represents unique or total clicks, and how it relates to email-specific clicks.
- Which metrics apply to each channel, and the CSV validation rules.
- Currency, date conventions, campaign identifiers, and synthetic dataset size.

## Provisional dashboard ideas — not yet confirmed

| View | Purpose |
| --- | --- |
| Overview | Summarize spend, conversions, revenue, and efficiency |
| Channel comparison | Compare channel performance |
| Performance over time | Show daily spend, conversions, and revenue trends |
| Email performance | Explore delivery, opens, clicks, bounces, and purchases |

Suggested shared filters: date range, campaign, and channel. Include a detailed table for inspecting uploaded records.

Potential calculated metrics include click-through rate, cost per click, cost per conversion, return on ad spend, and email engagement rates. Exact denominators remain to be agreed.

## Current discussion and next decision

The user confirmed: “The data above looks good for version 1,” referring to the daily sample with `date`, `campaign_id`, `campaign_name`, `channel`, `spend`, `clicks`, `purchases`, and `revenue`. Row granularity and the initial columns are now settled.

Purchase attribution is settled: first touch receives 100% of Closed Won revenue on the opportunity close date. See the attribution direction and implementation defaults below.

Continue refining metric definitions and CSV fields one decision at a time. Other open areas include currency, optional email fields, CSV validation, dashboard priorities, visualization and data-processing libraries, upload/storage behavior, optional AI scope, and the eventual Git learning workflow.

## Reference context

## Version-two Salesforce direction and architecture discussion

### Confirmed first-touch attribution direction

- The user approved a custom `Campaign_Performance__c` object to preserve daily V1 data in Salesforce.
- Use first-touch attribution from the outset, including when designing V1 synthetic datasets.
- The user wants opportunity close dates to anchor performance reporting, with attribution to the first campaign.
- Proposed precise interpretation, pending clarification if needed: identify the earliest eligible campaign touch for an opportunity on or before its close date, assign 100% of the opportunity revenue to that campaign, and report the purchase/revenue on the opportunity close date. For realized purchases/revenue, include Closed Won opportunities only. The campaign touch timestamp determines first touch; the close date determines the reporting day.
- Earliest touch refers to customer interaction, not campaign creation/start date. Eligibility and contact-to-opportunity linkage rules still need definition.
- V1's accepted eight-column daily CSV remains the reporting format. To preserve auditable attribution and enable Salesforce migration, also propose supporting synthetic opportunity and campaign-touch datasets from V1: stable opportunity IDs, amounts, stages, close dates, campaign IDs, channels, touch timestamps, and explicit opportunity/touch linkage. These supporting datasets are proposed, not yet approved as additional uploads.
- Derive `purchases` and `revenue` in the daily CSV from those supporting records using first-touch attribution; spend and clicks remain daily activity measures. A row's revenue may therefore come from touches on earlier days.
- For opportunities with no eligible touch, equal touch timestamps, changes to close dates, and multiple contacts, rules remain open. Do not silently attribute to a campaign.
- Standard `CampaignInfluence` and `CampaignInfluenceModel` were recommended rather than a custom influence object. Exact Salesforce model configuration/writability and channel representation require discovery; do not assume a built-in first-touch model is available in this Developer Edition org.
- Synthetic datasets are now generated under the user's explicit V1 build authorization.

- The user approved the suggested separation-of-concerns project structure: a short Streamlit entry point, separate loading, validation, metrics, charts, UI, sample data, and focused tests.
- The user wants version two to integrate Salesforce Developer Edition, including Campaign, Campaign Influence, and related objects.
- Additional requirement: preserve all eight version-one attributes through CSV import into Salesforce and retrieval back into Streamlit.
- Proposed architecture refinement (not yet confirmed): separate source retrieval (`sources/`) from reporting transformations (`transforms/`), with both sources producing the same dashboard format.
- Recommended Salesforce mapping (provisional): standard Campaign records for campaign identity, with a related custom `Campaign_Performance__c` object storing one record per campaign/channel/day. Custom fields would preserve date, channel, spend, clicks, purchases, and revenue. A custom external ID on Campaign would preserve CSV IDs such as C001; a unique external key on performance records would support repeatable imports.
- Standard Campaign cost is campaign-level and does not directly preserve daily channel spend. Aggregate CSV rows also cannot reconstruct individual CampaignMember, Opportunity, or CampaignInfluence records. Those require separate detailed synthetic records if included in version two.
- Customizable Campaign Influence documentation lists Developer Edition availability, but org configuration and access still require verification.
- No Salesforce configuration, authentication, import, or implementation has been performed. All mapping names are proposed.

### Salesforce references consulted

- Campaign fields: https://help.salesforce.com/s/articleView?id=sales.campaigns_fields.htm&language=en_US
- Customizable Campaign Influence: https://help.salesforce.com/s/articleView?id=sales.campaigns_influence_customizable_understanding.htm&language=en_US&type=5

- The user supplied a shared ChatGPT conversation: https://chatgpt.com/share/6acbf01d-ed00-83ea-82de-d4f38aa7e0ee
- The browser could not retrieve it. The user subsequently pasted the project brief into this chat; the scope above reflects that brief and the ensuing discussion.
- V1 implementation and dataset generation have begun under explicit user authorization.

## V1 implementation status

- Implemented a local Streamlit dashboard with CSV upload/sample selection, date/campaign/channel filters, seven KPI cards, daily and channel charts, comparison tables, and filtered CSV download.
- Separated source retrieval, transformations, validation, metrics, chart construction, and UI rendering.
- Generated deterministic synthetic data: 120 daily rows, 160 opportunities (128 Closed Won), and 320 touch records. Supporting records reconcile first-touch purchases/revenue to daily records.
- Implementation assumptions: USD throughout; purchases/revenue include Closed Won only; attribution uses the earliest eligible linked touch on/before close date; equal timestamps use touch ID order. These are documented defaults rather than separately confirmed business decisions.
- CSV validation rejects missing fields, blank identifiers, invalid dates, nonfinite/negative numbers, fractional counts, duplicate daily keys, and inconsistent campaign names.
- Installed pinned Streamlit, pandas, and Plotly packages in the project-local `.venv`.
- Validation complete: all 10 unittest tests passed, including Streamlit AppTest filter interactions, mocked valid/invalid uploads, attribution reconciliation, and metric edge cases. `pip check` reported no broken requirements.
- Streamlit is running at http://127.0.0.1:8501 and its health endpoint returned `ok`. No manual browser visual review has been performed.
- No Salesforce connection or GitHub push has been performed. Next step is user review of the local dashboard.

## Four-month dataset update — October 11, 2026

- User requested exactly June, July, August, and September; interpreted as 2026 to match the existing September dataset.
- Generated June, July, and August without changing existing September data (verified byte-for-byte for performance and supporting records).
- Month-specific performance files: `data/sample_campaign_performance_2026_06.csv`, `_2026_07.csv`, `_2026_08.csv`, and `_2026_09.csv`.
- Combined upload: `data/sample_campaign_performance_2026_06_to_09.csv`, containing 488 rows (120 June, 124 July, 124 August, 120 September). No months outside June–September are generated.
- Supporting opportunity/touch files follow the same monthly and combined naming scheme. IDs are unique across months; 640 opportunities, 1,280 touches, and 512 Closed Won opportunities in total. First-touch attribution reconciles to all daily performance records. Synthetic journeys stay within each month.
- Original unqualified filenames remain September-only compatibility copies.
- Streamlit sample mode now defaults to all four months, offers a monthly sample selector, and allows downloading the selected sample. Users can upload any monthly performance file or the combined CSV using the existing uploader.
- README includes the month-specific file guide. All 12 tests passed, including four-month validation, unique supporting IDs, attribution reconciliation, monthly UI selection, and combined-upload behavior (mocked uploader). No manual browser file upload was performed.
- No Salesforce connection or GitHub push has been performed.

## Header color update — October 11, 2026

- User requested aesthetically coordinated colors for dashboard and sidebar headings.
- Added `ui/styles.py` for centralized light/dark palettes: blue for the main title and trend-chart title, teal for channel reporting, filters and KPI labels, purple for campaign comparison and metric definitions, amber for the data source heading, and muted blue-gray for records and control labels.
- Heading helpers retain semantic heading levels and escape their text. Chart title colors use the same palette. Backgrounds and data calculations remain as before.
- Verification: all 12 existing tests pass with the new styles applied. Browser visual review remains pending.

## Button styling and layout update — October 11, 2026

- User requested updated button layout and appearance.
- Moved filtered CSV export into a right-aligned toolbar next to the Daily records heading; uses a filled blue primary button, download icon, and matching record count.
- Sidebar sample download uses a full-width outlined secondary button. Upload browse controls use the same rounded blue outline style.
- Centralized light/dark button colors, hover feedback, keyboard focus rings, disabled appearance, and reduced-motion support in `ui/styles.py`. Downloads use `on_click="ignore"` to avoid unnecessary dashboard reruns.
- Verification: all 12 existing tests passed after the layout update; browser visual review remains pending.

## Varied monthly scenarios and row counts — October 11, 2026

- User requested apparent differences in data and variable row counts when loading months.
- Regenerated all June–September performance and supporting CSVs with month-specific budgets, click efficiency, opportunity volume, win rates, deal sizes, channel mix, and activity schedules. This supersedes prior September preservation and prior row/purchase counts. Filenames and the eight-column reporting contract remain unchanged.
- June: 73 performance rows, 45 purchases, $4,571.88 spend, $21,280 revenue, 4.65x ROAS. Smaller budget and intermittent email/LinkedIn schedules.
- July: 145 rows, 125 purchases, $22,846.84 spend, $74,030 revenue, 3.24x ROAS. Mid-month expansion; Meta leads.
- August: 71 rows, 62 purchases, $10,800.79 spend, $26,212.50 revenue, 2.43x ROAS. Pauses and weaker efficiency; YouTube leads.
- September: 135 rows, 188 purchases, $15,519.27 spend, $127,270 revenue, 8.20x ROAS. Late-month recovery; Email leads.
- Combined performance file now has 424 rows and 420 attributed purchases. Supporting opportunity counts are 110, 210, 190, and 260 respectively; touch counts also vary, with two or three touches per opportunity.
- Active schedules determine which campaign/channel/day rows exist. Opportunities and touches are sampled on active days to preserve full first-touch reconciliation. Each month still covers every calendar date; journeys remain within the month.
- All 13 tests passed, including checks of visibly different monthly metrics, varied row counts, channel leadership, CSV integrity, and reconciliation of supporting records. README updated.
- To see the new data: refresh sample mode or download/re-upload the updated CSV. Previously downloaded files and an already uploaded in-memory CSV retain their earlier contents until replaced.

## Functional project documentation — October 11, 2026

- User requested approximately two pages of project documentation, focused primarily on functionality, to copy into a Google Doc.
- Prepared chat content describing purpose, CSV loading, filters, dashboard metrics, charts/tables, first-touch attribution, varied monthly datasets, exports, validation, current boundaries, and planned Salesforce V2. No Google Doc was created or published.

## GitHub publication guidance — October 11, 2026

- User wants to publish the current code publicly and specifically learn terminal Git commands such as `git push`.
- Read-only inspection confirmed that the project is not yet a Git repository and Git commit identity is configured. Existing `.gitignore` excludes `.venv`, caches, `.env`, and Streamlit secrets.
- Provide instructions to create an empty public GitHub repository, initialize Git inside `Week-01-project`, stage/review/commit files, configure the origin remote, and push `main`. HTTPS authentication requires a token or credential helper rather than an account password.
- Guidance only: no Git initialization, commit, remote creation, or push performed.
