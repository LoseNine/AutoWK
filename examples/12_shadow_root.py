"""Find elements inside an open shadow root."""

import argparse

from _common import add_browser_args, create_client, fixture_url, parse_with, safe_delete_and_close


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Demonstrate open shadow root traversal.")
    add_browser_args(parser, default_url=fixture_url("shadow_root.html"))
    parser.add_argument("--host-selector", default="[data-shadow-host]", help="Shadow host CSS selector.")
    parser.add_argument("--inside-selector", default="*", help="Selector inside the shadow root.")
    return parse_with(parser, argv)


def run(client, args):
    client.create_session()
    try:
        client.navigate(args.url)
        client.document_onload()

        host = client.find_element_by_css_selector(args.host_selector)
        shadow = host.get_open_shadow_root()
        first = shadow.find_element_by_css_selector(args.inside_selector)
        all_matches = shadow.find_elements_by_css_selector(args.inside_selector)

        print("First shadow element:", first)
        print("Shadow match count:", len(all_matches))
    finally:
        safe_delete_and_close(client)


def main(argv=None):
    args = parse_args(argv)
    run(create_client(args), args)


if __name__ == "__main__":
    main()
