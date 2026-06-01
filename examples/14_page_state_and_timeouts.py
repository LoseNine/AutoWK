"""Read page state and configure WebDriver timeouts."""

import argparse

from _common import add_browser_args, create_client, fixture_url, parse_with, safe_delete_and_close


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Demonstrate status, timeouts, page source, and page state APIs.")
    add_browser_args(parser, default_url=fixture_url("page_state.html"))
    parser.add_argument("--implicit-timeout", type=int, default=0, help="Implicit wait timeout in milliseconds.")
    parser.add_argument("--page-load-timeout", type=int, default=30000, help="Page load timeout in milliseconds.")
    parser.add_argument("--script-timeout", type=int, default=30000, help="Script timeout in milliseconds.")
    return parse_with(parser, argv)


def run(client, args):
    client.create_session()
    try:
        print("Status:", client.status())
        print("Initial timeouts:", client.get_timeouts())
        client.set_timeouts(
            {
                "implicit": args.implicit_timeout,
                "pageLoad": args.page_load_timeout,
                "script": args.script_timeout,
            }
        )
        print("Updated timeouts:", client.get_timeouts())

        client.navigate(args.url)
        client.document_onload()
        print("Title:", client.get_title())
        print("Current URL:", client.get_current_url())
        print("Page source length:", len(client.get_page_source()))
        print("Ready state:", client.execute_script("return document.readyState;"))
    finally:
        safe_delete_and_close(client)


def main(argv=None):
    args = parse_args(argv)
    run(create_client(args), args)


if __name__ == "__main__":
    main()
