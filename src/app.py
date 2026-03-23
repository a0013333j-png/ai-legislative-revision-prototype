import csv
import json
import os
from pathlib import Path

from openai import OpenAI


def load_input(file_path: Path) -> dict:
    """Load input JSON file."""
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_input(data: dict) -> None:
    """Validate required fields in input JSON."""
    required_fields = ["law_name", "article_no", "original_text", "revision_goal"]

    missing = [field for field in required_fields if field not in data or not str(data[field]).strip()]
    if missing:
        raise ValueError(f"Missing required field(s): {', '.join(missing)}")


def build_prompt(
    law_name: str,
    article_no: str,
    original_text: str,
    revision_goal: str,
    background: list[str],
) -> str:
    """Build prompt for legal revision drafting."""
    background_text = "\n".join([f"- {item}" for item in background]) if background else "- 無"

    return f"""
你是一個法律修法輔助系統。

法規名稱：{law_name}
條號：{article_no}
修法目標：{revision_goal}

背景（不可違反）：
{background_text}

規則：
1. 修改必須符合修法目標
2. 修改不得違反背景，若修法目標與背景衝突，優先遵守背景
3. 理由必須明確反映背景
4. 條文需保持正式、簡潔、法律條文風格
5. 不要加入未被要求的額外制度設計
6. 不要輸出任何說明文字或前言

原始條文：
{original_text}

請嚴格使用以下格式輸出：

修正條文：
（在此填入修改後條文）

理由：
（在此填入簡潔理由）
""".strip()


def call_model(prompt: str) -> str:
    """Call OpenAI model and return the response text."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY is not set.")

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "你是嚴謹、精簡的法律修法輔助模型。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content.strip()


def parse_result(result: str) -> tuple[str, str]:
    """Parse model output into revised_text and reason."""
    revised_text = ""
    reason = ""

    if "修正條文：" in result and "理由：" in result:
        revised_text = result.split("修正條文：", 1)[1].split("理由：", 1)[0].strip()
        reason = result.split("理由：", 1)[1].strip()
    else:
        revised_text = result.strip()
        reason = "模型輸出未符合指定格式，請人工檢查。"

    return revised_text, reason


def ensure_output_dir(output_path: Path) -> None:
    """Ensure output directory exists."""
    output_path.parent.mkdir(parents=True, exist_ok=True)


def write_csv(
    output_path: Path,
    law_name: str,
    article_no: str,
    revision_goal: str,
    background: list[str],
    original_text: str,
    revised_text: str,
    reason: str,
) -> None:
    """Write comparison result to CSV."""
    ensure_output_dir(output_path)

    with output_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "law_name",
                "article_no",
                "revision_goal",
                "background",
                "original_text",
                "revised_text",
                "reason",
            ]
        )
        writer.writerow(
            [
                law_name,
                article_no,
                revision_goal,
                " | ".join(background) if background else "",
                original_text,
                revised_text,
                reason,
            ]
        )


def main() -> None:
    """Main execution flow."""
    input_path = Path("data/input_article.json")
    output_path = Path("output/comparison.csv")

    data = load_input(input_path)
    validate_input(data)

    law_name = data["law_name"].strip()
    article_no = data["article_no"].strip()
    original_text = data["original_text"].strip()
    revision_goal = data["revision_goal"].strip()
    background = data.get("background", [])

    if not isinstance(background, list):
        raise ValueError("Field 'background' must be a list.")

    prompt = build_prompt(
        law_name=law_name,
        article_no=article_no,
        original_text=original_text,
        revision_goal=revision_goal,
        background=background,
    )

    result = call_model(prompt)
    revised_text, reason = parse_result(result)

    write_csv(
        output_path=output_path,
        law_name=law_name,
        article_no=article_no,
        revision_goal=revision_goal,
        background=background,
        original_text=original_text,
        revised_text=revised_text,
        reason=reason,
    )

    print(f"完成：{output_path}")


if __name__ == "__main__":
    main()
