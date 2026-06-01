"""Add, read, and delete cookies for the current site."""

import argparse

from _common import add_browser_args, create_client, parse_with, safe_delete_and_close


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Demonstrate cookie APIs.")
    add_browser_args(parser)
    parser.add_argument("--cookie-name", default="autowk_example", help="Cookie name.")
    parser.add_argument("--cookie-value", default="ok", help="Cookie value.")
    return parse_with(parser, argv)


def run(client, args):
    client.create_session()
    try:
        client.navigate(args.url)
        client.document_onload()

        cookie = {"name": args.cookie_name, "value": args.cookie_value, "path": "/"}
        client.add_cookie(cookie)
        print("Added cookie:", cookie)
        print("All cookies:", client.get_all_cookies())
        print("Named cookie:", client.get_cookie_by_name(args.cookie_name))

        client.delete_cookie(args.cookie_name)
        print("Deleted named cookie:", args.cookie_name)
        client.delete_all_cookies()
        print("Deleted all cookies")
    finally:
        safe_delete_and_close(client)


def main(argv=None):
    args = parse_args(argv)
    run(create_client(args), args)


if __name__ == "__main__":
    main()
