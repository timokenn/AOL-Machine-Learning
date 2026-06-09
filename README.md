# RecruitAI - Resume Screener

A Streamlit web application for automated resume screening using a Random Forest classifier. The app supports both single-candidate evaluation and bulk CSV analysis, with a dark-themed UI and recruiter-facing feedback.

## Features

**Single Candidate**
Evaluate one candidate at a time by filling in their profile. The app predicts whether the candidate should be shortlisted, displays a shortlist probability, and generates a score breakdown across five dimensions alongside recruiter notes with strengths and areas for improvement.

**Bulk Analysis**
Upload a CSV file containing multiple candidates. The app runs inference on all rows, displays summary KPIs (total, shortlisted, rejected, pass rate), and lets you filter and export results as CSV.

**CSV Guide**
Describes the required input columns, accepted value ranges, and field definitions. Includes a sample CSV download for reference.

## Requirements

Python 3.8 or later is recommended.

Install dependencies:

```
pip install streamlit pandas joblib scikit-learn
```

## Project Structure

```
.
├── app.py
└── models/
    └── random_forest.pkl
```

The trained model must be placed at `models/random_forest.pkl`. The app will show a warning and stop if the file is not found.

## Running the App

```
streamlit run app.py
```

## Input Features

The model expects the following six columns. Two additional features (`exp_x_skills` and `resume_per_proj`) are derived automatically by the app before inference.

| Column | Type | Range | Description |
|---|---|---|---|
| years_experience | integer | 0 – ∞ | Total years in relevant roles |
| skills_match_score | float | 0.0 – 100.0 | Recruiter-assigned alignment score |
| education_level | string | High School / Bachelors / Masters / PhD | Highest qualification |
| project_count | integer | 0 – ∞ | Total completed projects |
| resume_length | integer | 0 – ∞ | Approximate word count of the resume |
| github_activity | integer | 0 – ∞ | Total public GitHub commits |

Extra columns such as `candidate_name` or `email` are allowed in the CSV and will be preserved in the output without affecting predictions.

## Derived Features

| Feature | Formula |
|---|---|
| exp_x_skills | years_experience x skills_match_score |
| resume_per_proj | resume_length / (project_count + 1) |

## Model

The classifier is a Random Forest loaded via `joblib`. It outputs a binary prediction (Shortlisted / Not Shortlisted) and a shortlist probability used for ranking in bulk mode.

## Notes

- Education level strings are ordinally encoded: High School = 0, Bachelors = 1, Masters = 2, PhD = 3.
- The GitHub activity benchmark used in the app is 393 commits, the average among shortlisted candidates in the training dataset (n = 30,000).
- The app uses `st.cache_resource` to load the model once per session.
