from netlog.core.resolver import AsyncDNSResolver
from netlog.core.anomaly import AnomalyDetector
from netlog.core.models import ConnectionInfo, ProcessNetworkStats

def test_async_dns_local_ips():
    resolver = AsyncDNSResolver()
    assert resolver.resolve("127.0.0.1") == "localhost"
    assert resolver.resolve("192.168.1.1") == "lan"
    assert resolver.resolve("10.0.0.5") == "lan"
    assert resolver.resolve(None) == "*:*"
    resolver.shutdown()

def test_anomaly_detection_telnet_port():
    detector = AnomalyDetector()
    conn = ConnectionInfo(
        fd=10,
        family="IPv4",
        proto="TCP",
        laddr="192.168.1.10",
        lport=45000,
        raddr="45.33.32.156",
        rport=23,  # Telnet
        status="ESTABLISHED",
        pid=999,
        process_name="legacy_app",
        user="root"
    )
    detector.inspect_connections([conn], {})
    assert conn.is_suspicious is True
    assert "Insecure Telnet" in conn.anomaly_reason
