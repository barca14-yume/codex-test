"""Sales aggregation CLI.

Usage:
    python -m src.app.sales_cli <csv_path> [--top N] [--by-date] [--out PATH]

Required CSV columns: ``date`` (YYYY-MM-DD), ``sku`` (non-empty), ``amount`` (float).
Output format:
    TOTAL,<sum to two decimals>
    BY_SKU
    <SKU>,<amount to two decimals>
    [BY_DATE\nYYYY-MM-DD,<amount> ...]
    DATE_RANGE,<min(date)>..<max(date)>  (or ``unknown`` if no data)
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable, List, Tuple


@dataclass(frozen=True)
class Row:
    dt: date
    sku: str
    amount: float


class InputError(Exception):
    """Raised for invalid CLI input (file/columns/row values)."""


REQUIRED_COLUMNS = {"date", "sku", "amount"}


def parse_rows(csv_path: Path) -> List[Row]:
    """Parse and validate rows from a CSV file.

    - If the file is empty (0 bytes), return an empty list (treated as no data).
    - Validate required columns when a header is present.
    - Validate date format (YYYY-MM-DD), non-empty sku, and numeric amount.
    """

    if not csv_path.exists():
        raise InputError(f"file not found: {csv_path}")

    if csv_path.stat().st_size == 0:
        return []

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            # No header present but file not empty: treat as invalid shape
            raise InputError("missing header row with required columns: date, sku, amount")

        header = {h.strip() for h in reader.fieldnames if h is not None}
        missing = REQUIRED_COLUMNS - header
        if missing:
            raise InputError(
                "missing required columns: " + ", ".join(sorted(missing))
            )

        rows: List[Row] = []
        for i, raw in enumerate(reader, start=2):  # header is line 1
            try:
                dt_str = (raw.get("date") or "").strip()
                sku = (raw.get("sku") or "").strip()
                amt_str = (raw.get("amount") or "").strip()

                if not sku:
                    raise InputError(f"line {i}: sku must be non-empty")

                try:
                    dt = date.fromisoformat(dt_str)
                except Exception as exc:  # noqa: BLE001
                    raise InputError(f"line {i}: invalid date '{dt_str}' (YYYY-MM-DD)") from exc

                try:
                    amt = float(amt_str)
                except Exception as exc:  # noqa: BLE001
                    raise InputError(f"line {i}: invalid amount '{amt_str}'") from exc

                rows.append(Row(dt=dt, sku=sku, amount=amt))
            except InputError:
                # Re-raise to terminate on first invalid data row.
                raise
        return rows


def aggregate_by_sku(rows: Iterable[Row]) -> List[Tuple[str, float]]:
    """Aggregate amounts by SKU and return sorted list.

    Sort by amount desc, then sku asc.
    """

    totals: dict[str, float] = {}
    for r in rows:
        totals[r.sku] = totals.get(r.sku, 0.0) + r.amount

    sorted_items = sorted(
        totals.items(), key=lambda kv: (-kv[1], kv[0])
    )
    return sorted_items


def aggregate_by_date(rows: Iterable[Row]) -> List[Tuple[date, float]]:
    """Aggregate amounts by date and return sorted list ascending by date."""

    totals: dict[date, float] = {}
    for r in rows:
        totals[r.dt] = totals.get(r.dt, 0.0) + r.amount
    return sorted(totals.items(), key=lambda kv: kv[0])


def _format_output(rows: List[Row], *, top: int | None = None, by_date: bool = False) -> str:
    total = sum(r.amount for r in rows)
    lines: List[str] = [f"TOTAL,{total:.2f}", "BY_SKU"]

    by_sku = aggregate_by_sku(rows)
    if top is not None and top >= 0:
        by_sku = by_sku[:top]

    for sku, amt in by_sku:
        lines.append(f"{sku},{amt:.2f}")

    if by_date:
        lines.append("BY_DATE")
        for dt, amt in aggregate_by_date(rows):
            lines.append(f"{dt.isoformat()},{amt:.2f}")

    if rows:
        dts = [r.dt for r in rows]
        drange = f"{min(dts).isoformat()}..{max(dts).isoformat()}"
    else:
        drange = "unknown"
    lines.append(f"DATE_RANGE,{drange}")
    return "\n".join(lines)


def main(argv: List[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    parser = argparse.ArgumentParser(
        prog="python -m src.app.sales_cli",
        add_help=True,
        description="Aggregate sales totals from a CSV file.",
    )
    parser.add_argument("csv_path", help="Path to CSV file with date,sku,amount columns")
    parser.add_argument("--top", type=int, default=None, help="Limit number of SKUs shown")
    parser.add_argument(
        "--by-date",
        action="store_true",
        help="Include BY_DATE section with totals per date",
    )
    parser.add_argument(
        "--out",
        type=str,
        default=None,
        help="Write BY_SKU table to CSV path (headers: sku,amount)",
    )

    try:
        ns = parser.parse_args(args)
    except SystemExit as exc:
        # argparse will print its own error message; respect non-zero code.
        return exc.code if isinstance(exc.code, int) else 2

    csv_path = Path(ns.csv_path)
    try:
        rows = parse_rows(csv_path)
    except InputError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    # Prepare BY_SKU aggregation (for printing and optional export).
    by_sku = aggregate_by_sku(rows)
    top_n = ns.top if ns.top is not None and ns.top >= 0 else None
    if top_n is not None:
        by_sku = by_sku[:top_n]

    # Optional CSV export of BY_SKU.
    if ns.out:
        out_path = Path(ns.out)
        with out_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["sku", "amount"])
            for sku, amt in by_sku:
                writer.writerow([sku, f"{amt:.2f}"])

    print(_format_output(rows, top=top_n, by_date=ns.by_date))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
