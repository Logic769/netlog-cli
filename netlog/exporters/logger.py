import csv
import json
import time
from pathlib import Path
from typing import List
from netlog.core.models import ConnectionInfo

class TrafficExporter:
    """
    Exports network snapshots to CSV and structured JSON format.
    """

    @staticmethod
    def export_csv(connections: List[ConnectionInfo], output_path: str = "logs/traffic.csv"):
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Timestamp", "PID", "Process", "User", "Proto",
                "Local_Endpoint", "Remote_Endpoint", "State", "Suspicious", "Alert"
            ])
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            for c in connections:
                writer.writerow([
                    ts, c.pid or "", c.process_name, c.user, c.proto,
                    c.local_endpoint, c.remote_endpoint, c.status,
                    c.is_suspicious, c.anomaly_reason
                ])

    @staticmethod
    def export_json(connections: List[ConnectionInfo], output_path: str = "logs/traffic.jsonl"):
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        ts = time.time()
        with open(output_path, mode="a", encoding="utf-8") as f:
            for c in connections:
                record = {
                    "timestamp": ts,
                    "pid": c.pid,
                    "process": c.process_name,
                    "user": c.user,
                    "proto": c.proto,
                    "local": c.local_endpoint,
                    "remote": c.remote_endpoint,
                    "state": c.status,
                    "is_suspicious": c.is_suspicious,
                    "anomaly_reason": c.anomaly_reason,
                }
                f.write(json.dumps(record) + "\n")
