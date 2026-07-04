"""
BuzzosaurusServer - Network discovery (mDNS / zeroconf)
-------------------------------------------------------

Optional helpers so players' phones can find the host's server automatically
on the local network, instead of typing an IP address by hand.
"""
import socket
import time

from zeroconf import ServiceInfo, Zeroconf, ServiceBrowser

SERVICE_TYPE = "_Buzzosaurus._tcp.local."


def get_local_ip() -> str:
    """Best-effort way to find this machine's LAN IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def advertise(server_name: str, port: int) -> tuple[Zeroconf, ServiceInfo]:
    """Register this server on the local network via mDNS.

    Keep the returned (zeroconf, info) objects alive for as long as the
    server runs, and call zeroconf.unregister_service(info) on shutdown.
    """
    zc = Zeroconf()
    ip = get_local_ip()
    info = ServiceInfo(
        SERVICE_TYPE,
        f"{server_name}.{SERVICE_TYPE}",
        addresses=[socket.inet_aton(ip)],
        port=port,
        properties={},
    )
    zc.register_service(info)
    return zc, info


class _Listener:
    def __init__(self):
        self.found: dict[str, tuple[str, int]] = {}

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info = zc.get_service_info(type_, name)
        if info and info.addresses:
            ip = socket.inet_ntoa(info.addresses[0])
            self.found[name] = (ip, info.port)

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        self.found.pop(name, None)

    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        pass


def discover(timeout: float = 3.0) -> dict[str, tuple[str, int]]:
    """Scan the local network for BuzzosaurusServer servers for `timeout` seconds.

    Returns a dict of {service_name: (ip, port)}.
    """
    zc = Zeroconf()
    listener = _Listener()
    ServiceBrowser(zc, SERVICE_TYPE, listener)
    time.sleep(timeout)
    zc.close()
    return listener.found
