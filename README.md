# AI Legislative Revision Prototype

A lightweight prototype for AI-assisted legislative revision.

This project tests a simple workflow:

1. Input one legal article
2. Set one revision goal
3. Add legal background constraints
4. Generate a revised article and reason
5. Export a comparison table as CSV

## Scope

This is a prototype, not a production legal system.

It does not:
- verify legal correctness
- guarantee consistency with the full legal system
- replace human legal review

It only tests whether a revision goal and background constraints can guide article rewriting in a structured way.

## Features

- Single-article input
- Revision-goal-driven drafting
- Background constraints as hard limits
- AI-generated revised text and reason
- CSV comparison output

## Project Structure

```text
ai-legislative-revision-prototype/
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   └── app.py
├── data/
│   └── input_article.json
└── output/
    └── comparison.csv`

## Input Format

Create `data/input_article.json`:

{
  "law_name": "Test Act",
  "article_no": "Article 3",
  "original_text": "The competent authority may, where necessary, require relevant persons to submit a report.",
  "revision_goal": "Restrict administrative discretion",
  "background": [
    "Administrative power should have clear limits under the principle of proportionality.",
    "Discretion should not be expanded excessively."
  ]
}

## How to Run

Install dependencies:

pip install -r requirements.txt

Set your API key:

export OPENAI_API_KEY="your_api_key"

Run:

python src/app.py

## Output

The script generates:

output/comparison.csv

CSV columns:
- law_name
- article_no
- revision_goal
- background
- original_text
- revised_text
- reason

## Notes

- Background is treated as a hard constraint.
- The reason must reflect the background.
- Human review is still required.
