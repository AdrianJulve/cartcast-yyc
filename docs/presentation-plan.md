# Presentation plan: DATA 398.1, Part 1 (10 minutes, in class)

## Scenario and audience

State these before the presentation starts.

- Scenario: a funding pitch to a community innovation fund, such as a municipal or foundation grant for food security projects.
- Audience: funders and community food security partners, such as food banks and family support agencies. They are not assumed to have a technical background.
- Request: seed funding and one partner agency to pilot CartCast YYC for six months.
- Topic type: a proposed solution to a real-world problem (rising grocery costs).

## Engagement tool: live demonstration

The class builds a basket during the presentation. One presenter asks the room for
three or four items people buy every week and adds them on the dashboard, while the
audience watches the weekly cost, price changes and substitutions update. The demo
ends by applying a substitution and showing the saving. A QR code linking to the
shared basket can be added to a slide so people can follow along on their phones.

## Schedule

Adjust names and segment lengths for the size of the team.

| Time | Presenter | Segment | Content |
|---|---|---|---|
| 0:00 to 0:45 | Presenter 1 | Scenario and opening | State the scenario and audience. Ask how many people have noticed their grocery bill going up this year. |
| 0:45 to 2:15 | Presenter 1 | The problem | Food Price Report 2026: food prices forecast to rise 4 to 6 percent in 2026; a family of four spending about $17,572 a year; prices up 27 percent in five years; Alberta above the national average. Record demand at the Calgary Food Bank, including from working households. |
| 2:15 to 3:30 | Presenter 2 | The solution and the data | What CartCast does, in one sentence. The five data sources, and which ones are Calgary-specific. The pipeline diagram from the README. Why average prices and the CPI are used for different things. |
| 3:30 to 7:00 | Presenters 3 and 2 | Live demo | Change the household to Couple. Add items suggested by the audience. Read out the largest price changes. Apply a substitution and point to the savings figure. Show the basket against the Calgary food benchmark. Filter the store map by community. Copy the share link. |
| 7:00 to 8:30 | Presenter 4 | Impact and next steps | Who would use it (households and agency caseworkers). Pilot measures: weekly users, substitutions applied, estimated savings per household. Costs: free hosting and about two hours of maintenance a month. |
| 8:30 to 9:15 | Presenter 4 | The request | Seed funding, one partner agency, and feedback on the default basket. |
| 9:15 to 10:00 | All | Closing and questions | Restate what the tool does and who it is for. |

## Slides

1. Title, scenario and audience
2. The problem, in three figures
3. Who is affected (food bank demand)
4. The dashboard (`design/cartcast_mockup.png`)
5. Data sources, licences and the method note
6. Live demo (title slide only)
7. Pilot plan, measures and costs
8. The request and thank you

## Demo preparation

- [ ] Run `python -m cartcast fetch` and `python -m cartcast build` the night before so the demo uses the latest real data. Commit the updated `data/snapshot/`.
- [ ] Copy a sample build of `site/index.html` to a USB drive as a fallback that works offline.
- [ ] Set the browser zoom to 110 to 125 percent for the projector and close other tabs.
- [ ] Rehearse the sequence: change to Couple, add "Avocado, unit", apply the top substitution, filter the map.
- [ ] Put screenshots of each demo step in hidden slides in case the laptop or projector fails.
- [ ] Have one person operate the laptop while another narrates.

## Likely questions

- Why Alberta prices and not Calgary prices? StatCan publishes average prices by province only. The inflation figure uses the Calgary CMA CPI, and the food benchmark uses the Calgary Market Basket Measure.
- What is the food benchmark? The food cost in the Market Basket Measure, Canada's official poverty line, for Calgary. It is the cost of a nutritious diet, adjusted for household size.
- Can average prices be used to show change over time? StatCan advises against it, so the inflation figure on the dashboard comes from the CPI.
- How is the data kept current? A GitHub Actions workflow downloads the data and redeploys the site every month.
- Is any personal data collected? No. There are no accounts or tracking, and the basket is stored only in the link.
