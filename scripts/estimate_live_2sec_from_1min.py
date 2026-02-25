#!/usr/bin/env python3
import argparse
import csv
import random
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class Trade:
    pnl_rupees: float
    pnl_pct: float


@dataclass
class Scenario:
    name: str
    description: str
    entry_slippage_pct: float
    exit_slippage_pct: float
    fees_rupees_per_trade: float
    missed_trade_prob: float
    false_entry_prob: float
    false_entry_loss_pct: float
    stop_hunt_prob: float
    stop_hunt_loss_pct: float


def load_trades(path: Path):
    trades = []
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            try:
                trades.append(
                    Trade(
                        pnl_rupees=float(row["pnl_rupees"]),
                        pnl_pct=float(row["pnl_pct"]),
                    )
                )
            except Exception:
                continue
    return trades


def percentile(values, q):
    if not values:
        return 0.0
    arr = sorted(values)
    idx = int((len(arr) - 1) * q)
    return arr[idx]


def simulate_once(trades, scenario: Scenario, quantity: int):
    executed_pnls = []

    for t in trades:
        if random.random() < scenario.missed_trade_prob:
            continue

        pnl_pct = t.pnl_pct

        total_slippage_pct = scenario.entry_slippage_pct + scenario.exit_slippage_pct
        pnl_pct -= total_slippage_pct

        if random.random() < scenario.stop_hunt_prob:
            pnl_pct = min(pnl_pct, scenario.stop_hunt_loss_pct)

        pnl_rupees = pnl_pct * quantity * 100
        pnl_rupees -= scenario.fees_rupees_per_trade

        executed_pnls.append(pnl_rupees)

        if random.random() < scenario.false_entry_prob:
            false_pnl = scenario.false_entry_loss_pct * quantity * 100
            false_pnl -= scenario.fees_rupees_per_trade
            executed_pnls.append(false_pnl)

    total_pnl = sum(executed_pnls)
    wins = sum(1 for x in executed_pnls if x > 0)
    win_rate = (wins / len(executed_pnls) * 100) if executed_pnls else 0.0

    return {
        "trades": len(executed_pnls),
        "total_pnl": total_pnl,
        "win_rate": win_rate,
    }


def summarize_runs(runs, starting_capital):
    totals = [r["total_pnl"] for r in runs]
    win_rates = [r["win_rate"] for r in runs]
    trades = [r["trades"] for r in runs]

    mean_total = sum(totals) / len(totals)
    mean_wr = sum(win_rates) / len(win_rates)
    mean_trades = sum(trades) / len(trades)

    return {
        "mean_total_pnl": mean_total,
        "mean_return_pct": (mean_total / starting_capital) * 100 if starting_capital else 0.0,
        "mean_win_rate": mean_wr,
        "mean_trades": mean_trades,
        "p10_return_pct": (percentile(totals, 0.10) / starting_capital) * 100 if starting_capital else 0.0,
        "p50_return_pct": (percentile(totals, 0.50) / starting_capital) * 100 if starting_capital else 0.0,
        "p90_return_pct": (percentile(totals, 0.90) / starting_capital) * 100 if starting_capital else 0.0,
        "p10_win_rate": percentile(win_rates, 0.10),
        "p50_win_rate": percentile(win_rates, 0.50),
        "p90_win_rate": percentile(win_rates, 0.90),
    }


def default_scenarios():
    return [
        Scenario(
            name="Aggressive 2s",
            description="No debounce; highest micro-noise and overtrading",
            entry_slippage_pct=0.0015,
            exit_slippage_pct=0.0015,
            fees_rupees_per_trade=25,
            missed_trade_prob=0.02,
            false_entry_prob=0.22,
            false_entry_loss_pct=-0.06,
            stop_hunt_prob=0.12,
            stop_hunt_loss_pct=-0.08,
        ),
        Scenario(
            name="Balanced 2s",
            description="Debounce 10-20s; moderate false triggers",
            entry_slippage_pct=0.0012,
            exit_slippage_pct=0.0012,
            fees_rupees_per_trade=25,
            missed_trade_prob=0.08,
            false_entry_prob=0.10,
            false_entry_loss_pct=-0.05,
            stop_hunt_prob=0.08,
            stop_hunt_loss_pct=-0.06,
        ),
        Scenario(
            name="Conservative 2s",
            description="Debounce + confirmation filter; fewer but cleaner trades",
            entry_slippage_pct=0.0010,
            exit_slippage_pct=0.0010,
            fees_rupees_per_trade=25,
            missed_trade_prob=0.20,
            false_entry_prob=0.04,
            false_entry_loss_pct=-0.04,
            stop_hunt_prob=0.05,
            stop_hunt_loss_pct=-0.05,
        ),
    ]


def write_report(path: Path, baseline, scenario_results, simulations, starting_capital):
    lines = [
        "# 2-Second Live Monitoring Impact Estimate",
        "",
        f"Generated at: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Baseline (1-minute backtest)",
        f"- Trades: {baseline['trades']}",
        f"- Total P&L: ₹{baseline['total_pnl']:,.2f}",
        f"- Return: {baseline['return_pct']:.2f}%",
        f"- Win rate: {baseline['win_rate']:.2f}%",
        "",
        "## Assumptions",
        "- Uses 1-minute trade outcomes as base and applies execution/noise Monte Carlo adjustments.",
        "- Includes slippage, per-trade charges, missed trades, false entries, and stop-hunt effects.",
        "- This is an estimate, not a tick-accurate replay.",
        "",
        f"## Scenario Results ({simulations} simulations each)",
        "",
        "| Scenario | Mean Return % | P10 Return % | P50 Return % | P90 Return % | Mean Win Rate % | P10 WR % | P90 WR % | Mean Trades |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for row in scenario_results:
        s = row["summary"]
        lines.append(
            f"| {row['scenario'].name} | {s['mean_return_pct']:.2f} | {s['p10_return_pct']:.2f} | {s['p50_return_pct']:.2f} | {s['p90_return_pct']:.2f} | {s['mean_win_rate']:.2f} | {s['p10_win_rate']:.2f} | {s['p90_win_rate']:.2f} | {s['mean_trades']:.1f} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "- Aggressive 2s often increases trade count but can reduce quality due to micro-noise.",
            "- Balanced debounce typically gives better risk-adjusted behavior.",
            "- Conservative mode can improve win quality but may miss some trend entries.",
            "",
            "## Next Validation Step",
            "- Run 2-4 weeks paper trading at 2s and compare realized metrics to the Balanced scenario band.",
        ]
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser(description="Estimate 2-second live impact from 1-minute backtest trades")
    parser.add_argument("--trades-csv", default="reports/backtest_1min_trades.csv")
    parser.add_argument("--output-report", default="reports/live_2sec_impact_estimate.md")
    parser.add_argument("--starting-capital", type=float, default=10000)
    parser.add_argument("--quantity", type=int, default=50)
    parser.add_argument("--simulations", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main():
    args = parse_args()
    random.seed(args.seed)

    trades = load_trades(Path(args.trades_csv))
    if not trades:
        print(f"❌ No trades found in {args.trades_csv}")
        return 1

    baseline_total = sum(t.pnl_rupees for t in trades)
    baseline_wr = (sum(1 for t in trades if t.pnl_rupees > 0) / len(trades)) * 100
    baseline = {
        "trades": len(trades),
        "total_pnl": baseline_total,
        "return_pct": (baseline_total / args.starting_capital) * 100,
        "win_rate": baseline_wr,
    }

    scenario_results = []
    for scenario in default_scenarios():
        runs = [simulate_once(trades, scenario, args.quantity) for _ in range(args.simulations)]
        summary = summarize_runs(runs, args.starting_capital)
        scenario_results.append({"scenario": scenario, "summary": summary})

    write_report(
        path=Path(args.output_report),
        baseline=baseline,
        scenario_results=scenario_results,
        simulations=args.simulations,
        starting_capital=args.starting_capital,
    )

    print("=" * 72)
    print("✅ 2-SECOND IMPACT ESTIMATE COMPLETE")
    print("=" * 72)
    print(f"Baseline return: {baseline['return_pct']:.2f}% | win rate: {baseline['win_rate']:.2f}%")
    for row in scenario_results:
        s = row["summary"]
        print(
            f"{row['scenario'].name}: mean return {s['mean_return_pct']:.2f}% | "
            f"mean win rate {s['mean_win_rate']:.2f}%"
        )
    print(f"Report: {args.output_report}")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
