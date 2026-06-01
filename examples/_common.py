import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from autowk import AutoWK


DEFAULT_URL = "https://xjbedu.site/"


def fixture_url(filename):
    return (FIXTURES_DIR / filename).resolve().as_uri()


def add_browser_args(parser, default_url=DEFAULT_URL):
    parser.add_argument("--url", default=default_url, help="URL to open.")
    return parser


def add_keep_open_arg(parser):
    parser.add_argument("--keep-open", action="store_true", help="Keep the browser open until Ctrl+C.")
    return parser


def create_client(args):
    return AutoWK()


def create_options_client(args):
    return AutoWK(fpfile=str(args.fpfile) if args.fpfile else "")


def wait_if_requested(keep_open):
    if not keep_open:
        return

    import time

    print("Browser is open. Press Ctrl+C to close it.")
    while True:
        time.sleep(1)


def safe_delete_and_close(client):
    try:
        client.delete_session()
    finally:
        client.close()


def parse_with(parser, argv=None):
    return parser.parse_args(argv)
