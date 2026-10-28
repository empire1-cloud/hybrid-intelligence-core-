"""Outbound URL checks for server-side fetches (SSRF defence).

Limitation, stated plainly: the check resolves the hostname before the fetch,
and the HTTP client resolves it again. A DNS-rebinding attacker controlling the
domain's resolver could return a public address to this check and a private
one to the client. Closing that fully requires pinning the resolved IP into
the connection; this module removes the trivial cases (literal internal IPs,
localhost, internal hostnames, metadata endpoints).
"""

import ipaddress
import os
import socket
from urllib.parse import urlsplit


class UnsafeURLError(ValueError):
    """The URL must not be fetched server-side."""


def _host_allowlist():
    raw = os.environ.get("SPRITE_PROXY_ALLOWED_HOSTS", "")
    return {h.strip().lower() for h in raw.split(",") if h.strip()}


def _is_public_ip(ip: ipaddress._BaseAddress) -> bool:
    return not (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
        or (isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped and not _is_public_ip(ip.ipv4_mapped))
    )


def assert_public_https_url(url: str) -> None:
    parts = urlsplit(url or "")
    if parts.scheme != "https":
        raise UnsafeURLError("Only HTTPS URLs allowed")
    if parts.username or parts.password:
        raise UnsafeURLError("Credentials in URL are not allowed")

    host = (parts.hostname or "").lower()
    if not host:
        raise UnsafeURLError("URL has no host")

    allowlist = _host_allowlist()
    if allowlist and host not in allowlist:
        raise UnsafeURLError("Host is not on the allowed list")

    if host == "localhost" or host.endswith((".localhost", ".local", ".internal")):
        raise UnsafeURLError("Internal hosts are not allowed")

    try:
        literal = ipaddress.ip_address(host)
    except ValueError:
        literal = None

    if literal is not None:
        addresses = [literal]
    else:
        try:
            infos = socket.getaddrinfo(host, parts.port or 443, proto=socket.IPPROTO_TCP)
        except socket.gaierror:
            raise UnsafeURLError("Host could not be resolved")
        addresses = [ipaddress.ip_address(info[4][0]) for info in infos]

    if not addresses or not all(_is_public_ip(ip) for ip in addresses):
        raise UnsafeURLError("Host resolves to a non-public address")
