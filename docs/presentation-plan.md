# Presentation plan: DATA 398.1 Part 1 (10 minutes, in class)

## Scenario and audience (state these before you start)

> **Scenario:** a funding pitch to a community innovation fund (for example, a municipal
> or foundation grant for food-security tools).
> **Audience:** non-technical funders and community food-security partners, such as
> food banks and family-support agencies.
> **Ask:** seed funding and one partner agency to pilot CartCast YYC for six months.

Topic type: **a proposed solution to a real-world problem** (rising grocery costs).

## Engagement tool: live demonstration with audience participation

The class builds a basket live. A teammate asks the room for 3–4 items ("What's
always in your cart?") and adds them in the dashboard. The room watches the weekly
cost, the movers and the swaps update. Finish by applying a swap and showing the
savings. Optional: put a QR code to the shared-basket link on the slide so people
can open it on their phones.

## Run of show (adjust names and team size)

| Time | Who | Segment | Key points |
|---|---|---|---|
| 0:00–0:45 | Presenter 1 | Scenario + hook | State scenario and audience. "Hands up if your grocery bill went up this year." |
| 0:45–2:15 | Presenter 1 | The problem | Food Price Report 2026: +4–6% in 2026; family of four ≈ $17,572/yr; +27% in five years; Alberta above national average. Record Calgary Food Bank demand, including working households |
| 2:15–3:30 | Presenter 2 | The solution + the data | What CartCast does in one sentence. Four open datasets. Pipeline diagram (README). Average prices vs CPI caveat |
| 3:30–7:00 | Presenters 3 + 2 | **Live demo** | Household → Couple. Audience adds items. Read the movers. Apply a swap and watch the savings KPI. Store map: filter a community. Copy the share link |
| 7:00–8:30 | Presenter 4 | Impact + roadmap | Who uses it (households, agency caseworkers). Pilot metrics: weekly active users, swaps applied, $ saved per household. Cost: free hosting, ~2 hrs/month maintenance |
| 8:30–9:15 | Presenter 4 | The ask | Seed funding + one partner agency + feedback on the basket |
| 9:15–10:00 | All | Close / Q&A buffer | Repeat the one-line value proposition |

## Slide outline (8 slides)

1. Title + scenario + audience
2. The problem in three numbers
3. Who feels it (food bank context)
4. CartCast in one screen (`design/cartcast_mockup.png`)
5. The data (four sources + licences) and the methodology caveat
6. *(Live demo, no slide, or a "demo" title card)*
7. Pilot plan, metrics and costs
8. The ask + thank you

## Demo checklist

- [ ] Run `make data build` the night before, so the demo uses **live** data and has no sample banner
- [ ] Also keep `site/index.html` from a `make build-sample` run on a USB stick as an offline fallback
- [ ] Browser zoom at 110–125% for the projector. Close other tabs
- [ ] Pre-load the default basket. Practise: Couple → add "Avocado, unit" → apply the top swap → filter the map
- [ ] Screenshots of every demo step in hidden backup slides, in case the laptop or projector fails
- [ ] One person drives, one narrates. Never type in silence

## Likely questions

- **"Why Alberta prices, not Calgary?"** StatCan publishes average prices by province only. The CPI is available for the Calgary CMA, which we use for context.
- **"Isn't price change over time misleading?"** StatCan says average prices aren't a pure inflation measure, so the inflation KPI uses the CPI.
- **"How do you keep it current?"** A GitHub Action re-downloads and redeploys monthly.
- **"Privacy?"** No accounts and no tracking. The basket lives only in the link.
