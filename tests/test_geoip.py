import pytest
from netlog.core.geoip import AsyncGeoIPResolver, GeoLocation

def test_geoip_is_public_ip():
    assert not AsyncGeoIPResolver.is_public_ip("127.0.0.1")
    assert not AsyncGeoIPResolver.is_public_ip("192.168.1.1")
    assert not AsyncGeoIPResolver.is_public_ip("10.0.0.5")
    assert not AsyncGeoIPResolver.is_public_ip("172.16.0.1")
    assert not AsyncGeoIPResolver.is_public_ip("*")
    assert not AsyncGeoIPResolver.is_public_ip(None)
    
    assert AsyncGeoIPResolver.is_public_ip("8.8.8.8")
    assert AsyncGeoIPResolver.is_public_ip("1.1.1.1")

def test_geoip_known_networks():
    resolver = AsyncGeoIPResolver()
    
    # 8.8.8.8 is in known networks, resolved directly or scheduled
    loc = resolver._fetch_geoip("8.8.8.8")
    assert loc is not None
    assert loc.country_code == "US"
    assert "Google" in loc.org
    assert loc.summary() == "[US] Google LLC"

    resolver.shutdown()
