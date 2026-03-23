# AI 修法輔助原型系統（AI Legislative Revision Prototype）

本專案為輕量級 AI 修法輔助原型，用於測試以下流程是否可行：

1. 輸入單一法條
2. 設定修法目標
3. 加入法律背景限制（上位原則）
4. 生成修正條文與理由
5. 輸出對照表（CSV）

---

## 專案定位（Scope）

本系統為原型（Prototype），並非正式法律系統。

不具備以下能力：

- 不驗證法律正確性
- 不確保整體法體系一致性
- 不取代專業法律審查

本專案僅用於驗證：

> 在明確修法目標與法律背景限制下，是否能產生具結構性的條文修正建議。

---

## 功能（Features）

- 單一條文輸入
- 修法目標導向的條文生成
- 背景限制（視為硬性約束）
- 自動生成：
  - 修正條文
  - 修法理由
  - 風險提示（risk note）
- 自動抓取全國法規資料庫條文（透過 pcode）
- 輸出 CSV 對照表

---

## 專案結構（Project Structure）

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

##輸入格式（Input Format）

建立 `data/input_article.json`:
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
說明：
- pcode：全國法規資料庫之法規代碼（用於自動抓取條文）
- background：作為不可違反之法律限制

## 執行方式（How to Run）

安裝套件：
```bash
pip install -r requirements.txt
```

設定 API 金鑰：

- mac / Linux：
```bash
export OPENAI_API_KEY="your_api_key"
```
- Windows（PowerShell）：
```PowerShell
setx OPENAI_API_KEY "你的key"
```

執行：
```bash
python src/app.py
```

## 輸出結果（Output）

程式會產生：
`output/comparison.csv`

欄位包含：
- law_name（法規名稱）
- article_no（條號）
- revision_goal（修法目標）
- background（背景限制）
- original_text（原條文）
- revised_text（修正條文）
- reason（修法理由）
- risk_note（風險提示）

## 設計原則（Design Notes）

- 背景（background）視為不可違反之上位限制
- 若修法目標與背景衝突，優先遵守背景
- 修法理由需反映背景依據
- 風險提示用於揭示潛在制度副作用
- 所有輸出仍需人工審查

## 補充說明

本專案著重於：
- 修法邏輯結構化
- 限制條件下的條文生成
- 法規文本自動擷取與處理

不涉及：
- 法律效力判斷
- 判例分析
- 全法體系推論

