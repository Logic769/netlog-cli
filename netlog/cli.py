import argparse
import sys
import time
from rich.console import Console
from rich.live import Live

from netlog import __version__
from netlog.core.metrics import RateCalculator
from netlog.core.resolver import AsyncDNSResolver
from netlog.core.anomaly import AnomalyDetector
from netlog.ui.dashboard import render_dashboard, create_connections_table
from netlog.exporters.logger import TrafficExporter

def parse_args():
    parser = argparse.ArgumentParser(
        prog="netlog",
        description="High-performance CLI network telemetry dashboard tracking socket states, live bandwidth, and async DNS."
    )
    parser.add_argument(
        "-i", "--interval",
        type=float,
        default=1.0,
        help="Refresh sampling interval in seconds (default: 1.0)"
    )
    parser.add_argument(
        "-p", "--process",
        type=str,
        default=None,
        help="Filter connections matching process name (case-insensitive substring)"
    )
    parser.add_argument(
        "-n", "--rows",
        type=int,
        default=25,
        help="Maximum rows to display in the live table (default: 25)"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Capture a single snapshot, display in terminal, and exit immediately"
    )
    parser.add_argument(
        "--export-csv",
        type=str,
        metavar="PATH",
        help="Export snapshot to CSV file"
    )
    parser.add_argument(
        "--export-json",
        type=str,
        metavar="PATH",
        help="Stream snapshots as structured JSON lines"
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"netlog-cli {__version__}"
    )
    return parser.parse_args()

def main():
    args = parse_args()
    console = Console()

    rate_engine = RateCalculator()
    dns_resolver = AsyncDNSResolver()
    anomaly_detector = AnomalyDetector()

    if args.once:
        snapshot = rate_engine.capture_snapshot()
        anomaly_detector.inspect_connections(snapshot.connections, snapshot.processes)

        if args.export_csv:
            TrafficExporter.export_csv(snapshot.connections, args.export_csv)
            console.print(f"[green]✔ Exported {len(snapshot.connections)} records to {args.export_csv}[/green]")

        if args.export_json:
            TrafficExporter.export_json(snapshot.connections, args.export_json)
            console.print(f"[green]✔ Exported {len(snapshot.connections)} records to {args.export_json}[/green]")

        table = create_connections_table(
            snapshot.connections,
            dns_resolver,
            max_rows=args.rows,
            filter_process=args.process
        )
        console.print(table)
        dns_resolver.shutdown()
        return

    # Live Interactive Loop
    try:
        with Live(console=console, screen=True, refresh_per_second=int(1.0 / max(args.interval, 0.2))) as live:
            while True:
                snapshot = rate_engine.capture_snapshot()
                anomaly_detector.inspect_connections(snapshot.connections, snapshot.processes)

                if args.export_json:
                    TrafficExporter.export_json(snapshot.connections, args.export_json)

                layout = render_dashboard(
                    snapshot,
                    dns_resolver,
                    filter_process=args.process,
                    max_rows=args.rows
                )
                live.update(layout)
                time.sleep(args.interval)

    except KeyboardInterrupt:
        pass
    finally:
        dns_resolver.shutdown()
        console.print("\n[bold cyan]netlog-cli stopped cleanly. Goodbye![/bold cyan]")

if __name__ == "__main__":
    main()
