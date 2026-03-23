# AI Legislative Revision Prototype

A lightweight prototype for AI-assisted legislative revision.
This project explores a structured workflow for revising legal articles under explicit goals and constraints.
---

## Overview

The system supports a simple but structured process:

1. Input legal article(s)
2. Define a revision goal
3. Provide legal background constraints
4. Generate:
   - Revised article
   - Reason for revision
   - Risk note
5. Export results as a comparison CSV

---

## Scope

This is a **prototype**, not a production legal system.

It does NOT:

- verify legal correctness  
- guarantee consistency across the full legal system  
- replace professional legal review  

It focuses on testing whether:

> A revision goal + explicit constraints can guide structured legal rewriting.

---

## Features

- Single-article processing (`app.py`)
- Multi-article input support (`multi_app.py`)
- Goal-driven revision drafting
- Background constraints as hard limits
- Structured output:
  - revised text
  - reason
  - risk note
- CSV comparison output
- Automatic law article fetching from Taiwan Laws & Regulations Database (via `pcode`)

---

## Project Structure

```text
ai-legislative-revision-prototype/
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   ├── app.py              # single-article mode
│   └── multi_app.py        # multi-article mode
├── data/
│   ├── input_article.json
│   └── input_articles.json
├── output/
│   └── comparison.csv
└── examples/
    └── comparison_example.csv
```

---

## Input Format

# Single Article
Create `data/input_article.json`:
```
{
  "law_name": "少年事件處理法",
  "pcode": "C0010011",
  "article_no": "第3條",
  "revision_goal": "限縮權限",
  "background": [
    "依憲法比例原則，行政權限應有明確界限",
    "不得過度擴張行政裁量"
  ]
}
```

# Multi-Article
Create `data/input_articles.json`:
```
{
  "law_name": "少年事件處理法",
  "pcode": "C0010011",
  "revision_goal": "限縮權限",
  "background": [
    "依憲法比例原則，行政權限應有明確界限",
    "不得過度擴張行政裁量"
  ],
  "articles": [
    { "article_no": "第3條" },
    { "article_no": "第3-1條" }
  ]
}
```


## How to Run

Install dependencies:
```bash
pip install -r requirements.txt
```

Set your API key:

- mac / Linux：
```bash
export OPENAI_API_KEY="your_api_key"
```
- Windows（PowerShell）：
```PowerShell
setx OPENAI_API_KEY "你的key"
```

Run Single Article
```bash
python src/app.py
```

Run Multi Article
```bash
python src/multi_app.py
```


## Output

Generated files:
`output/comparison.csv
output/comparison_multi.csv`

CSV columns:
- law_name
- article_no
- revision_goal
- background
- original_text
- revised_text
- reason
- risk_note

## Design Notes

- Background is treated as a hard constraint
- If conflict occurs, background takes priority over revision goal
- Reason must reflect the applied constraints
- Risk note highlights potential side effects of the revision
- Human review is required for all outputs

## Notes

This project focuses on:
- structured legal text transformation
- constraint-based drafting logic
- integration with external legal data sources

It does not attempt:
- full legal reasoning
- precedent analysis
- system-wide legal validation
