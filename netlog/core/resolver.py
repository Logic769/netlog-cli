import socket
from typing import Dict, Optional, Set
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor

class AsyncDNSResolver:
    """
    Non-blocking asynchronous reverse-DNS resolver with an LRU cache.
    Prevents UI frame rate drops during network inspection.
    """

    def __init__(self, max_cache_size: int = 1024, max_workers: int = 4):
        self.max_cache_size = max_cache_size
        self._cache: OrderedDict[str, str] = OrderedDict()
        self._pending_ips: Set[str] = set()
        self._pool = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="dns-worker")

    def _is_private_or_local(self, ip: str) -> bool:
        if not ip or ip == "0.0.0.0" or ip == "::":
            return True
        if ip.startswith("127.") or ip == "::1":
            return True
        if ip.startswith("10.") or ip.startswith("192.168."):
            return True
        if ip.startswith("172."):
            try:
                second_octet = int(ip.split(".")[1])
                if 16 <= second_octet <= 31:
                    return True
            except (IndexError, ValueError):
                pass
        return False

    def _resolve_task(self, ip: str):
        try:
            hostname, _, _ = socket.gethostbyaddr(ip)
        except (socket.herror, socket.gaierror, TimeoutError, OSError):
            hostname = ip
        except Exception:
            hostname = ip

        # Save to LRU cache
        self._cache[ip] = hostname
        if len(self._cache) > self.max_cache_size:
            self._cache.popitem(last=False)

        self._pending_ips.discard(ip)

    def resolve(self, ip: Optional[str]) -> str:
        """
        Fast lookup: returns cached hostname if available.
        If uncached, queues an asynchronous background lookup and returns the IP immediately.
        """
        if not ip:
            return "*:*"

        if ip in self._cache:
            # Move to end for LRU freshness
            self._cache.move_to_end(ip)
            return self._cache[ip]

        if self._is_private_or_local(ip):
            self._cache[ip] = "localhost" if (ip.startswith("127.") or ip == "::1") else "lan"
            return self._cache[ip]

        # Queue async task if not already in flight
        if ip not in self._pending_ips:
            self._pending_ips.add(ip)
            self._pool.submit(self._resolve_task, ip)

        return ip

    def shutdown(self):
        """Cleanly terminate worker threads."""
        self._pool.shutdown(wait=False)
