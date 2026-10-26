import ipaddress
import json
import urllib.request
from typing import Optional, Dict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

KNOWN_NETWORKS = {
    "8.8.8.8": ("US", "Google LLC"),
    "8.8.4.4": ("US", "Google LLC"),
    "1.1.1.1": ("US", "Cloudflare, Inc."),
    "1.0.0.1": ("US", "Cloudflare, Inc."),
    "9.9.9.9": ("US", "Quad9"),
    "208.67.222.222": ("US", "Cisco OpenDNS"),
}

@dataclass
class GeoLocation:
    country_code: str = ""
    org: str = ""

    def summary(self) -> str:
        if self.country_code and self.org:
            return f"[{self.country_code}] {self.org}"
        elif self.country_code:
            return f"[{self.country_code}]"
        return ""


class AsyncGeoIPResolver:
    """Non-blocking GeoIP and ASN metadata resolver with in-memory LRU caching."""

    def __init__(self, max_workers: int = 4, max_cache: int = 2048):
        self._cache: Dict[str, Optional[GeoLocation]] = {}
        self._pending = set()
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="netlog-geoip")
        self._max_cache = max_cache

    @staticmethod
    def is_public_ip(ip_str: Optional[str]) -> bool:
        if not ip_str or ip_str in ("*", "0.0.0.0", "::", "127.0.0.1", "::1"):
            return False
        try:
            ip = ipaddress.ip_address(ip_str)
            return not (ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_multicast or ip.is_link_local)
        except ValueError:
            return False

    def _fetch_geoip(self, ip_str: str) -> Optional[GeoLocation]:
        if ip_str in KNOWN_NETWORKS:
            code, org = KNOWN_NETWORKS[ip_str]
            return GeoLocation(country_code=code, org=org)

        try:
            # Query lightweight public endpoint with strict 1s timeout
            url = f"http://ip-api.com/json/{ip_str}?fields=countryCode,org"
            req = urllib.request.Request(url, headers={"User-Agent": "netlog-cli/0.1"})
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    return GeoLocation(
                        country_code=data.get("countryCode", ""),
                        org=data.get("org", "")
                    )
        except Exception:
            pass
        return GeoLocation()

    def _on_resolved(self, ip_str: str, future):
        try:
            res = future.result()
            self._cache[ip_str] = res
        except Exception:
            self._cache[ip_str] = GeoLocation()
        finally:
            self._pending.discard(ip_str)

    def lookup(self, ip_str: Optional[str]) -> Optional[GeoLocation]:
        """Look up GeoIP info synchronously from cache or schedule background query."""
        if not ip_str or not self.is_public_ip(ip_str):
            return None

        if ip_str in self._cache:
            return self._cache[ip_str]

        if ip_str not in self._pending:
            if len(self._cache) >= self._max_cache:
                self._cache.clear()
            self._pending.add(ip_str)
            future = self._executor.submit(self._fetch_geoip, ip_str)
            future.add_done_callback(lambda f: self._on_resolved(ip_str, f))

        return None

    def shutdown(self):
        self._executor.shutdown(wait=False)
