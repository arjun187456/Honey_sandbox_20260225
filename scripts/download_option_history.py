#!/usr/bin/env python3
import argparse
import csv
import os
import re
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import quote, quote_plus

import requests
from dotenv import load_dotenv


BASE_URL = "https://api.upstox.com"
DEFAULT_INDEX_KEY = "NSE_INDEX|Nifty 50"


def make_headers(token: str):
    return {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }


def get_json(url: str, headers: dict, timeout: int = 20, max_retries: int = 5):
    last_error = None
    for attempt in range(1, max_retries + 1):
        response = requests.get(url, headers=headers, timeout=timeout)
        if response.status_code == 200:
            return response.json()

        body = response.text[:500].replace("\n", " ")
        last_error = f"HTTP {response.status_code} for {url} | {body}"

        should_retry = response.status_code in (429, 500, 502, 503, 504)
        if not should_retry or attempt == max_retries:
            break

        sleep_seconds = min(30, 2 ** (attempt - 1))
        print(f"⚠️ API retry {attempt}/{max_retries} after {response.status_code}; waiting {sleep_seconds}s")
        time.sleep(sleep_seconds)

    raise RuntimeError(last_error or f"Failed request: {url}")


def get_spot_price(index_key: str, headers: dict) -> float:
    url = f"{BASE_URL}/v3/market-quote/ltp?instrument_key={quote(index_key, safe='|,:')}"
    payload = get_json(url, headers)
    data = payload.get("data", {})
    ltp = data.get(index_key, {}).get("last_price", 0)
    if ltp:
        return float(ltp)
    alt_key = index_key.replace("|", ":")
    return float(data.get(alt_key, {}).get("last_price", 0) or 0)


def get_option_chain(index_key: str, expiry_date: str, headers: dict):
    url = (
        f"{BASE_URL}/v2/option/chain"
        f"?instrument_key={quote(index_key, safe='|')}&expiry_date={quote_plus(expiry_date)}"
    )
    payload = get_json(url.replace(" ", ""), headers)
    return payload.get("data", [])


def resolve_expiry(index_key: str, preferred_expiry: str | None, headers: dict) -> tuple[str, list]:
    if not preferred_expiry:
        today = date.today()
        weekday = today.weekday()  # Monday=0 ... Sunday=6
        preferred_expiry = (today + timedelta(days=9 - weekday)).isoformat()

    if preferred_expiry:
        chain = get_option_chain(index_key, preferred_expiry, headers)
        if not chain:
            print(f"ℹ️ No data on preferred expiry {preferred_expiry}, scanning nearby expiries...")
        else:
            return preferred_expiry, chain

    today = date.today()
    for offset in range(0, 46):
        candidate = (today + timedelta(days=offset)).isoformat()
        chain = get_option_chain(index_key, candidate, headers)
        if chain:
            return candidate, chain

    raise RuntimeError("Could not find any expiry with option-chain data in next 45 days")


def extract_instrument_key(option_leg: dict) -> str | None:
    direct_keys = [
        "instrument_key",
        "instrumentKey",
        "instrument_token",
        "instrumentToken",
        "symbol",
    ]
    for key in direct_keys:
        value = option_leg.get(key)
        if isinstance(value, str) and "|" in value:
            return value

    for value in option_leg.values():
        if isinstance(value, dict):
            found = extract_instrument_key(value)
            if found:
                return found
    return None


def pick_near_atm_instruments(chain: list, spot: float, strikes_around: int):
    if not chain:
        return []

    ranked = sorted(
        chain,
        key=lambda row: abs(float(row.get("strike_price", 0)) - spot)
    )

    selected_rows = ranked[: max(1, strikes_around * 2 + 1)]
    instruments = []

    for row in selected_rows:
        strike = float(row.get("strike_price", 0))

        call_leg = row.get("call_options") or {}
        call_key = extract_instrument_key(call_leg)
        if call_key:
            instruments.append({
                "option_type": "CE",
                "strike": strike,
                "instrument_key": call_key,
            })

        put_leg = row.get("put_options") or {}
        put_key = extract_instrument_key(put_leg)
        if put_key:
            instruments.append({
                "option_type": "PE",
                "strike": strike,
                "instrument_key": put_key,
            })

    unique = {}
    for item in instruments:
        unique[item["instrument_key"]] = item
    return list(unique.values())


def fetch_historical_candles(instrument_key: str, interval: str, from_date: str, to_date: str, headers: dict):
    encoded_key = quote(instrument_key, safe="")
    url = f"{BASE_URL}/v2/historical-candle/{encoded_key}/{interval}/{to_date}/{from_date}"
    payload = get_json(url, headers)
    return payload.get("data", {}).get("candles", [])


def sanitize_filename(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("_")


def write_candles_csv(path: Path, candles: list):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["timestamp", "open", "high", "low", "close", "volume", "open_interest"])
        for candle in candles:
            if not isinstance(candle, list) or len(candle) < 6:
                continue
            row = candle[:7] if len(candle) >= 7 else candle + [None]
            writer.writerow(row)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Download options historical candles from Upstox and save CSV files"
    )
    parser.add_argument("--days", type=int, default=100, help="Number of days back from today")
    parser.add_argument("--interval", default="day", choices=["1minute", "30minute", "day", "week", "month"])
    parser.add_argument("--index-key", default=DEFAULT_INDEX_KEY, help="Underlying index instrument key")
    parser.add_argument("--expiry", default=None, help="Expiry date YYYY-MM-DD (auto-detect if omitted)")
    parser.add_argument("--strikes-around", type=int, default=2, help="Strikes around ATM (2 -> 5 strikes total)")
    parser.add_argument("--max-instruments", type=int, default=10, help="Max option instruments to download")
    parser.add_argument("--output-dir", default="data/options_history", help="Output directory for CSV files")
    parser.add_argument(
        "--instrument-keys",
        default=None,
        help="Comma-separated option instrument keys (skip auto selection when provided)",
    )
    return parser.parse_args()


def main():
    load_dotenv()
    args = parse_args()

    token = os.getenv("UPSTOX_ACCESS_TOKEN")
    if not token:
        print("❌ Missing UPSTOX_ACCESS_TOKEN in environment/.env")
        return 1

    if args.days <= 0:
        print("❌ --days must be greater than 0")
        return 1

    headers = make_headers(token)
    to_date = date.today().isoformat()
    from_date = (date.today() - timedelta(days=args.days)).isoformat()

    print("=" * 72)
    print("📥 OPTION HISTORY DOWNLOADER")
    print("=" * 72)
    print(f"Range: {from_date} -> {to_date}")
    print(f"Interval: {args.interval}")

    selected = []
    expiry_used = args.expiry

    try:
        if args.instrument_keys:
            keys = [k.strip() for k in args.instrument_keys.split(",") if k.strip()]
            selected = [{"option_type": "NA", "strike": 0, "instrument_key": k} for k in keys]
            print(f"Using {len(selected)} explicit instrument keys")
        else:
            expiry_used, chain = resolve_expiry(args.index_key, args.expiry, headers)
            spot = get_spot_price(args.index_key, headers)
            if not spot:
                raise RuntimeError("Could not fetch spot price")
            selected = pick_near_atm_instruments(chain, spot, args.strikes_around)
            if not selected:
                raise RuntimeError("Could not extract option instrument keys from option-chain response")

            print(f"Index: {args.index_key}")
            print(f"Spot: {spot:.2f}")
            print(f"Expiry used: {expiry_used}")

        selected = selected[: args.max_instruments]
        print(f"Instruments selected: {len(selected)}")

        output_root = Path(args.output_dir)
        output_root.mkdir(parents=True, exist_ok=True)

        downloaded = 0
        for idx, item in enumerate(selected, start=1):
            key = item["instrument_key"]
            option_type = item.get("option_type", "NA")
            strike = item.get("strike", 0)
            print(f"[{idx}/{len(selected)}] {key} ({option_type}, strike={strike})")

            candles = fetch_historical_candles(
                instrument_key=key,
                interval=args.interval,
                from_date=from_date,
                to_date=to_date,
                headers=headers,
            )

            filename = sanitize_filename(f"{key}_{args.interval}_{from_date}_{to_date}.csv")
            out_file = output_root / filename
            write_candles_csv(out_file, candles)

            print(f"    ✅ candles={len(candles)} -> {out_file}")
            downloaded += 1

        manifest = output_root / "manifest.csv"
        with manifest.open("w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["generated_at", "index_key", "expiry", "interval", "from_date", "to_date", "file_count"])
            writer.writerow([
                datetime.now().isoformat(timespec="seconds"),
                args.index_key,
                expiry_used or "CUSTOM_KEYS",
                args.interval,
                from_date,
                to_date,
                downloaded,
            ])

        print("=" * 72)
        print(f"✅ Completed. Files saved in: {output_root}")
        print(f"✅ Manifest: {manifest}")
        print("=" * 72)
        return 0

    except Exception as exc:
        print(f"❌ Failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
