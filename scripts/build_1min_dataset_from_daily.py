#!/usr/bin/env python3
import argparse
import csv
import os
import re
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import requests
from dotenv import load_dotenv


BASE_URL = "https://api.upstox.com"


def make_headers(token: str):
    return {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }


def get_json(url: str, headers: dict, timeout: int = 20, max_retries: int = 6):
    last_error = None
    for attempt in range(1, max_retries + 1):
        response = requests.get(url, headers=headers, timeout=timeout)
        if response.status_code == 200:
            return response.json()

        body = response.text[:500].replace("\n", " ")
        last_error = f"HTTP {response.status_code} for {url} | {body}"
        retryable = response.status_code in (429, 500, 502, 503, 504)
        if not retryable or attempt == max_retries:
            break
        sleep_for = min(45, 2 ** (attempt - 1))
        print(f"⚠️ Retry {attempt}/{max_retries} after {response.status_code}; sleeping {sleep_for}s")
        time.sleep(sleep_for)

    raise RuntimeError(last_error or f"Failed request: {url}")


def fetch_1min_candles(instrument_key: str, from_date: str, to_date: str, headers: dict):
    encoded = quote(instrument_key, safe="")
    url = f"{BASE_URL}/v2/historical-candle/{encoded}/1minute/{to_date}/{from_date}"
    payload = get_json(url, headers)
    return payload.get("data", {}).get("candles", [])


def parse_instrument_key_from_name(file_name: str):
    m = re.search(r"(NSE_FO)_(\d+)_", file_name)
    if not m:
        return None
    return f"{m.group(1)}|{m.group(2)}"


def read_actual_date_range(day_csv: Path):
    min_dt = None
    max_dt = None
    with day_csv.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            ts = row.get("timestamp")
            if not ts:
                continue
            try:
                dt = datetime.fromisoformat(ts)
            except Exception:
                continue
            if min_dt is None or dt < min_dt:
                min_dt = dt
            if max_dt is None or dt > max_dt:
                max_dt = dt
    if min_dt is None or max_dt is None:
        return None, None
    return min_dt.date().isoformat(), max_dt.date().isoformat()


def write_candles_csv(path: Path, candles: list):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["timestamp", "open", "high", "low", "close", "volume", "open_interest"])
        for candle in candles:
            if not isinstance(candle, list) or len(candle) < 6:
                continue
            row = candle[:7] if len(candle) >= 7 else candle + [None]
            writer.writerow(row)


def parse_args():
    parser = argparse.ArgumentParser(description="Build 1-minute dataset from existing daily options dataset")
    parser.add_argument("--source-root", default="data/options_history_100d_all_expiries")
    parser.add_argument("--output-root", default="data/options_history_1min_all_expiries")
    parser.add_argument("--max-files", type=int, default=0, help="Limit number of instrument files (0 = all)")
    return parser.parse_args()


def main():
    load_dotenv()
    token = os.getenv("UPSTOX_ACCESS_TOKEN")
    if not token:
        print("❌ Missing UPSTOX_ACCESS_TOKEN")
        return 1

    args = parse_args()
    source_root = Path(args.source_root)
    output_root = Path(args.output_root)

    day_files = sorted(source_root.glob("expiry_*/NSE_FO_*_day_*.csv"))
    if not day_files:
        print(f"❌ No day files found under {source_root}")
        return 1

    if args.max_files > 0:
        day_files = day_files[: args.max_files]

    headers = make_headers(token)

    print("=" * 72)
    print("📥 BUILDING 1-MIN DATASET FROM DAILY FILES")
    print("=" * 72)
    print(f"Source files: {len(day_files)}")

    success = 0
    failed = 0
    manifest_rows = []

    for idx, day_file in enumerate(day_files, start=1):
        expiry_folder = day_file.parent.name
        instrument_key = parse_instrument_key_from_name(day_file.name)
        if not instrument_key:
            failed += 1
            continue

        from_date, to_date = read_actual_date_range(day_file)
        if not from_date or not to_date:
            failed += 1
            continue

        out_file = output_root / expiry_folder / day_file.name.replace("_day_", "_1minute_")
        print(f"[{idx}/{len(day_files)}] {instrument_key} | {from_date} -> {to_date}")

        try:
            candles = fetch_1min_candles(instrument_key, from_date, to_date, headers)
            write_candles_csv(out_file, candles)
            manifest_rows.append([expiry_folder.replace("expiry_", ""), instrument_key, from_date, to_date, len(candles), str(out_file)])
            print(f"    ✅ candles={len(candles)} -> {out_file}")
            success += 1
            time.sleep(0.25)
        except Exception as exc:
            print(f"    ❌ failed: {exc}")
            failed += 1

    output_root.mkdir(parents=True, exist_ok=True)
    manifest = output_root / "manifest.csv"
    with manifest.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["expiry", "instrument_key", "from_date", "to_date", "candles", "file"])
        writer.writerows(manifest_rows)

    print("=" * 72)
    print(f"✅ Done. success={success}, failed={failed}")
    print(f"✅ Manifest: {manifest}")
    print("=" * 72)
    return 0 if success > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
