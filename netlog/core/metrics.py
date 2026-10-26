import time
from typing import Dict, Tuple, Optional
import psutil
from netlog.core.models import ProcessNetworkStats, NetworkSnapshot, ConnectionInfo
from netlog.core.monitor import SocketMonitor

class RateCalculator:
    """
    Computes real-time upload and download throughput (KB/s)
    using differential sampling across moving time windows.
    """

    def __init__(self, monitor: Optional[SocketMonitor] = None):
        self.monitor = monitor or SocketMonitor()
        self._last_system_time = time.time()
        self._last_system_io = psutil.net_io_counters()

        # Cache of PID -> (bytes_read, bytes_written, timestamp)
        self._proc_io_history: Dict[int, Tuple[int, int, float]] = {}

    def get_system_rates(self) -> Tuple[float, float, int, int]:
        """
        Returns (upload_kbps, download_kbps, total_bytes_sent, total_bytes_recv)
        """
        now = time.time()
        dt = max(now - self._last_system_time, 0.001)

        current_io = psutil.net_io_counters()
        bytes_sent_delta = current_io.bytes_sent - self._last_system_io.bytes_sent
        bytes_recv_delta = current_io.bytes_recv - self._last_system_io.bytes_recv

        # Update cache
        self._last_system_time = now
        self._last_system_io = current_io

        upload_kbps = max(bytes_sent_delta / 1024.0 / dt, 0.0)
        download_kbps = max(bytes_recv_delta / 1024.0 / dt, 0.0)

        return upload_kbps, download_kbps, current_io.bytes_sent, current_io.bytes_recv

    def update_process_rates(self, proc_stats_map: Dict[int, ProcessNetworkStats]):
        """
        Updates each active ProcessNetworkStats with calculated download/upload KB/s.
        Uses process IO counters to estimate network throughput.
        """
        now = time.time()

        for pid, stats in proc_stats_map.items():
            if pid <= 0:
                continue

            try:
                proc = psutil.Process(pid)
                io = proc.io_counters()
                cur_read = io.read_bytes
                cur_write = io.write_bytes

                if pid in self._proc_io_history:
                    last_read, last_write, last_time = self._proc_io_history[pid]
                    dt = max(now - last_time, 0.001)

                    stats.download_rate = max((cur_read - last_read) / 1024.0 / dt, 0.0)
                    stats.upload_rate = max((cur_write - last_write) / 1024.0 / dt, 0.0)
                    stats.bytes_recv = cur_read
                    stats.bytes_sent = cur_write
                else:
                    stats.download_rate = 0.0
                    stats.upload_rate = 0.0

                self._proc_io_history[pid] = (cur_read, cur_write, now)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Clean up stale history
                self._proc_io_history.pop(pid, None)

    def capture_snapshot(self) -> NetworkSnapshot:
        """
        Creates a complete atomic point-in-time network snapshot.
        """
        connections = self.monitor.scan_connections()
        grouped_procs = self.monitor.group_by_process(connections)

        up_rate, down_rate, sys_sent, sys_recv = self.get_system_rates()
        self.update_process_rates(grouped_procs)

        return NetworkSnapshot(
            timestamp=time.time(),
            total_connections=len(connections),
            active_processes_count=len(grouped_procs),
            system_bytes_sent=sys_sent,
            system_bytes_recv=sys_recv,
            system_upload_rate=up_rate,
            system_download_rate=down_rate,
            connections=connections,
            processes=grouped_procs,
        )
