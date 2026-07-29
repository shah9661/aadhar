
# UIDAI Data Hackathon 2026 — Aadhaar Ecosystem Analytics

**Team ID:** UIDAI_2402

Analyzes Aadhaar enrolment, demographic-update, and biometric-update transaction data (state/district/pincode level, monthly) to understand how mature the Aadhaar ecosystem is across regions, where update pressure is coming from, and where child-inclusion gaps exist. Built as a data pipeline + Power BI dashboard for the UIDAI hackathon.

## What this actually does

Raw UIDAI transaction dumps are messy — inconsistent state/district spellings, duplicates, mojibake characters, districts that got renamed or merged over the years, and a few outright wrong state assignments. Before any analysis is possible, this had to be cleaned up properly. On top of the cleaned data, a set of composite indices is computed to answer three questions per state:

- Is this state still in an **enrolment phase** or has it moved to **maintenance** (i.e. mostly updates, not new enrolments)?
- How **saturated** is biometric re-verification (BSI)?
- How well is the **child population (0–5, 5–17)** being brought into the system (CII)?

These roll up into a single **AIMS (Aadhaar Inclusion-Maturity Score)** per state, plus anomaly and clustering analysis to flag outlier states/districts.

## Repo structure

```
data_cleaning/
├── __init__.py
├── loaders.py       # reads all CSVs from a folder, concats, parses dates
├── text_clean.py    # normalizes state/district text (lowercase, strip punctuation,
│                    # fix mojibake dashes, remove bracketed text, etc.)
├── duplicated.py    # drops exact duplicate rows and rows with critical nulls
├── rules.py         # state_fix_map, district_fix_map, state_district_rules,
│                    # andhra_pradesh_to_telangana, jammu_kashmir_to_ladakh,
│                    # rename_column, keys, counts — all the lookup tables
├── overrides.py     # apply_value_map + apply_state_district_rules
├── fixes.py         # apply_special_fixes (hand-fixed edge cases),
│                    # fix_state_by_district (bulk state reassignment by district list)
├── merge.py         # merge_dataframes — outer-joins enrolment/demo/bio on
│                    # [date, state, district, pincode], fills zeros, downcasts dtypes
├── transform.py     # rename_columns, aggregate (final groupby-sum)
├── pipeline.py       # run_pipeline() — chains everything above in order
└── powerbi_entry.py  # runs the pipeline for enrolment/demographic/biometric
                       # and merges into final_df, used as the entry point for
                       # both the Power BI dataset and the analysis notebook

api_data_aadhar_enrolment/     # raw enrolment CSVs (chunked by pincode range)
api_data_aadhar_demographic/   # raw demographic-update CSVs
api_data_aadhar_biometric/     # raw biometric-update CSVs

analysis.py / notebook         # Plotly/sklearn analysis — indices, PCA, KMeans clustering
dashboard.pbix                 # final Power BI decision-support dashboard
```

## Data cleaning pipeline

Each of the three datasets (enrolment, demographic, biometric) goes through the same pipeline in `pipeline.py`:

1. **Load & concat** all CSVs in the folder, parse `date` (`%d-%m-%Y`).
2. **Drop duplicates & nulls** — this alone removed **591,454** duplicate rows across the raw data.
3. **Normalize text** — lowercase, strip whitespace, fix mojibake dash artifacts (`â€“` type garbage), collapse all dash variants to spaces, strip punctuation, drop bracketed text.
4. **Fix state names** via `state_fix_map` (e.g. `orissa` → `odisha`, `puducherry` → `pondicherry`, typos like `westbengal`, `chhatisgarh`, `uttaranchal`).
5. **Resolve state/district ambiguity** via `state_district_rules` — some rows had a *city name* sitting in the `state` column (e.g. `"raja annamalai puram"`, `"puttenahalli"`, `"jaipur"`) instead of an actual state; these get remapped to their correct state + district.
6. **Fix district names** via `district_fix_map` — this is the bulk of the work: old→new district names (Allahabad→Prayagraj, Bangalore→Bengaluru, Osmanabad→Dharashiv, Gulbarga→Kalaburagi, etc.), spelling variants, and district splits/merges over time.
7. **Hand-fixed special cases** (`apply_special_fixes`) — a handful of rows that don't follow any general rule, e.g. Kamrup incorrectly tagged under Meghalaya instead of Assam, Rupnagar under Chandigarh instead of Punjab.
8. **State reassignment by district** (`fix_state_by_district`) — some districts belong to a state that didn't exist yet at the time of older records: Telangana districts still tagged as Andhra Pradesh, and Kargil/Leh still tagged as Jammu & Kashmir instead of Ladakh.
9. **Rename columns** to the final schema (`enrol_age_0_5` → etc.) and **aggregate** with a final groupby-sum on `[date, state, district, pincode]`.

Net result: **57 raw state labels → 36 official States/UTs**, **932 raw district labels → 804 unique districts**.

The three cleaned datasets are then outer-merged in `merge.py` on `[date, state, district, pincode]`, with count columns zero-filled and numeric columns downcast for memory efficiency — this is `final_df`, the single source of truth for both the Python analysis and the Power BI dashboard.

## Metrics & indices

| Metric | Formula (roughly) | What it tells you |
|---|---|---|
| **Enrolment / Update Ratio** | `Enrolment / (Demographic + Biometric)` | Is a state still adding new people, or mostly maintaining existing records? |
| **Update Intensity** | `(Demographic + Biometric) / Total` | Share of total activity that's maintenance, not new enrolment |
| **BSI (Biometric Saturation Index)** | `bio_17+ / (bio_17+ + demo_17+ + enrol_18+)` | How saturated biometric re-verification is among adults |
| **CII (Child Inclusion Index)** | `(enrol_0_5 + enrol_5_17) / Total` | Share of activity coming from child enrolment |
| **AIMS (composite score)** | `0.4·(1 − update_intensity) + 0.3·(1 − BSI) + 0.3·CII` | Higher = better balance between expansion, maintenance load, and child inclusion |

On top of these: Z-score based outlier detection on the enrolment/update ratio, IQR-based outlier detection on CII, a correlation matrix across the structural metrics, PCA (2 components — PC1 reads as "scale", PC2 as "maturity/inclusion"), and KMeans clustering (4 clusters, labeled Emerging / Stabilizing / Saturated / Outliers based on cluster-centroid thresholds).

## Key findings

- **No enrolment data for August** across states — looks like a reporting gap or operational pause, not an actual activity drop.
- Clear **seasonality**: activity peaks in March, September, November, December; April–June is consistently quieter.
- **Biometric updates dominate** overall activity — the system nationally has shifted from expansion to maintenance mode, driven almost entirely by the 18+ age group.
- **Child enrolment (0–5) stays low nationally (~4–5% of activity)** — a persistent early-age inclusion gap, though districts like West Champaran, East Champaran, Sitamarhi, Bahraich, and South 24 Parganas stand out as high-volume child-enrolment zones worth targeting.
- **Meghalaya** is a clear outlier — youth-skewed enrolment (~48.5% age 5–17 vs the national adult-dominated pattern) and the highest AIMS score, alongside anomalous activity spikes in Assam and Meghalaya during Apr–Sep 2025 that line up with the Immigration & Foreigners Act, 2025 and Aadhaar-restriction actions rather than any population change — both are treated as outliers in national trend analysis so they don't skew averages.
- Activity is heavily **population- and urban-linked**: UP, Maharashtra, and Bihar dominate at the state level; Pune, Thane, and Bengaluru Urban dominate at the district level.
- Andaman & Nicobar has the highest update intensity (98%); Lakshadweep has the highest biometric saturation.

## Dashboard (Power BI)

`dashboard.pbix` — built on `final_df` — includes:
- State/district drill-down map of total Aadhaar activity
- Age-group split (0–5 / 5–17 / 17+) and activity-type split (Enrolment/Demographic/Biometric)
- Month-wise trend lines with a pincode/district-level breakdown table
- Live-computed KPI cards: Update Intensity, Biometric Share, Child Inclusion Index, "Adult Maturity Index"

## Tools & tech

Python (pandas, NumPy) for the pipeline; scikit-learn (StandardScaler, PCA, KMeans) and Plotly for the analysis and visualizations; Power BI + DAX for the dashboard; Jupyter/Colab for the exploratory notebook.

## Running it

```bash
# from repo root
python -c "from data_cleaning.powerbi_entry import final_df; print(final_df.shape)"
```

`final_df` is what feeds both `dashboard.pbix` (via CSV/direct query export) and the analysis notebook.

<img width="1358" height="594" alt="image" src="https://github.com/user-attachments/assets/5a804693-1374-47bd-8038-0a3bb37c3766" />
<img width="1327" height="590" alt="image" src="https://github.com/user-attachments/assets/ce24d702-1c82-4ab0-92e3-ec41c70edcf1" />

## Team

Team ID: **UIDAI_2402** — UIDAI Data Hackathon 2026
