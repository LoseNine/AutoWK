"""Open a page and print its title and final URL."""

import argparse

from _common import add_browser_args, add_keep_open_arg, create_client, parse_with, safe_delete_and_close, wait_if_requested


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Navigate to a page and print title/current URL.")
    add_browser_args(parser)
    add_keep_open_arg(parser)
    return parse_with(parser, argv)


def run(client, args):
    client.create_session()
    try:
        client.navigate(args.url)
        client.document_onload()
        print("Title:", client.get_title())
        print("Current URL:", client.get_current_url())
        wait_if_requested(args.keep_open)
    finally:
        safe_delete_and_close(client)


def main(argv=None):
    args = parse_args(argv)
    run(create_client(args), args)


if __name__ == "__main__":
    main()
