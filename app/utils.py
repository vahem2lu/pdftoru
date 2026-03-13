import os
import ipaddress
from fastapi import HTTPException, Request
from app.app_config import MAX_UPLOAD_SIZE_MB

# ---------------------------
# Utility functions
# ---------------------------
"""

def get_client_ip(request: Request, trusted_proxies: list[str] | None = None) -> str:
    client_ip = request.client.host
    trusted_networks = []

    if trusted_proxies:
        for ip in trusted_proxies:
            try:
                # Support both single IPs and CIDR ranges
                net = ipaddress.ip_network(ip)
                trusted_networks.append(net)
            except ValueError:
                continue  # skip invalid entries

    def is_trusted(ip_str: str) -> bool:
        try:
            ip_obj = ipaddress.ip_address(ip_str)
        except ValueError:
            return False
        return any(ip_obj in net for net in trusted_networks)

    # 1️⃣ Check X-Forwarded-For header
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        for ip_str in map(str.strip, x_forwarded_for.split(",")):
            if not is_trusted(ip_str):
                return ip_str

    # 2️⃣ Fallback: X-Real-IP header
    x_real_ip = request.headers.get("x-real-ip")
    if x_real_ip and not is_trusted(x_real_ip):
        return x_real_ip

    # 3️⃣ Fallback: direct TCP connection
    return client_ip

"""

def get_client_ip(request: Request, trusted_proxies: set | None = None) -> str:
    client_ip = request.client.host

    # Default: no trusted proxies → use only direct connection
    if not trusted_proxies:
        return client_ip

    # Check X-Forwarded-For header
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        # List of IPs in chain, leftmost = original client
        for ip in map(str.strip, x_forwarded_for.split(",")):
            # Ignore proxy IPs unless they are trusted
            if ip not in trusted_proxies:
                return ip

    # Fallback to X-Real-IP header
    x_real_ip = request.headers.get("x-real-ip")
    if x_real_ip and x_real_ip not in trusted_proxies:
        return x_real_ip

    # Fallback to direct TCP connection
    return client_ip


def validate_file_size(contents: bytes):
    max_bytes = MAX_UPLOAD_SIZE_MB * 1024 * 1024
    size_mb = len(contents) / (1024 * 1024)

    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large: {size_mb:.2f} MB. Max size is {MAX_UPLOAD_SIZE_MB} MB"
        )