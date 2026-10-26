import pytest
from netlog.core.models import ConnectionInfo, ProcessNetworkStats

def test_connection_info_endpoints():
    conn = ConnectionInfo(
        fd=5,
        family="IPv4",
        proto="TCP",
        laddr="127.0.0.1",
        lport=8080,
        raddr="93.184.216.34",
        rport=443,
        status="ESTABLISHED",
        pid=1234,
        process_name="curl",
        user="testuser"
    )
    assert conn.local_endpoint == "127.0.0.1:8080"
    assert conn.remote_endpoint == "93.184.216.34:443"

def test_connection_info_stateless_endpoint():
    conn = ConnectionInfo(
        fd=6,
        family="IPv4",
        proto="UDP",
        laddr="0.0.0.0",
        lport=5353,
        raddr=None,
        rport=None,
        status="STATELESS",
        pid=555,
        process_name="avahi",
        user="avahi"
    )
    assert conn.remote_endpoint == "*:*"
