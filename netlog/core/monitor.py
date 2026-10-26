import socket
from typing import List, Dict, Optional, Tuple
import psutil
from netlog.core.models import ConnectionInfo, ProcessNetworkStats

class SocketMonitor:
    """
    Scans active system sockets and maps them to process metadata safely.
    Handles ephemeral processes, access restrictions, and kernel threads.
    """

    def __init__(self):
        self._process_cache: Dict[int, Tuple[str, str]] = {}

    def _get_process_meta(self, pid: Optional[int]) -> Tuple[str, str]:
        if pid is None or pid == 0:
            return "System / Idle", "root"

        if pid in self._process_cache:
            return self._process_cache[pid]

        try:
            proc = psutil.Process(pid)
            name = proc.name() or "unknown"
            username = proc.username() or "unknown"
            self._process_cache[pid] = (name, username)
            return name, username
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return "terminated", "unknown"
        except Exception:
            return "unknown", "unknown"

    def scan_connections(self, kind: str = "inet") -> List[ConnectionInfo]:
        """
        Scan all active internet network connections (TCP and UDP).
        """
        raw_conns = []
        try:
            raw_conns = psutil.net_connections(kind=kind)
        except (psutil.AccessDenied, PermissionError):
            # Fallback when running unprivileged without root
            try:
                raw_conns = psutil.net_connections(kind="inet4")
            except Exception:
                raw_conns = []
        except Exception:
            raw_conns = []

        connections: List[ConnectionInfo] = []

        for c in raw_conns:
            family_str = "IPv4" if c.family == socket.AF_INET else "IPv6"
            proto_str = "TCP" if c.type == socket.SOCK_STREAM else "UDP"

            laddr_ip = c.laddr.ip if c.laddr else "0.0.0.0"
            laddr_port = c.laddr.port if c.laddr else 0

            raddr_ip = c.raddr.ip if c.raddr else None
            raddr_port = c.raddr.port if c.raddr else None

            status_str = c.status if c.status else "NONE"
            if proto_str == "UDP" and status_str == "NONE":
                status_str = "STATELESS"

            proc_name, proc_user = self._get_process_meta(c.pid)

            conn = ConnectionInfo(
                fd=c.fd if c.fd is not None else -1,
                family=family_str,
                proto=proto_str,
                laddr=laddr_ip,
                lport=laddr_port,
                raddr=raddr_ip,
                rport=raddr_port,
                status=status_str,
                pid=c.pid,
                process_name=proc_name,
                user=proc_user,
            )
            connections.append(conn)

        return connections

    def group_by_process(self, connections: List[ConnectionInfo]) -> Dict[int, ProcessNetworkStats]:
        """
        Groups connection list by Process ID with status breakdowns.
        """
        grouped: Dict[int, ProcessNetworkStats] = {}

        for conn in connections:
            pid = conn.pid or 0
            if pid not in grouped:
                grouped[pid] = ProcessNetworkStats(
                    pid=pid,
                    name=conn.process_name,
                    user=conn.user,
                    connections_count=0,
                    established_count=0,
                    listen_count=0,
                    connections=[],
                )

            stats = grouped[pid]
            stats.connections_count += 1
            if conn.status == "ESTABLISHED":
                stats.established_count += 1
            elif conn.status == "LISTEN":
                stats.listen_count += 1

            stats.connections.append(conn)

        return grouped
