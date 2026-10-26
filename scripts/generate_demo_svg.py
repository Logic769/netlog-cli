import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich import box

def build_demo_screen():
    console = Console(record=True, width=130, height=30)

    # Header Panel
    header_text = Text()
    header_text.append(" 🌐 NETLOG-CLI ", style="bold black on bright_cyan")
    header_text.append("  |  Active Sockets: ", style="bold white")
    header_text.append("42", style="bold yellow")
    header_text.append("  |  Tracked Processes: ", style="bold white")
    header_text.append("18", style="bold yellow")
    header_text.append("  |  ▼ Down: ", style="bold green")
    header_text.append("3.2 MB/s", style="bold bright_green")
    header_text.append("  ▲ Up: ", style="bold cyan")
    header_text.append("412.5 KB/s", style="bold bright_cyan")

    header_panel = Panel(
        header_text,
        box=box.ROUNDED,
        border_style="bright_blue",
        padding=(0, 1),
    )

    # Table
    table = Table(
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style="bold bright_white on grey23",
        expand=True,
        row_styles=["none", "dim"],
    )

    table.add_column("PID", justify="right", style="cyan", no_wrap=True, width=7)
    table.add_column("Process", style="bold white", width=16)
    table.add_column("Proto", justify="center", style="yellow", width=6)
    table.add_column("Local Endpoint", style="green", width=22)
    table.add_column("Remote Endpoint", style="bright_blue", width=22)
    table.add_column("Peer / Geo", style="italic bright_white", width=26)
    table.add_column("State", justify="center", width=14)
    table.add_column("Status / Alert", style="bold red")

    demo_rows = [
        ("4821", "chrome", "TCP", "192.168.1.105:54210", "142.250.190.46:443", "google.com [US]", Text("ESTABLISHED", style="bold green"), Text("OK", style="dim green")),
        ("4821", "chrome", "TCP", "192.168.1.105:54212", "140.82.112.4:443", "api.github.com [US]", Text("ESTABLISHED", style="bold green"), Text("OK", style="dim green")),
        ("1290", "discord", "TCP", "192.168.1.105:49811", "162.159.135.232:443", "gateway.discord.gg [US]", Text("ESTABLISHED", style="bold green"), Text("OK", style="dim green")),
        ("892", "sshd", "TCP", "0.0.0.0:22", "*:*", "*:*", Text("LISTEN", style="bold cyan"), Text("OK", style="dim green")),
        ("1043", "dockerd", "TCP", "127.0.0.1:2375", "*:*", "*:*", Text("LISTEN", style="bold cyan"), Text("OK", style="dim green")),
        ("2104", "postgres", "TCP", "127.0.0.1:5432", "*:*", "*:*", Text("LISTEN", style="bold cyan"), Text("OK", style="dim green")),
        ("3188", "python3", "TCP", "192.168.1.105:58220", "52.84.18.99:443", "aws.amazon.com [US]", Text("ESTABLISHED", style="bold green"), Text("OK", style="dim green")),
        ("6219", "unknown_srv", "TCP", "0.0.0.0:23", "*:*", "*:*", Text("LISTEN", style="bold cyan"), Text("⚠ Insecure Telnet port", style="bold red")),
        ("4821", "chrome", "TCP", "192.168.1.105:54216", "172.217.16.206:443", "1e100.net [US]", Text("TIME_WAIT", style="dim yellow"), Text("OK", style="dim green")),
        ("1844", "spotify", "TCP", "192.168.1.105:51200", "35.186.224.25:443", "audio-fa.spotify.com [US]", Text("ESTABLISHED", style="bold green"), Text("OK", style="dim green")),
        ("712", "systemd-resolve", "UDP", "127.0.0.53:53", "*:*", "*:*", Text("STATELESS", style="bright_blue"), Text("OK", style="dim green")),
    ]

    for row in demo_rows:
        table.add_row(*row)

    # Footer Panel
    footer_text = Text()
    footer_text.append(" [q] ", style="bold cyan")
    footer_text.append("Quit  ", style="dim white")
    footer_text.append(" [s] ", style="bold cyan")
    footer_text.append("Sort: pid  ", style="bold yellow")
    footer_text.append(" [p/space] ", style="bold cyan")
    footer_text.append("Pause  ", style="dim white")
    footer_text.append(" [r] ", style="bold cyan")
    footer_text.append("Reset Sort", style="dim white")

    footer_panel = Panel(footer_text, box=box.ROUNDED, border_style="grey37", padding=(0, 1))

    console.print(header_panel)
    console.print(table)
    console.print(footer_panel)

    os.makedirs("assets", exist_ok=True)
    svg_path = "assets/demo.svg"
    console.save_svg(svg_path, title="netlog-cli Terminal Dashboard")
    print(f"Generated demo SVG at {svg_path}")

if __name__ == "__main__":
    build_demo_screen()
