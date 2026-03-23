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
- Automatic law article fetching from Taiwan Laws & Regulations Database by pcode
- Risk note generation for revision output

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
├── output/
│   └── comparison.csv
└── examples/
    └── comparison_example.csv
```

---

## Input Format

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

Run:
```bash
python src/app.py
```

## Output

The script generates:
`output/comparison.csv`

CSV columns:
- law_name
- article_no
- revision_goal
- background
- original_text
- revised_text
- reason
- risk_note

## Notes

- Background is treated as a hard constraint.
- The reason must reflect the background.
- Human review is still required.
