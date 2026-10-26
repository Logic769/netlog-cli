from typing import List, Dict
from netlog.core.models import ConnectionInfo, ProcessNetworkStats

SUSPICIOUS_CLEARTEXT_PORTS = {
    21: "Unencrypted FTP",
    23: "Insecure Telnet",
    69: "Trivial FTP (TFTP)",
    513: "rlogin",
    514: "rsh",
}

class AnomalyDetector:
    """
    Lightweight heuristic rule-based anomaly detector for active network connections.
    Identifies high connection burst rates, insecure protocols, and abnormal port activity.
    """

    def __init__(self, connection_threshold_per_proc: int = 50):
        self.conn_threshold = connection_threshold_per_proc

    def inspect_connections(self, connections: List[ConnectionInfo], proc_stats: Dict[int, ProcessNetworkStats]):
        """
        Inspects connections in-place, marking suspicious ones with reason tags.
        """
        for conn in connections:
            if not conn.raddr or conn.rport is None:
                continue

            # Rule 1: Cleartext obsolete protocols
            if conn.rport in SUSPICIOUS_CLEARTEXT_PORTS:
                conn.is_suspicious = True
                conn.anomaly_reason = f"Security: {SUSPICIOUS_CLEARTEXT_PORTS[conn.rport]}"

            # Rule 2: High socket count from non-browser process
            if conn.pid and conn.pid in proc_stats:
                stats = proc_stats[conn.pid]
                proc_name = stats.name.lower()
                is_browser = any(b in proc_name for b in ["brave", "chrome", "firefox", "chromium", "safari"])
                if not is_browser and stats.connections_count > self.conn_threshold:
                    conn.is_suspicious = True
                    conn.anomaly_reason = f"Traffic Spike: {stats.connections_count} sockets"
