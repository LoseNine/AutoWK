"""Read and update element text, attributes, geometry, and visibility."""

import argparse

from _common import add_browser_args, create_client, fixture_url, parse_with, safe_delete_and_close


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Read element text, attributes, rect, and display state.")
    add_browser_args(parser, default_url=fixture_url("page_state.html"))
    parser.add_argument("--selector", default="#state-root", help="CSS selector to inspect.")
    return parse_with(parser, argv)


def run(client, args):
    client.create_session()
    try:
        client.navigate(args.url)
        client.document_onload()

        element = client.find_element_by_css_selector(args.selector)
        print("Text:", element.get_text())
        print("Text property:", element.text)
        print("Class attribute:", element.get_attribute("class"))
        print("Rect:", element.get_rect())
        print("Displayed:", element.is_displayed())

        element.set_attribute("data-autowk-example", "text-and-attributes")
        print("Updated data attribute:", element.get_attribute("data-autowk-example"))
    finally:
        safe_delete_and_close(client)


def main(argv=None):
    args = parse_args(argv)
    run(create_client(args), args)


if __name__ == "__main__":
    main()
