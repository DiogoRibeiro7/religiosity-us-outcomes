# U.S. Religiosity and Social Outcomes

This is a small data science project to test the state-level claim:

> More religious U.S. states have higher rates of gun violence, illiteracy, obesity, and incarceration.

The project is deliberately written as notebooks, not as a package. It extracts public data, transforms it into a clean state-level analytical table, and runs exploratory and statistical analysis.

The main point is **association**, not causation. The notebooks can show whether the claim is supported by state-level correlations. They do not prove that religion itself causes the outcomes.

## Notebooks

Run the notebooks in this order:

1. `notebooks/01_extract_public_data.ipynb`
   - Downloads or scrapes the raw data.
   - Saves files under `data/raw/`.
   - Sources:
     - Pew Research Center Religious Landscape Study state pages.
     - Pew Research Center analysis of CDC WONDER firearm mortality data.
     - CDC adult obesity BRFSS CSV.
     - Bureau of Justice Statistics `Prisoners in 2023` PDF.
     - NCES / PIAAC Skills Map through ArcGIS Open Data (literacy/numeracy **and** the socioeconomic covariates).
     - CDC *Mapping Injury, Overdose, and Violence* (Socrata `fpsi-y8tj`) for firearm deaths split by intent and a gun-ownership proxy.
     - Census county Gazetteer for state land area (used to build a population-density / urbanicity control).

2. `notebooks/02_transform_state_panel.ipynb`
   - Cleans the raw files.
   - Standardises state names and abbreviations.
   - Builds one row per state.
   - Saves `data/processed/state_religiosity_outcomes.csv`.

3. `notebooks/03_analyse_religiosity_outcomes.ipynb`
   - **Part 1 (descriptive):** missingness checks, Pearson/Spearman correlations, scatter plots, simple OLS, and region-adjusted OLS.
   - **Part 2 (deeper analysis):** distributions, a full correlation heatmap, regional boxplots, region-coloured scatters, religiosity-vs-confounder checks, **covariate-adjusted regressions**, a model-comparison forest plot, partial correlations, multiple-comparison (FDR) control, bootstrap CIs, influence diagnostics, the **firearm homicide-vs-suicide** split with a gun-ownership analysis, and a **hierarchical (MixedLM) model by region**.
   - Exports tables and plots to `reports/`.

## How religiosity is measured

The default measure is:

```text
religiously_affiliated_pct = 100 - religiously_unaffiliated_pct
```

The unaffiliated share is extracted from Pew state pages by summing:

```text
Atheist + Agnostic + Nothing in particular
```

This is a practical, current, state-level proxy for religious affiliation. It is not exactly the same as Pew's older "highly religious" index, which combined belief, prayer, attendance, and importance of religion.

The analysis notebook is written so that you can swap in another religiosity measure later.

## Outcomes

The current analytical table uses:

- Firearm mortality rate per 100,000 people, age-adjusted, 2024 — plus the **firearm homicide** and **firearm suicide** rates separately (CDC, 2024).
- Adult obesity prevalence, 2024.
- Literacy and **numeracy** average scores from PIAAC/NCES.
- Imprisonment rate per 100,000 residents, 2023.

## Covariates (confounders)

The analytical table also carries candidate confounders, used by the Part 2 models in notebook 03:

- Poverty rate, share with less than a high-school education, unemployment, uninsured share, SNAP receipt, % Black, % Hispanic (PIAAC/NCES).
- A household **gun-ownership proxy** (FS/S = firearm suicides ÷ all suicides; CDC).
- **Population density** (state population ÷ Census land area) as an urbanicity proxy.

These let the analysis test whether religiosity predicts the outcomes *independently* of socioeconomics — not just whether it correlates with them.

## Setup

Create a clean environment and install:

```bash
python -m venv .venv
source .venv/bin/activate
pip install pandas numpy requests beautifulsoup4 lxml matplotlib scipy statsmodels tqdm pdfplumber nbformat
```

On Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install pandas numpy requests beautifulsoup4 lxml matplotlib scipy statsmodels tqdm pdfplumber nbformat
```

## Project structure after running

```text
.
├── README.md
├── notebooks
│   ├── 01_extract_public_data.ipynb
│   ├── 02_transform_state_panel.ipynb
│   └── 03_analyse_religiosity_outcomes.ipynb
├── data
│   ├── raw
│   └── processed
└── reports
    ├── figures
    └── tables
```

## Interpretation guide

The analysis should be read carefully:

- A positive correlation between religiosity and firearm mortality means more religious states tend to have higher firearm mortality.
- A negative correlation between religiosity and literacy score means more religious states tend to have lower average literacy scores.
- These are ecological state-level relationships. They do not imply that religious individuals are more violent, less literate, more obese, or more likely to be incarcerated.
- State-level religiosity is correlated with region, rurality, poverty, education, race, policy, public health access, and historical inequality. Those variables matter.

**What the Part 2 analysis found:** the bivariate associations are all real and statistically robust *as descriptions of states*, but they are largely **confounded**. Adjusting for Census region removes the firearm, obesity, and imprisonment associations; adjusting further for socioeconomic covariates (poverty, education, race composition, density) removes essentially everything else — including literacy and numeracy, which had survived the region-only adjustment. The "gun violence" signal is specifically firearm **homicide** (not suicide), and even that is fully explained by socioeconomics rather than by gun ownership. Obesity is the only outcome that retains a modest, fragile association after adjustment. See the conclusion in notebook 03 for details.

## Suggested extensions (status)

Done in this version:

- ✅ Controls for poverty, education, race/ethnicity, unemployment, insurance, and urbanisation (population density).
- ✅ Firearm homicide separated from firearm suicide.
- ✅ A household gun-ownership proxy (FS/S ratio).
- ✅ A hierarchical (random-intercept by region) model via `statsmodels` MixedLM.

Still open (need extra data or libraries):

- Add median household income and median age (Census ACS — needs a free API key).
- Compare religious affiliation with a religious **practice-intensity** measure (parse the Pew state-page practice charts).
- Full **Bayesian** hierarchical model by region (`PyMC`, not currently installed).
- **County-level** analysis (needs a county religiosity source such as the ARDA / U.S. Religion Census).
- Robustness checks across multiple religiosity measures.


