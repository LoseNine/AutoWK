"""Use a SOCKS password proxy through a MiniBrowser fpfile."""

import argparse
import json
import sys
import tempfile
import time
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit, urlunsplit

from _common import add_keep_open_arg, parse_with, safe_delete_and_close


DEFAULT_URL = "http://lumtest.com/myip.json"
DEFAULT_FPFILE = Path("C:/safari/fp.txt")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Launch AutoWK with a SOCKS password proxy.")
    parser.add_argument("--url", default=DEFAULT_URL, help="URL used to verify the proxy exit.")
    parser.add_argument("--mode", choices=("fpfile", "args"), default="fpfile", help="Read an fpfile directly or build one from proxy args.")
    parser.add_argument("--fpfile", type=Path, default=DEFAULT_FPFILE, help="MiniBrowser fpfile path.")
    parser.add_argument("--scheme", default="socks5h", choices=("socks5h", "socks5"), help="SOCKS proxy scheme.")
    parser.add_argument("--proxy", default="", help="host:port:username:password or socks5h://username:password@host:port.")
    parser.add_argument("--proxy-host", default="", help="Proxy host for --mode args.")
    parser.add_argument("--proxy-port", default="", help="Proxy port for --mode args.")
    parser.add_argument("--proxy-username", default="", help="Proxy username for --mode args.")
    parser.add_argument("--proxy-password", default="", help="Proxy password for --mode args.")
    parser.add_argument("--port", type=int, default=12345, help="WebDriver port used by AutoWK.")
    parser.add_argument("--timeout", type=float, default=45.0, help="Seconds to wait for a verification response.")
    add_keep_open_arg(parser)
    return parse_with(parser, argv)


def build_socks_proxy_url(args):
    if args.proxy:
        proxy = args.proxy.strip()
        if "://" in proxy:
            return proxy
        parts = proxy.rsplit(":", 3)
        if len(parts) != 4:
            raise ValueError("--proxy must be host:port:username:password")
        host, port, username, password = parts
    else:
        host = args.proxy_host.strip()
        port = str(args.proxy_port).strip()
        username = args.proxy_username
        password = args.proxy_password
        if not all((host, port, username, password)):
            raise ValueError("--mode args requires --proxy or all proxy host/port/username/password fields")

    return f"{args.scheme}://{quote(username, safe='')}:{quote(password, safe='')}@{host}:{port}"


def redact_proxy_url(proxy_url):
    parts = urlsplit(proxy_url)
    if not parts.username:
        return proxy_url

    username = unquote(parts.username)
    host = parts.hostname or ""
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    if parts.port:
        host = f"{host}:{parts.port}"
    netloc = f"{username}:<redacted>@{host}"
    return urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))


def console_safe_text(text, encoding=None):
    encoding = encoding or getattr(sys.stdout, "encoding", None) or "utf-8"
    return str(text).encode(encoding, errors="backslashreplace").decode(encoding, errors="replace")


def write_proxy_fpfile(base_fpfile, proxy_url):
    prefix = ""
    base_path = Path(base_fpfile) if base_fpfile else None
    if base_path and base_path.exists():
        prefix = base_path.read_text(encoding="utf-8", errors="replace").rstrip() + "\n\n"

    fp = tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8", prefix="autowk_socks_proxy_", suffix=".txt")
    try:
        fp.write(prefix)
        fp.write("# Temporary SOCKS password proxy override for MiniBrowser.\n")
        fp.write("proxy_type=socks5h\n")
        fp.write(f"http_proxy={proxy_url}\n")
        return Path(fp.name)
    finally:
        fp.close()


def create_proxy_client(args):
    from autowk import AutoWK

    if args.mode == "fpfile":
        return AutoWK(port=args.port, fpfile=str(args.fpfile) if args.fpfile else "")

    proxy_url = build_socks_proxy_url(args)
    args._generated_fpfile = write_proxy_fpfile(args.fpfile, proxy_url)
    args._proxy_url = proxy_url
    return AutoWK(port=args.port, fpfile=str(args._generated_fpfile))


def wait_for_body_text(client, timeout):
    deadline = time.time() + timeout
    last_text = ""
    while time.time() < deadline:
        ready = client.execute_script("return document.readyState")
        last_text = client.execute_script("return document.body ? document.body.innerText : ''") or ""
        if ready == "complete" and last_text.strip():
            return last_text.strip()
        time.sleep(1)
    return last_text.strip()


def print_proxy_result(text):
    print("Response:", console_safe_text(text[:1000]))
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return

    asn = data.get("asn") or {}
    geo = data.get("geo") or {}
    print("Country:", data.get("country", ""))
    print("ASN:", asn.get("org_name", ""))
    print("Region:", geo.get("region", ""))
    print("City:", geo.get("city", ""))


def run(client, args):
    generated_fpfile = getattr(args, "_generated_fpfile", None)
    try:
        client.create_session()
        try:
            client.navigate(args.url)
            text = wait_for_body_text(client, args.timeout)
            print("URL:", args.url)
            print("Mode:", args.mode)
            print("fpfile:", generated_fpfile or args.fpfile)
            proxy_url = getattr(args, "_proxy_url", "")
            if proxy_url:
                print("Proxy:", redact_proxy_url(proxy_url))
            print_proxy_result(text)
            return text
        finally:
            safe_delete_and_close(client)
    finally:
        if generated_fpfile:
            generated_fpfile.unlink(missing_ok=True)


def main(argv=None):
    args = parse_args(argv)
    run(create_proxy_client(args), args)


if __name__ == "__main__":
    main()
