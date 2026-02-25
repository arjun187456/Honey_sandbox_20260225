#!/usr/bin/env python3
import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class TradeResult:
    source_file: str
    expiry: str
    instrument_key: str
    entry_time: str
    exit_time: str
    entry_price: float
    exit_price: float
    quantity: int
    pnl_rupees: float
    pnl_pct: float
    mfe_pct: float
    mae_pct: float
    bars_held: int
    exit_reason: str


def parse_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def read_candles(csv_path: Path):
    candles = []
    with csv_path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            ts = row.get("timestamp")
            if not ts:
                continue
            candles.append(
                {
                    "timestamp": ts,
                    "open": parse_float(row.get("open")),
                    "high": parse_float(row.get("high")),
                    "low": parse_float(row.get("low")),
                    "close": parse_float(row.get("close")),
                }
            )

    candles.sort(key=lambda x: x["timestamp"])
    return candles


def simulate_single_instrument(
    candles,
    source_file: str,
    expiry: str,
    instrument_key: str,
    quantity: int,
    breakout_buffer: float,
    initial_sl_pct: float,
    trail_activate_pct: float,
    trailing_sl_pct: float,
    lookback_bars: int,
    confirm_bars: int,
    cooldown_bars: int,
):
    if len(candles) <= lookback_bars + 1:
        return []

    trades = []
    in_position = False
    confirm_count = 0
    cooldown_until_index = -1

    entry_price = 0.0
    entry_index = -1
    entry_time = ""
    stop_loss = 0.0
    trail_activated = False
    highest_price = 0.0
    max_high_since_entry = 0.0
    min_low_since_entry = 0.0

    for idx in range(lookback_bars, len(candles)):
        candle = candles[idx]
        high = candle["high"]
        low = candle["low"]
        close = candle["close"]

        if not in_position:
            if idx <= cooldown_until_index:
                confirm_count = 0
                continue

            ref_high = max(c["high"] for c in candles[idx - lookback_bars : idx])
            trigger = ref_high * (1 + breakout_buffer)
            if close > trigger:
                confirm_count += 1
            else:
                confirm_count = 0

            if confirm_count >= confirm_bars:
                in_position = True
                entry_price = close
                entry_index = idx
                entry_time = candle["timestamp"]
                stop_loss = entry_price * (1 + initial_sl_pct)
                trail_activated = False
                highest_price = entry_price
                max_high_since_entry = entry_price
                min_low_since_entry = entry_price
                confirm_count = 0
            continue

        max_high_since_entry = max(max_high_since_entry, high)
        min_low_since_entry = min(min_low_since_entry, low)
        highest_price = max(highest_price, high)

        if not trail_activated and highest_price >= entry_price * (1 + trail_activate_pct):
            trail_activated = True
            stop_loss = max(stop_loss, highest_price * (1 + trailing_sl_pct))

        if trail_activated:
            stop_loss = max(stop_loss, highest_price * (1 + trailing_sl_pct))

        if low <= stop_loss:
            exit_price = stop_loss
            pnl_rupees = (exit_price - entry_price) * quantity
            pnl_pct = (exit_price - entry_price) / entry_price
            trades.append(
                TradeResult(
                    source_file=source_file,
                    expiry=expiry,
                    instrument_key=instrument_key,
                    entry_time=entry_time,
                    exit_time=candle["timestamp"],
                    entry_price=entry_price,
                    exit_price=exit_price,
                    quantity=quantity,
                    pnl_rupees=pnl_rupees,
                    pnl_pct=pnl_pct,
                    mfe_pct=(max_high_since_entry - entry_price) / entry_price,
                    mae_pct=(min_low_since_entry - entry_price) / entry_price,
                    bars_held=(idx - entry_index + 1),
                    exit_reason="TRAIL_SL" if trail_activated else "INITIAL_SL",
                )
            )
            in_position = False
            cooldown_until_index = idx + cooldown_bars

    if in_position:
        last = candles[-1]
        exit_price = last["close"]
        pnl_rupees = (exit_price - entry_price) * quantity
        pnl_pct = (exit_price - entry_price) / entry_price
        trades.append(
            TradeResult(
                source_file=source_file,
                expiry=expiry,
                instrument_key=instrument_key,
                entry_time=entry_time,
                exit_time=last["timestamp"],
                entry_price=entry_price,
                exit_price=exit_price,
                quantity=quantity,
                pnl_rupees=pnl_rupees,
                pnl_pct=pnl_pct,
                mfe_pct=(max_high_since_entry - entry_price) / entry_price,
                mae_pct=(min_low_since_entry - entry_price) / entry_price,
                bars_held=(len(candles) - entry_index),
                exit_reason="END_OF_DATA",
            )
        )

    return trades


def write_trades_csv(trades, out_csv: Path):
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "source_file",
                "expiry",
                "instrument_key",
                "entry_time",
                "exit_time",
                "entry_price",
                "exit_price",
                "quantity",
                "pnl_rupees",
                "pnl_pct",
                "mfe_pct",
                "mae_pct",
                "bars_held",
                "exit_reason",
            ]
        )
        for t in trades:
            writer.writerow(
                [
                    t.source_file,
                    t.expiry,
                    t.instrument_key,
                    t.entry_time,
                    t.exit_time,
                    f"{t.entry_price:.4f}",
                    f"{t.exit_price:.4f}",
                    t.quantity,
                    f"{t.pnl_rupees:.2f}",
                    f"{t.pnl_pct:.6f}",
                    f"{t.mfe_pct:.6f}",
                    f"{t.mae_pct:.6f}",
                    t.bars_held,
                    t.exit_reason,
                ]
            )


def build_summary(trades, starting_capital: float):
    total_trades = len(trades)
    total_pnl = sum(t.pnl_rupees for t in trades)
    final_capital = starting_capital + total_pnl
    overall_return_pct = (total_pnl / starting_capital) * 100 if starting_capital else 0.0

    wins = [t for t in trades if t.pnl_rupees > 0]
    losses = [t for t in trades if t.pnl_rupees < 0]
    win_rate = (len(wins) / total_trades * 100) if total_trades else 0.0

    avg_win = sum(t.pnl_rupees for t in wins) / len(wins) if wins else 0.0
    avg_loss = sum(t.pnl_rupees for t in losses) / len(losses) if losses else 0.0

    near_miss = [t for t in losses if 0.08 <= t.mfe_pct < 0.10]
    early_stop = [t for t in losses if t.bars_held <= 2 and t.mae_pct <= -0.10]
    strong_trend = [t for t in wins if t.mfe_pct >= 0.15]

    by_exit = {}
    for t in trades:
        by_exit[t.exit_reason] = by_exit.get(t.exit_reason, 0) + 1

    return {
        "total_trades": total_trades,
        "total_pnl": total_pnl,
        "final_capital": final_capital,
        "overall_return_pct": overall_return_pct,
        "win_rate": win_rate,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "near_miss_count": len(near_miss),
        "early_stop_count": len(early_stop),
        "strong_trend_count": len(strong_trend),
        "exit_counts": by_exit,
    }


def write_summary_md(summary: dict, out_md: Path, params: dict):
    out_md.parent.mkdir(parents=True, exist_ok=True)
    exit_lines = "\n".join([f"- {k}: {v}" for k, v in sorted(summary["exit_counts"].items())]) or "- None"

    scenarios = [
        f"- Near-miss trail activations (MFE 8-10% but losing): {summary['near_miss_count']}",
        f"- Fast stop-outs (<=2 bars and MAE <= -10%): {summary['early_stop_count']}",
        f"- Strong trend captures (winning trades with MFE >= 15%): {summary['strong_trend_count']}",
    ]

    lines = [
        "# Backtest Report (Options Dataset)",
        "",
        f"Generated at: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Configuration",
        f"- Data root: {params['data_root']}",
        f"- Quantity per trade: {params['quantity']}",
        f"- Starting capital: ₹{params['starting_capital']:,.2f}",
        f"- Breakout lookback bars: {params['lookback_bars']}",
        f"- Confirmation bars: {params['confirm_bars']}",
        f"- Cooldown bars after SL: {params['cooldown_bars']}",
        f"- Breakout buffer: {params['breakout_buffer'] * 100:.2f}%",
        f"- Initial SL: {params['initial_sl_pct'] * 100:.2f}%",
        f"- Trail activation: {params['trail_activate_pct'] * 100:.2f}%",
        f"- Trailing SL gap: {abs(params['trailing_sl_pct']) * 100:.2f}%",
        "",
        "## Results",
        f"- Total trades: {summary['total_trades']}",
        f"- Total P&L: ₹{summary['total_pnl']:,.2f}",
        f"- Final capital: ₹{summary['final_capital']:,.2f}",
        f"- Overall return: {summary['overall_return_pct']:.2f}%",
        f"- Win rate: {summary['win_rate']:.2f}%",
        f"- Avg win: ₹{summary['avg_win']:.2f}",
        f"- Avg loss: ₹{summary['avg_loss']:.2f}",
        "",
        "## Exit Reasons",
        exit_lines,
        "",
        "## Scenario Diagnostics",
        *scenarios,
        "",
        "## Suggested Changes to Test Next",
        "- If near-miss count is high, test trail activation at +8% instead of +10%.",
        "- If fast stop-outs are frequent, add trend filter (e.g., only trade when prior bar closes near high).",
        "- If strong trends are many, test a wider trailing gap to reduce premature exits.",
        "",
        "## Important Limitation",
        "- This replay uses candle-level OHLC and contract-level files, not tick-level full option-chain state.",
        "- 100-day query window does not imply 100 candles per contract; each option has limited listed life.",
    ]

    out_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser(description="Backtest breakout + trailing logic on downloaded option CSVs")
    parser.add_argument("--data-root", default="data/options_history_100d_all_expiries")
    parser.add_argument("--starting-capital", type=float, default=10000)
    parser.add_argument("--quantity", type=int, default=50)
    parser.add_argument("--lookback-bars", type=int, default=3)
    parser.add_argument("--confirm-bars", type=int, default=1)
    parser.add_argument("--cooldown-bars", type=int, default=0)
    parser.add_argument("--breakout-buffer", type=float, default=0.001)
    parser.add_argument("--initial-sl-pct", type=float, default=-0.10)
    parser.add_argument("--trail-activate-pct", type=float, default=0.10)
    parser.add_argument("--trailing-sl-pct", type=float, default=-0.04)
    parser.add_argument("--report-md", default="reports/backtest_100d_report.md")
    parser.add_argument("--trades-csv", default="reports/backtest_100d_trades.csv")
    return parser.parse_args()


def main():
    args = parse_args()
    data_root = Path(args.data_root)
    if not data_root.exists():
        print(f"❌ Data root not found: {data_root}")
        return 1

    csv_files = sorted(data_root.glob("expiry_*/NSE_FO_*_*.csv"))
    if not csv_files:
        print(f"❌ No instrument CSV files found under: {data_root}")
        return 1

    all_trades = []

    for file_path in csv_files:
        candles = read_candles(file_path)
        if not candles:
            continue

        expiry = file_path.parent.name.replace("expiry_", "")
        name_parts = file_path.stem.split("_")
        instrument_key = "UNKNOWN"
        if len(name_parts) >= 3:
            instrument_key = f"{name_parts[0]}|{name_parts[1]}"

        trades = simulate_single_instrument(
            candles=candles,
            source_file=str(file_path),
            expiry=expiry,
            instrument_key=instrument_key,
            quantity=args.quantity,
            breakout_buffer=args.breakout_buffer,
            initial_sl_pct=args.initial_sl_pct,
            trail_activate_pct=args.trail_activate_pct,
            trailing_sl_pct=args.trailing_sl_pct,
            lookback_bars=args.lookback_bars,
            confirm_bars=args.confirm_bars,
            cooldown_bars=args.cooldown_bars,
        )
        all_trades.extend(trades)

    summary = build_summary(all_trades, args.starting_capital)
    write_trades_csv(all_trades, Path(args.trades_csv))

    write_summary_md(
        summary=summary,
        out_md=Path(args.report_md),
        params={
            "data_root": str(data_root),
            "quantity": args.quantity,
            "starting_capital": args.starting_capital,
            "lookback_bars": args.lookback_bars,
            "confirm_bars": args.confirm_bars,
            "cooldown_bars": args.cooldown_bars,
            "breakout_buffer": args.breakout_buffer,
            "initial_sl_pct": args.initial_sl_pct,
            "trail_activate_pct": args.trail_activate_pct,
            "trailing_sl_pct": args.trailing_sl_pct,
        },
    )

    print("=" * 72)
    print("✅ BACKTEST COMPLETE")
    print("=" * 72)
    print(f"Trades: {summary['total_trades']}")
    print(f"Total P&L: ₹{summary['total_pnl']:.2f}")
    print(f"Overall Return: {summary['overall_return_pct']:.2f}%")
    print(f"Report: {args.report_md}")
    print(f"Trades CSV: {args.trades_csv}")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
