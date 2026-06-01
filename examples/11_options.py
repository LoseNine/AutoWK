"""Launch AutoWK with a MiniBrowser fpfile."""

import argparse
from pathlib import Path

from _common import DEFAULT_URL, add_keep_open_arg, create_options_client, parse_with, safe_delete_and_close, wait_if_requested


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Demonstrate MiniBrowser fpfile startup configuration.")
    parser.add_argument("--url", default=DEFAULT_URL, help="URL to open.")
    parser.add_argument("--fpfile", type=Path, default=None, help="MiniBrowser fpfile path.")
    add_keep_open_arg(parser)
    return parse_with(parser, argv)


def run(client, args):
    client.create_session()
    try:
        client.navigate(args.url)
        client.document_onload()
        print("Window rect:", client.get_window_rect())
        print("User agent:", client.get_useragent())
        print("fpfile:", args.fpfile or "<none>")
        wait_if_requested(args.keep_open)
    finally:
        safe_delete_and_close(client)


def main(argv=None):
    args = parse_args(argv)
    run(create_options_client(args), args)


if __name__ == "__main__":
    main()
