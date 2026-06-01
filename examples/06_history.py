"""Use browser history: back, forward, and refresh."""

import argparse

from _common import add_browser_args, create_client, parse_with, safe_delete_and_close


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Navigate between two pages and use history APIs.")
    add_browser_args(parser)
    parser.add_argument("--second-url", default="https://example.com/", help="Second URL to open.")
    return parse_with(parser, argv)


def run(client, args):
    client.create_session()
    try:
        client.navigate(args.url)
        client.document_onload()
        print("First page:", client.get_current_url())

        client.navigate(args.second_url)
        client.document_onload()
        print("Second page:", client.get_current_url())

        client.back()
        client.document_onload()
        print("After back:", client.get_current_url())

        client.forward()
        client.document_onload()
        print("After forward:", client.get_current_url())

        client.refresh()
        client.document_onload()
        print("After refresh title:", client.get_title())
    finally:
        safe_delete_and_close(client)


def main(argv=None):
    args = parse_args(argv)
    run(create_client(args), args)


if __name__ == "__main__":
    main()
