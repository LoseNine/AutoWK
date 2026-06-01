"""Access a closed shadow root exposed by the page for automation."""

import argparse

from _common import add_browser_args, create_client, fixture_url, parse_with, safe_delete_and_close


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Demonstrate get_closed_shadow_root() on a cooperating page.")
    add_browser_args(parser, default_url=fixture_url("closed_shadow_root.html"))
    parser.add_argument("--host-selector", default="#closed-shadow-host", help="Closed shadow host selector.")
    return parse_with(parser, argv)


def run(client, args):
    client.create_session()
    try:
        client.navigate(args.url)
        client.document_onload()
        shadow_root = client.get_closed_shadow_root(args.host_selector)
        print("Closed shadow root handle:", shadow_root)
    finally:
        safe_delete_and_close(client)


def main(argv=None):
    args = parse_args(argv)
    run(create_client(args), args)


if __name__ == "__main__":
    main()
