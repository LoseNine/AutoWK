"""Read the current page user agent."""

import argparse

from _common import add_browser_args, create_client, fixture_url, parse_with, safe_delete_and_close


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Demonstrate get_useragent().")
    add_browser_args(parser, default_url=fixture_url("page_state.html"))
    return parse_with(parser, argv)


def run(client, args):
    client.create_session()
    try:
        client.navigate(args.url)
        client.document_onload()
        print("User agent:", client.get_useragent())
    finally:
        safe_delete_and_close(client)


def main(argv=None):
    args = parse_args(argv)
    run(create_client(args), args)


if __name__ == "__main__":
    main()
