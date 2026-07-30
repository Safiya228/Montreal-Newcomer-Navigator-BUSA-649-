# Montreal Newcomer Navigator

A Streamlit web app that helps newcomers and students find a Montreal neighborhood
that fits their commute, budget, and lifestyle. Users pick a campus/workplace, set
priority weights (transit, campus proximity, affordability, amenities), and get a
personalized top-5 neighborhood ranking, an interactive map, and a comparison tool.

Built for BUSA 649 — Team SAS.

## How to run it

Requires Python 3.9+.

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app opens automatically at `http://localhost:8501`. Make sure these files stay
in the same folder as `app.py`:

- `Montreal_Newcomer_Navigator_Scored.csv`
- `Neighborhood_Campus_Distances.csv`
- `.streamlit/config.toml` (locks in the dark theme so it displays consistently for
  every user, regardless of their system settings)

## How it works

**1. Data sources**

| Source | Used for | Status |
|---|---|---|
| [STM GTFS Transit Data](https://www.stm.info/en/about/developers/available-data-description) | Transit stops, routes, metro stations, accessibility | Real, downloaded |
| [Montreal Administrative Boundaries](https://donnees.montreal.ca/dataset/limites-administratives-agglomeration-de-montreal) | Neighborhood centroids and areas | Real, downloaded |
| [CMHC Rental Market Survey (2025)](https://www.cmhc-schl.gc.ca/professionals/housing-markets-data-and-research/housing-data/data-tables/rental-market) | Rent and vacancy rate (affordability) | Real, downloaded |
| Campus/workplace coordinates (McGill, Concordia, UQAM, UdeM) | Distance-to-campus scoring | Real, manually compiled |
| [OpenStreetMap via Overpass Turbo](https://overpass-turbo.eu) | Cafes, groceries, libraries, parks, gyms | **Estimated** — see Limitations |

**2. Main steps**

1. Neighborhood boundaries, transit stats, and rent data are compiled into one
   master table (`Montreal_Newcomer_Navigator_Scored.csv`).
2. Distance from every neighborhood centroid to each of the 6 campuses/workplaces
   is calculated with the haversine formula and stored separately
   (`Neighborhood_Campus_Distances.csv`), so the app can look up the right distance
   for whichever campus a user picks — not just the nearest one.
3. Four component scores are calculated per neighborhood (see breakdown below).
4. In the app, a user's slider weights combine these into one personalized score:
   `Personalized Score = Σ(weight × score) / Σ(weights)`, and the top 5
   neighborhoods are shown.

**3. How each score is calculated**

Every component below is first **min-max normalized to 0–100** (the best
neighborhood on that metric = 100, the worst = 0), then combined with the weights
shown. Full code is in `calculate_scores.ipynb`.

- **Transit Score** — stop density (35%) + route density (25%) + metro station
  count (25%) + share of wheelchair-accessible stops (15%)
- **Campus Access Score** — inverse distance to the selected campus (closer = higher)
- **Affordability Score** — inverse average rent, bachelor/1BR/2BR/3BR (70%) +
  vacancy rate (30%) — cheaper rent and higher vacancy both score higher
- **Amenity Score** — density (count ÷ area) of cafes (25%), groceries (25%),
  libraries (20%), parks (15%), gyms (15%)
- **Current Usability Score** (shown on the map as a default, non-personalized
  view) — Affordability (25%) + Campus Access (20%) + Transit (20%) + Amenity (35%),
  weights taken from the project's `Recommendation_Weights` sheet

**4. Assumptions & limitations**

- **Amenity counts (cafes/groceries/libraries/parks/gyms) are modeled estimates**,
  based on neighborhood population and density, not a real OpenStreetMap or
  Montreal Open Data export. The intended real source (Overpass Turbo) blocks
  automated access, so this needs a manual export to be fully accurate.
- **CMHC rent/vacancy data is neighborhood-level** where available, but is still a
  survey-based average, not exact per-building pricing.
- **The map uses neighborhood centroids** (points), not filled boundary shapes,
  since polygon boundaries weren't joined in for this version.
- The in-app chatbot tab uses simple keyword matching, not a language model.

## Files in this repo

```
app.py                                    Streamlit application
calculate_scores.ipynb                    Notebook that computes all 4 scores (full formulas)
requirements.txt                          Python dependencies
Montreal_Newcomer_Navigator_Scored.csv    Main neighborhood dataset + scores
Neighborhood_Campus_Distances.csv         Distance/score lookup per campus
.streamlit/config.toml                    Theme configuration
```
