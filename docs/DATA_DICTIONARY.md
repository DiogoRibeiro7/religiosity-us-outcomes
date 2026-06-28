# Data dictionary

The analytical panel — [`data/processed/state_religiosity_outcomes.csv`](../data/processed/state_religiosity_outcomes.csv) — is **one row per U.S. state (50 rows)**. Built by `notebooks/02_transform_state_panel.ipynb` from the raw snapshots in [`data/raw/`](../data/raw/).

Ranges below are the observed min–max across the 50 states.

## Identifiers

| Column | Type | Description |
|---|---|---|
| `state` | text | Full state name |
| `state_abbr` | text | Two-letter postal abbreviation |
| `census_region` | text | Census region: `Northeast`, `Midwest`, `South`, `West` |

## Religiosity (predictor)

Source: **Pew Research Center** Religious Landscape Study state pages (2023–24). The headline measure is current religious affiliation.

| Column | Units | Range | Description |
|---|---|---|---|
| `religiously_affiliated_pct` | % of adults | 52–85 | `100 − religiously_unaffiliated_pct`; the project's default predictor (higher = more religious) |
| `religiously_unaffiliated_pct` | % of adults | 15–48 | `atheist + agnostic + nothing in particular` |
| `atheist_pct` | % of adults | 1–11 | Self-identified atheist |
| `agnostic_pct` | % of adults | 1–12 | Self-identified agnostic |
| `nothing_in_particular_pct` | % of adults | 9–29 | "Nothing in particular" |

## Outcomes

| Column | Units | Range | Source / year | Notes |
|---|---|---|---|---|
| `firearm_death_rate_2024` | per 100,000 | 3.7–28 | Pew analysis of CDC WONDER, 2024 | Age-adjusted, all intents |
| `firearm_homicide_rate_2024` | per 100,000 | 0.8–16 | CDC *Mapping Injury, Overdose, and Violence* (`fpsi-y8tj`), 2024 | Firearm homicide only |
| `firearm_suicide_rate_2024` | per 100,000 | 2.2–21.1 | CDC `fpsi-y8tj`, 2024 | Firearm suicide only |
| `adult_obesity_pct_2024` | % of adults | 25–41.4 | CDC BRFSS, 2024 | **1 missing** (Tennessee: "Insufficient data") |
| `literacy_avg_score` | PIAAC scale (~0–500) | 251.5–278.9 | NCES / PIAAC | Average adult literacy proficiency |
| `numeracy_avg_score` | PIAAC scale (~0–500) | 233.3–268 | NCES / PIAAC | Average adult numeracy proficiency |
| `imprisonment_rate_2023_all_ages` | per 100,000 residents | 96–652 | BJS *Prisoners in 2023* | Headline incarceration outcome |
| `imprisonment_rate_2023_adult` | per 100,000 adults | 118–847 | BJS *Prisoners in 2023* | Robustness alternative |

## Covariates (confounders)

| Column | Units | Range | Source | Description |
|---|---|---|---|---|
| `poverty_pct` | % | 8.1–21.5 | PIAAC/NCES | Share below 100% of the poverty line |
| `less_than_hs_pct` | % | 7–17.5 | PIAAC/NCES | Adults with less than a high-school education |
| `unemployment_pct` | % | 2.2–6.1 | PIAAC/NCES | Unemployment share |
| `uninsured_pct` | % | 3–18.2 | PIAAC/NCES | Share without health insurance |
| `snap_pct` | % | 5.8–17.8 | PIAAC/NCES | Share receiving SNAP benefits |
| `pct_black` | % | 0.4–37.6 | PIAAC/NCES | Share Black |
| `pct_hispanic` | % | 1.5–48.2 | PIAAC/NCES | Share Hispanic |
| `gun_ownership_pct_proxy` | % | 15.5–74.3 | CDC `fpsi-y8tj` | FS/S proxy = firearm suicides ÷ all suicides, ×100 |
| `population_density` | people / sq mi | 1.3–1218 | PIAAC pop. ÷ Census land area | Urbanicity proxy |
| `median_household_income` | USD | 54,200–99,860 | Census ACS 1-year 2023 | `B19013_001E` |
| `median_age` | years | 32.3–44.9 | Census ACS 1-year 2023 | `B01002_001E` |

## Notes

- All percentages are state-level shares of the relevant population.
- The `gun_ownership_pct_proxy` is mechanically related to `firearm_suicide_rate_2024` (both built from firearm suicides); the analysis uses it as a control only with the firearm **homicide** outcome.
- Exact source URLs and extraction logic are in `notebooks/01_extract_public_data.ipynb`.
