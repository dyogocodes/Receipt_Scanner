# 🧾 Python Receipt Scanner, by DyogoCodes

**Turn a receipt photo into structured data using Python!**

Upload an image or take a picture, extract **store, date, time, items and total**, then export **CSV** and **JSON**. Includes a Streamlit web app and command-line version.

## Features

- 📷 Camera capture / JPG and PNG uploads
- 🤖 **AI Vision**, best for real-life photographs and mixed receipt layouts
- 🆓 **Free local OCR**, using Tesseract without an OpenAI account (less accurate)
- 🧾 Extract store, date, time, currency, purchased items and final total
- 📁 Exports `receipt_summary.csv`, `receipt_items.csv` and `receipt.json`
- 🛡️ EXIF metadata removed before sending AI images; API key kept in `.env`

## 1. Install Python and dependencies

Requires **Python 3.10+**. Run from the project folder:

```bash
python -m venv .venv
```

Activate it:

- **Windows PowerShell:** `.venv\Scripts\Activate.ps1`
- **macOS/Linux:** `source .venv/bin/activate`

Install packages:

```bash
python -m pip install -r requirements.txt
```

On Windows, if `python` does not work, try `py`.

## 2. Choose how to scan

### Option A: AI Vision (recommended)

1. Get an OpenAI API key at https://platform.openai.com/api-keys (API billing may be required).
2. Copy `.env.example` to `.env` in the project folder.
3. Edit `.env` and replace `your_openai_api_key_here` with your actual key.
4. AI uses `gpt-4.1-mini` by default, or set `OPENAI_MODEL` to another vision-capable model.

**Important:** A ChatGPT subscription does not include OpenAI API credits. Each AI scan may cost money. Receipt images are uploaded to the API in this mode. Do not share images containing sensitive card details or personal information unless you are comfortable sending them to the API.

### Option B: Free local OCR (no API key required)

Tesseract is **another program** you install on your computer. Installing `pytesseract` alone is not enough.

- **Windows:** Install the Tesseract OCR Windows program, then add its install directory to `PATH`.
- **macOS:** `brew install tesseract`
- **Ubuntu/Debian:** `sudo apt update && sudo apt install tesseract-ocr`
- For better German OCR: install German language data (`tesseract-lang` with Homebrew, or `tesseract-ocr-deu` on Ubuntu), then run the CLI with `--lang deu+eng`.

Verify in a new terminal:

```bash
tesseract --version
```

**Local OCR limitation:** Receipts vary in format and lighting. This rule-based offline parser is a starter project, and may miss or misinterpret fields. Review the data before using it.

## 3. Run the visual web app

```bash
streamlit run app.py
```

Select **AI Vision** or **Free local OCR**, upload or photograph a receipt, hit **Scan receipt**, and download the results. Streamlit should open a browser window automatically.

## 4. Run from terminal

```bash
# AI-powered scanning
python cli.py examples/sample_receipt.png --mode ai --out output

# Free local OCR
python cli.py examples/sample_receipt.png --mode local --out output

# German + English OCR, if both language packs are installed
python cli.py examples/sample_receipt.png --mode local --lang deu+eng
```

## Output examples

`receipt_summary.csv`:

```csv
store,date,time,currency,total,item_count
REWE,2026-10-12,14:23,EUR,8.96,4
```

`receipt_items.csv`:

```csv
store,date,item,price,currency
REWE,2026-10-12,Bananas,1.49,EUR
REWE,2026-10-12,Milk,1.19,EUR
REWE,2026-10-12,Bread,2.49,EUR
REWE,2026-10-12,Cheese,3.79,EUR
```

Results depend on the receipt's legibility and chosen extraction backend.

## Troubleshooting

| Problem | Solution |
|---|---|
| `OPENAI_API_KEY is missing` | Select local mode, or set your API key in `.env` |
| `Tesseract is not installed` | Install the Tesseract executable, make sure `tesseract --version` works |
| `eng.traineddata` / `deu.traineddata` missing | Install Tesseract language data or use `--lang eng` |
| Results are wrong | Crop / flatten the receipt, improve lighting, or use AI Vision |
| API 401, 429 or unavailable | Check your key, credits, permissions and rate limits |
| Export opens strangely in Excel | Import as UTF-8 CSV; CSV uses decimal dots and comma separators |

## Project structure

```text
DyogoCodes_Receipt_Scanner/
├── app.py                  # Streamlit GUI
├── cli.py                  # Command-line entry point
├── receipt_scanner.py      # AI, OCR, parsing and exporting
├── examples/sample_receipt.png
├── requirements.txt
├── .env.example
├── .gitignore
└── tests/test_receipt_scanner.py
```

## Run tests

```bash
python -m pytest -q
```

## Sharing

Made for educational purposes by **DyogoCodes**. Feel free to learn from, adapt and credit the project. Follow DyogoCodes for more fun Python builds.

> Safety: Check extraction results before accounting or reimbursement. This educational example is not a certified invoice recognition system.