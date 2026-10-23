import io
from pathlib import Path
from PIL import Image
import pytest

from receipt_scanner import (
    Receipt, ReceiptItem, items_csv, normalize_image, parse_ocr_text,
    receipt_json, save_exports, summary_csv,
)


def test_parser_synthetic_text():
    text = """REWE\nMuenchen\n12.10.2026 14:23\nBananas 1,49\nMilk 1,19\nBread 2,49\nCheese 3,79\nTOTAL 8,96 EUR\nKartenzahlung 8,96\n"""
    r = parse_ocr_text(text)
    assert r.store == "REWE"
    assert r.date == "2026-10-12"
    assert r.time == "14:23"
    assert r.total == 8.96
    assert r.currency == "EUR"
    assert len(r.items) == 4
    assert r.items[0].price == 1.49


def test_export(tmp_path: Path):
    receipt = Receipt(store="Corner Shop", date="2026-10-12", time="14:23", currency="EUR",
                      total=8.96, items=[ReceiptItem(name="Milk", price=1.19)])
    files = save_exports(receipt, tmp_path)
    assert len(files) == 3
    assert "8.96" in files[0].read_text(encoding="utf-8-sig")
    assert "Milk" in files[1].read_text(encoding="utf-8-sig")
    assert "Corner Shop" in files[2].read_text(encoding="utf-8")
    assert "item_count" in summary_csv(receipt)
    assert "price" in items_csv(receipt)
    assert '"total": 8.96' in receipt_json(receipt)


def test_normalize_image():
    img = Image.new("RGB", (100, 50), "white")
    raw = io.BytesIO()
    img.save(raw, "PNG")
    output = normalize_image(raw.getvalue())
    assert output.startswith(b"\xff\xd8")  # JPEG


def test_reject_invalid_image():
    with pytest.raises(ValueError):
        normalize_image(b"not an image")
    with pytest.raises(ValueError):
        normalize_image(b"")


def test_ai_wiring_without_network(monkeypatch):
    """Verify the API request structure without actually calling OpenAI."""
    import sys
    import types
    from receipt_scanner import Receipt, scan_with_ai

    img = Image.new("RGB", (50, 70), "white")
    buf = io.BytesIO()
    img.save(buf, "PNG")
    monkeypatch.setenv("OPENAI_API_KEY", "fake_key_only_for_test")

    class FakeResponses:
        def parse(self, **kwargs):
            assert kwargs["text_format"] is Receipt
            assert kwargs["store"] is False
            assert kwargs["input"][0]["content"][1]["image_url"].startswith("data:image/jpeg;base64,")
            return types.SimpleNamespace(output_parsed=Receipt(
                store="DEMO", date="2026-10-12", time="14:23", currency="EUR",
                total=3.50, items=[]))

    class FakeClient:
        def __init__(self, **kwargs):
            self.responses = FakeResponses()

    monkeypatch.setitem(sys.modules, "openai", types.SimpleNamespace(OpenAI=FakeClient))
    result = scan_with_ai(buf.getvalue())
    assert result.total == 3.5
