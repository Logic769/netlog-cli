import pytest
from netlog.core.models import ConnectionInfo
from netlog.ui.dashboard import create_connections_table
from netlog.core.resolver import AsyncDNSResolver

def test_sorting_connections():
    c1 = ConnectionInfo(fd=1, family="AF_INET", proto="TCP", laddr="127.0.0.1", lport=8080, raddr=None, rport=None, status="LISTEN", pid=200, process_name="zed", user="test")
    c2 = ConnectionInfo(fd=2, family="AF_INET", proto="TCP", laddr="127.0.0.1", lport=5000, raddr=None, rport=None, status="ESTABLISHED", pid=100, process_name="alpha", user="test")

    resolver = AsyncDNSResolver()
    
    # Test sort by PID
    table_pid = create_connections_table([c1, c2], resolver, sort_by="pid")
    assert table_pid is not None

    # Test sort by process name
    table_proc = create_connections_table([c1, c2], resolver, sort_by="process")
    assert table_proc is not None

    resolver.shutdown()
