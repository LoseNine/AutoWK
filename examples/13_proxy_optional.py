"""Optional proxy configuration through a MiniBrowser fpfile."""

import argparse

from _common import DEFAULT_URL, parse_with, safe_delete_and_close


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Launch AutoWK with an fpfile that can contain proxy keys.")
    parser.add_argument("--url", default=DEFAULT_URL, help="URL to open.")
    parser.add_argument("--fpfile", default="", help="fpfile path with proxy=http://host:port entries.")
    return parse_with(parser, argv)


def create_proxy_client(args):
    from autowk import AutoWK

    return AutoWK(fpfile=args.fpfile)


def run(client, args):
    client.create_session()
    try:
        client.navigate(args.url)
        client.document_onload()
        print("fpfile:", args.fpfile or "<none>")
        print("Current URL:", client.get_current_url())
    finally:
        safe_delete_and_close(client)


def main(argv=None):
    args = parse_args(argv)
    run(create_proxy_client(args), args)


if __name__ == "__main__":
    main()
