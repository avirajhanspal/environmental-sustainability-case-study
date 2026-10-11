# Environmental and Sustainability Specialist - working case study

This is a working **analysis project** for Case Study 4. It contains a runnable Python notebook and command-line script, a three-page report, and a five-slide executive presentation.

## Fastest run (Google Colab)

1. Open https://colab.research.google.com/ and upload `Environmental_Case_Study_Model.ipynb`.
2. Click **Runtime > Run all**. The notebook generates a 2,000-row synthetic demonstration dataset when the real CSV is absent.
3. Read the quality summary and site ledger. The generated CSV outputs are saved in `case_study_outputs/`.
4. Keep the report and deck beside the notebook when submitting.

## Local run

From this folder:

```bash
python3 -m pip install -r requirements.txt
python3 run_analysis.py
```

The script writes `case_study_outputs/quality_review.csv`, `carbon_ledger_demo.csv`, `site_summary_demo.csv`, and `gri_readiness.csv`.

## If the real CSV arrives

Place it in this folder as `Case_Study_4_Environmental_Sustainability.csv`. Check the `ALIASES` mapping in the notebook/script against its real headers. Add approved site/year factors before using any results. The current factors are intentionally illustrative.

## What to say about the limitation

"The assessment package named a 2,000-row CSV, but it was not supplied. I built and tested the full cleaning and accounting pipeline on clearly marked synthetic data. I have not presented those figures as the company's footprint. The report identifies the evidence required to turn the demonstration into an audit-ready inventory."

## Submission files

- `Environmental_Case_Study_Model.ipynb`: runnable calculation model and GRI tracker.
- `Environmental_Case_Study_Report.pdf`: method, ISO gap matrix and action plan.
- `Environmental_Case_Study_Executive_Deck.pptx`: five-slide leadership briefing.
- `run_analysis.py`: simple command-line demonstration.

The complete 15-category Scope 3 inventory and certification status require actual source documents and site evidence. GRI is used as a disclosure checklist, not as a universal performance target.
