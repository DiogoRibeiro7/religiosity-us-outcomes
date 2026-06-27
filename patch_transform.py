import json
from pathlib import Path

p = Path('notebooks/02_transform_state_panel.ipynb')
nb = json.loads(p.read_text(encoding='utf-8'))

nb['cells'][3]['source'] = '''from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

STATES: dict[str, str] = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri",
    "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
    "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
    "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
}
STATE_TO_ABBR = {state: abbr for abbr, state in STATES.items()}
EXPECTED_STATES = set(STATES.values())
EXPECTED_STATE_ABBRS = set(STATES.keys())

CENSUS_REGION: dict[str, str] = {
    "Connecticut": "Northeast", "Maine": "Northeast", "Massachusetts": "Northeast", "New Hampshire": "Northeast",
    "Rhode Island": "Northeast", "Vermont": "Northeast", "New Jersey": "Northeast", "New York": "Northeast", "Pennsylvania": "Northeast",
    "Illinois": "Midwest", "Indiana": "Midwest", "Michigan": "Midwest", "Ohio": "Midwest", "Wisconsin": "Midwest",
    "Iowa": "Midwest", "Kansas": "Midwest", "Minnesota": "Midwest", "Missouri": "Midwest", "Nebraska": "Midwest", "North Dakota": "Midwest", "South Dakota": "Midwest",
    "Delaware": "South", "Florida": "South", "Georgia": "South", "Maryland": "South", "North Carolina": "South", "South Carolina": "South", "Virginia": "South", "West Virginia": "South",
    "Alabama": "South", "Kentucky": "South", "Mississippi": "South", "Tennessee": "South",
    "Arkansas": "South", "Louisiana": "South", "Oklahoma": "South", "Texas": "South",
    "Arizona": "West", "Colorado": "West", "Idaho": "West", "Montana": "West", "Nevada": "West", "New Mexico": "West", "Utah": "West", "Wyoming": "West",
    "Alaska": "West", "California": "West", "Hawaii": "West", "Oregon": "West", "Washington": "West",
}

assert len(CENSUS_REGION) == 50
print(f"Raw dir: {RAW_DIR}")
print(f"Processed dir: {PROCESSED_DIR}")


def require_raw_file(filename: str) -> pd.DataFrame:
    path = RAW_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing required source file: {path}. Run notebook 01 first.")
    return pd.read_csv(path)


def normalise_state_name(value: Any) -> str | None:
    if pd.isna(value):
        return None
    text = str(value).strip()
    text = re.sub(r"\([^)]*\)", "", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^A-Za-z ]", "", text)
    text = text.strip()
    return text if text in STATE_TO_ABBR else None


def to_float(value: Any) -> float | None:
    if pd.isna(value):
        return None
    text = str(value).replace(",", "").replace("%", "")
    text = re.sub(r"[^0-9.\-]", "", text)
    if text == "":
        return None
    return float(text)


def require_columns(df: pd.DataFrame, columns: list[str], name: str) -> None:
    missing = sorted(set(columns) - set(df.columns))
    if missing:
        raise ValueError(f"{name} missing columns: {missing}. Available columns: {list(df.columns)}")


def require_50_states(df: pd.DataFrame, state_col: str, source: str) -> pd.DataFrame:
    if state_col not in df.columns:
        raise ValueError(f"{source} missing state column '{state_col}'. Columns: {list(df.columns)}")

    out = df.copy()
    raw_states = out[state_col].astype("string")
    full_to_abbr = raw_states.map(STATE_TO_ABBR)
    abbr_guess = raw_states.str.strip().str.upper()
    state_abbr = full_to_abbr.where(~full_to_abbr.isna(), abbr_guess)

    valid = state_abbr.isin(EXPECTED_STATE_ABBRS)
    if (~valid).any():
        dropped = int((~valid).sum())
        print(f"{source}: dropping {dropped} non-state rows from '{state_col}'.")

    out = out.loc[valid].copy()
    out["state_abbr"] = state_abbr.loc[valid]
    out["state"] = out["state_abbr"].map(STATES)

    present_states = set(out["state"].dropna())
    extras = sorted(present_states - EXPECTED_STATES)
    missing = sorted(EXPECTED_STATES - present_states)

    if len(present_states) != 50 or missing or extras:
        raise ValueError(
            f"{source} must contain exactly 50 US states. Found {len(present_states)} after normalisation. "
            f"Missing: {missing}. Unexpected: {extras}."
        )

    if out["state"].duplicated().any():
        dupes = sorted(out.loc[out["state"].duplicated(), "state"].dropna().unique().tolist())
        raise ValueError(f"{source} has duplicated states after normalisation: {dupes}.")

    return out
'''

nb['cells'][5]['source'] = '''religion = pd.read_csv(RAW_DIR / "pew_religious_unaffiliated_by_state.csv")
require_columns(
    religion,
    ["state", "state_abbr", "religiously_unaffiliated_pct", "atheist_pct", "agnostic_pct", "nothing_in_particular_pct"],
    "religion",
)
religion = require_50_states(religion, "state", "religion")
religion = religion[[
    "state", "state_abbr", "atheist_pct", "agnostic_pct", "nothing_in_particular_pct", "religiously_unaffiliated_pct"
]].copy()
religion["religiously_affiliated_pct"] = 100.0 - religion["religiously_unaffiliated_pct"]
religion.head()
'''

nb['cells'][7]['source'] = '''firearm = pd.read_csv(RAW_DIR / "firearm_mortality_by_state_2024.csv")
require_columns(firearm, ["state", "state_abbr", "firearm_death_rate_2024"], "firearm")
firearm = require_50_states(firearm, "state", "firearm")
firearm = firearm[["state", "state_abbr", "firearm_death_rate_2024"]].copy()
firearm.head()
'''

nb['cells'][9]['source'] = '''obesity_raw = require_raw_file("adult_obesity_by_state_2024.csv")
print(obesity_raw.columns.tolist())

state_col_candidates = [c for c in obesity_raw.columns if c.lower() in {"state", "location", "jurisdiction", "geographic area"}]
if not state_col_candidates:
    state_col_candidates = [
        c for c in obesity_raw.columns
        if c.lower().startswith("state") or "state" in c.lower() or "location" in c.lower()
    ]
if not state_col_candidates:
    raise ValueError("Could not infer state column in obesity CSV.")

state_col = state_col_candidates[0]
prevalence_col_candidates = [
    c for c in obesity_raw.columns
    if any(token in c.lower() for token in ["prevalence", "percent", "percentage", "value", "obesity"])
]
if not prevalence_col_candidates:
    prevalence_col_candidates = [
        c for c in obesity_raw.select_dtypes(include="number").columns if "obesity" not in c.lower()
    ]

if not prevalence_col_candidates:
    raise ValueError("Could not infer obesity prevalence column in obesity CSV.")

prevalence_col = prevalence_col_candidates[0]

obesity = obesity_raw[[state_col, prevalence_col]].copy()
obesity.columns = ["state", "adult_obesity_pct_2024"]
obesity["state"] = obesity["state"].map(normalise_state_name)
obesity["adult_obesity_pct_2024"] = obesity["adult_obesity_pct_2024"].map(to_float)
obesity = obesity.dropna(subset=["state", "adult_obesity_pct_2024"])
obesity = require_50_states(obesity, "state", "obesity")
obesity = obesity[["state", "state_abbr", "adult_obesity_pct_2024"]]
obesity.head()
'''

nb['cells'][13]['source'] = '''piaac_raw = require_raw_file("piaac_state_literacy_numeracy.csv")
print(piaac_raw.columns.tolist())

# Infer state column.
state_candidates = [c for c in piaac_raw.columns if c.lower() in {"state", "state_name", "statename", "name"}]
if not state_candidates:
    state_candidates = [c for c in piaac_raw.columns if "state" in c.lower() or "name" in c.lower()]
if not state_candidates:
    raise ValueError("Could not infer PIAAC state column.")
piaac_state_col = state_candidates[0]

# Infer literacy average score and low-literacy share columns.
columns_lower = {c: c.lower() for c in piaac_raw.columns}

avg_lit_candidates = [
    c for c, lc in columns_lower.items()
    if "lit" in lc and ("avg" in lc or "average" in lc or "score" in lc) and "num" not in lc
]
low_lit_candidates = [
    c for c, lc in columns_lower.items()
    if "lit" in lc and ("low" in lc or "below" in lc or "level_1" in lc or "level1" in lc or "le1" in lc)
]

if not avg_lit_candidates:
    avg_lit_candidates = [c for c, lc in columns_lower.items() if lc in {"lit_a", "literacy_avg_score"}]
    if not avg_lit_candidates:
        raise ValueError("Could not infer average literacy score column. Inspect printed PIAAC columns.")

literacy = piaac_raw[[piaac_state_col, avg_lit_candidates[0]] + low_lit_candidates[:1]].copy()
new_cols = ["state", "literacy_avg_score"]
if low_lit_candidates:
    new_cols.append("low_literacy_pct")
literacy.columns = new_cols
literacy["state"] = literacy["state"].map(normalise_state_name)
literacy["literacy_avg_score"] = literacy["literacy_avg_score"].map(to_float)
if "low_literacy_pct" in literacy.columns:
    literacy["low_literacy_pct"] = literacy["low_literacy_pct"].map(to_float)
literacy = literacy.dropna(subset=["state", "literacy_avg_score"])
literacy = require_50_states(literacy, "state", "literacy")
literacy = literacy[["state", "state_abbr", "literacy_avg_score"] + (["low_literacy_pct"] if "low_literacy_pct" in literacy.columns else [])]
literacy.head()
'''

nb['cells'][15]['source'] = '''panel = religion.copy()
assert panel.shape[0] == 50, f"Religion seed must have 50 rows, found {panel.shape[0]}."

for df, name in [
    (firearm, "firearm"),
    (obesity, "obesity"),
    (imprisonment, "imprisonment"),
    (literacy, "literacy"),
]:
    before = panel.shape[0]
    panel = panel.merge(df.drop(columns=["state_abbr"], errors="ignore"), on="state", how="left", validate="one_to_one")
    after = panel.shape[0]
    assert before == after, f"Merge with {name} changed row count."

panel = require_50_states(panel, "state", "panel")
panel["census_region"] = panel["state"].map(CENSUS_REGION)

ordered_columns = [
    "state", "state_abbr", "census_region",
    "religiously_affiliated_pct", "religiously_unaffiliated_pct", "atheist_pct", "agnostic_pct", "nothing_in_particular_pct",
    "firearm_death_rate_2024", "adult_obesity_pct_2024",
    "literacy_avg_score", "low_literacy_pct",
    "imprisonment_rate_2023_all_ages", "imprisonment_rate_2023_adult",
]
ordered_columns = [col for col in ordered_columns if col in panel.columns]
panel = panel[ordered_columns].sort_values("state").reset_index(drop=True)

panel.to_csv(PROCESSED_DIR / "state_religiosity_outcomes.csv", index=False)
panel.head()
'''

p.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding='utf-8')
