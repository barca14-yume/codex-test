from __future__ import annotations

from pathlib import Path
import csv as _csv

import pytest

from app.sales_cli import (
    InputError,
    _format_output,
    aggregate_by_sku,
    main,
    parse_rows,
    make_parser,
)


def write_csv(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def test_happy_path(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    csv = ",".join(["date", "sku", "amount"]) + "\n" + "\n".join(
        [
            "2024-06-01,AAA,10.0",
            "2024-06-02,BBB,5.5",
            "2024-06-03,AAA,2.5",
            "2024-06-03,CCC,20",
            "2024-06-05,BBB,3",
            "2024-06-06,AAA,7",
        ]
    )
    f = tmp_path / "sales.csv"
    write_csv(f, csv)

    code = main([str(f)])
    assert code == 0
    out = capsys.readouterr().out.strip().splitlines()

    assert out[0] == "TOTAL,48.00"
    assert out[1] == "BY_SKU"
    # Top SKU line (CCC has 20, AAA has 19.5, BBB has 8.5)
    assert out[2] == "CCC,20.00"
    assert out[-1] == "DATE_RANGE,2024-06-01..2024-06-06"


def test_missing_column(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    # Missing 'amount'
    csv = "date,sku\n2024-01-01,AAA"
    f = tmp_path / "sales.csv"
    write_csv(f, csv)

    code = main([str(f)])
    assert code == 2
    err = capsys.readouterr().err
    assert "missing required columns" in err


def test_bad_amount_raises(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    csv = "date,sku,amount\n2024-01-01,AAA,ten"
    f = tmp_path / "sales.csv"
    write_csv(f, csv)

    code = main([str(f)])
    assert code == 2
    err = capsys.readouterr().err
    assert "invalid amount" in err


def test_empty_file_and_only_header(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    # Empty file
    f1 = tmp_path / "empty.csv"
    f1.write_text("", encoding="utf-8")
    code1 = main([str(f1)])
    assert code1 == 0
    out1 = capsys.readouterr().out.strip().splitlines()
    assert out1[0] == "TOTAL,0.00"
    assert out1[1] == "BY_SKU"
    assert out1[-1] == "DATE_RANGE,unknown"

    # Only header
    f2 = tmp_path / "only_header.csv"
    write_csv(f2, "date,sku,amount\n")
    code2 = main([str(f2)])
    assert code2 == 0
    out2 = capsys.readouterr().out.strip().splitlines()
    assert out2[0] == "TOTAL,0.00"
    assert out2[1] == "BY_SKU"
    assert out2[-1] == "DATE_RANGE,unknown"


def test_top_limit(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    csv = ",".join(["date", "sku", "amount"]) + "\n" + "\n".join(
        [
            "2024-06-01,AAA,10.0",
            "2024-06-02,BBB,5.5",
            "2024-06-03,AAA,2.5",
            "2024-06-03,CCC,20",
            "2024-06-05,BBB,3",
            "2024-06-06,AAA,7",
        ]
    )
    f = tmp_path / "sales.csv"
    write_csv(f, csv)

    code = main([str(f), "--top", "2"])
    assert code == 0
    out = capsys.readouterr().out.strip().splitlines()
    # BY_SKU should have exactly 2 entries after header
    assert out[1] == "BY_SKU"
    by_sku_lines = [ln for ln in out[2:] if not ln.startswith("DATE_RANGE") and not ln.startswith("BY_DATE")]
    # Should list CCC, AAA and not BBB
    assert "CCC,20.00" in by_sku_lines
    assert "AAA,19.50" in by_sku_lines
    assert not any(ln.startswith("BBB,") for ln in by_sku_lines)


def test_by_date_section(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    csv = "date,sku,amount\n" + "\n".join(
        [
            "2024-06-01,AAA,10.0",
            "2024-06-02,BBB,5.5",
            "2024-06-03,AAA,2.5",
            "2024-06-03,CCC,20",
            "2024-06-05,BBB,3",
            "2024-06-06,AAA,7",
        ]
    )
    f = tmp_path / "sales.csv"
    write_csv(f, csv)

    code = main([str(f), "--by-date"])
    assert code == 0
    out = capsys.readouterr().out.strip().splitlines()
    assert "BY_DATE" in out

    # Date totals: 2024-06-01:10.00, 2024-06-02:5.50, 2024-06-03:22.50, 2024-06-05:3.00, 2024-06-06:7.00
    assert "2024-06-01,10.00" in out
    assert "2024-06-03,22.50" in out
    assert out.index("2024-06-01,10.00") < out.index("2024-06-03,22.50")


def test_out_csv(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    csv = "date,sku,amount\n" + "\n".join(
        [
            "2024-06-01,AAA,10.0",
            "2024-06-02,BBB,5.5",
            "2024-06-03,AAA,2.5",
            "2024-06-03,CCC,20",
            "2024-06-05,BBB,3",
            "2024-06-06,AAA,7",
        ]
    )
    f = tmp_path / "sales.csv"
    write_csv(f, csv)
    out_csv = tmp_path / "out.csv"

    code = main([str(f), "--top", "2", "--out", str(out_csv)])
    assert code == 0
    assert out_csv.exists()

    # Re-read the output CSV and verify header and two rows
    rows = out_csv.read_text(encoding="utf-8").strip().splitlines()
    assert rows[0] == "sku,amount"
    assert rows[1].startswith("CCC,") and rows[2].startswith("AAA,")
    assert len(rows) == 3


def test_help_uses_sales_cli() -> None:
    parser = make_parser()
    text = parser.format_help()
    assert "usage: sales-cli" in text
