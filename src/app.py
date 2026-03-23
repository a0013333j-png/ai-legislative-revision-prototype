import csv
import json
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from pathlib import Path

from openai import OpenAI


def load_input(file_path: Path) -> dict:
    """Load input JSON file."""
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)

import requests
from bs4 import BeautifulSoup


def fetch_law_article(pcode: str, article_no: str) -> str:
    import re
    import requests
    from bs4 import BeautifulSoup

    law_url = f"https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode={pcode}"

    res = requests.get(law_url, verify=False)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")
    full_text = soup.get_text("\n", strip=True)

    # 找所有條號位置，例如：
    # 第 3 條、第 3-1 條、第 4 條
    article_pattern = r"第\s*\d+(?:-\d+)?\s*條"
    matches = list(re.finditer(article_pattern, full_text))

    if not matches:
        raise ValueError("頁面中找不到任何條文格式")

    # 把輸入條號標準化，例如「第3條」→「第 3 條」也能比對
    target_match = re.search(r"第\s*(\d+(?:-\d+)?)\s*條", article_no)
    if not target_match:
        raise ValueError(f"條號格式錯誤：{article_no}")

    target_no = target_match.group(1)

    for i, match in enumerate(matches):
        found_text = match.group(0)
        found_no_match = re.search(r"第\s*(\d+(?:-\d+)?)\s*條", found_text)
        if not found_no_match:
            continue

        found_no = found_no_match.group(1)

        if found_no == target_no:
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)
            article_text = full_text[start:end].strip()
            article_text = re.sub(r"\n+", "\n", article_text)
            return article_text

    raise ValueError(f"找不到條文：{article_no}")

    article_text = article_match.group(1)

    # 清理多餘空白
    article_text = re.sub(r"\n+", "\n", article_text).strip()

    return article_text

def validate_input(data: dict) -> None:
    """Validate required fields in input JSON."""
    required_fields = ["article_no", "revision_goal"]

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


def generate_risk_note(revision_goal: str, original_text: str, revised_text: str) -> str:
    """Generate a simple risk note based on revision goal and text changes."""
    notes = []

    if revision_goal == "限縮權限":
        notes.append("可能影響行政機關執行彈性，需確認是否過度限縮裁量。")
    elif revision_goal == "強化程序":
        notes.append("新增程序要求可能增加行政成本與處理時間。")
    elif revision_goal == "補漏洞":
        notes.append("新增規範可能與其他條文產生競合，需再比對體系一致性。")
    elif revision_goal == "統一用語":
        notes.append("用語調整需確認是否改變原有法律效果。")

    if "應" in revised_text and "得" in original_text:
        notes.append("裁量空間可能縮小，需確認是否符合立法目的。")

    if not notes:
        notes.append("需人工確認修正內容是否與上位法及相關條文一致。")

    return " ".join(notes)


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
    risk_note: str,
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
                "risk_note",
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
                risk_note,
            ]
        )


def main() -> None:
    """Main execution flow."""
    input_path = Path("data/input_article.json")
    output_path = Path("output/comparison.csv")

    data = load_input(input_path)
    validate_input(data)

    law_name = data.get("law_name", "").strip()
    pcode = data.get("pcode", "").strip()
    article_no = data["article_no"].strip()
    original_text = data.get("original_text", "").strip()

    if not original_text:
        if not pcode:
            raise ValueError("缺少 pcode，無法自動抓法條。")
        original_text = fetch_law_article(pcode, article_no)
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

    # 目前使用固定結果，先驗證流程；之後有 API 或本地模型再改回 call_model(prompt)
    result = """修正條文：
主管機關於有具體必要時，始得命相關人員提出報告。

理由：
為符合比例原則，避免行政裁量過度，爰增列具體條件，以限縮行政機關之裁量範圍。"""

    revised_text, reason = parse_result(result)
    risk_note = generate_risk_note(revision_goal, original_text, revised_text)

    write_csv(
        output_path=output_path,
        law_name=law_name,
        article_no=article_no,
        revision_goal=revision_goal,
        background=background,
        original_text=original_text,
        revised_text=revised_text,
        reason=reason,
        risk_note=risk_note,
    )

    print(f"完成：{output_path}")


if __name__ == "__main__":
    main()