"""Command-line receipt scanner: python cli.py example.jpg --mode local"""
import argparse
from pathlib import Path
from receipt_scanner import save_exports, scan_with_ai, scan_with_local_ocr


def main() -> int:
    parser = argparse.ArgumentParser(description="DyogoCodes Python Receipt Scanner")
    parser.add_argument("image", type=Path, help="Path to receipt JPG/PNG")
    parser.add_argument("--mode", choices=["ai", "local"], default="ai", help="Extraction backend (default: ai)")
    parser.add_argument("--out", type=Path, default=Path("output"), help="Directory for CSV/JSON files")
    parser.add_argument("--lang", default="eng", help="Tesseract language for local mode, e.g. eng or deu+eng")
    args = parser.parse_args()
    try:
        if not args.image.is_file():
            raise FileNotFoundError(f"Image not found: {args.image}")
        source = args.image.read_bytes()
        receipt = scan_with_ai(source) if args.mode == "ai" else scan_with_local_ocr(source, args.lang)
        paths = save_exports(receipt, args.out)
    except (ValueError, RuntimeError, OSError) as exc:
        parser.exit(status=1, message=f"Error: {exc}\n")
    print(f"Store: {receipt.store or '?'} | Date: {receipt.date or '?'} | Total: {receipt.total} {receipt.currency or ''}")
    for path in paths:
        print(f"Created: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
