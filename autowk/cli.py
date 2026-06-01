import argparse
import platform
import socket
import sys
from pathlib import Path

from . import __version__
from .AutoWKBase import get_bin_file_path


def _port_available(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex((host, port)) != 0


def print_paths():
    print(f"autowk {__version__}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Platform: {platform.platform()}")
    print(f"Package: {Path(__file__).resolve().parent}")
    print(f"MiniBrowser.exe: {get_bin_file_path('MiniBrowser.exe')}")
    print(f"WebDriver.exe: {get_bin_file_path('WebDriver.exe')}")


def doctor():
    print_paths()
    checks = [
        ("MiniBrowser.exe exists", Path(get_bin_file_path("MiniBrowser.exe")).exists()),
        ("WebDriver.exe exists", Path(get_bin_file_path("WebDriver.exe")).exists()),
        ("Default WebDriver port 12345 available", _port_available("127.0.0.1", 12345)),
        ("Default inspector port 12346 available", _port_available("127.0.0.1", 12346)),
    ]
    failed = False
    for label, ok in checks:
        status = "OK" if ok else "FAIL"
        print(f"{status}: {label}")
        failed = failed or not ok
    return 1 if failed else 0


def build_parser():
    parser = argparse.ArgumentParser(prog="autowk", description="AutoWK helper commands")
    parser.add_argument("--version", action="version", version=f"autowk {__version__}")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("doctor", help="check installation, binaries, and default ports")
    subparsers.add_parser("paths", help="print package and browser binary paths")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "doctor":
        return doctor()
    if args.command == "paths" or args.command is None:
        print_paths()
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
