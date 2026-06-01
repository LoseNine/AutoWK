"""Clear, type into, and click page elements."""

import argparse

from _common import add_browser_args, create_client, fixture_url, parse_with, safe_delete_and_close


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Demonstrate element clear/input/click.")
    add_browser_args(parser, default_url=fixture_url("input_and_click.html"))
    parser.add_argument("--input-selector", default="#example-input", help="Input CSS selector.")
    parser.add_argument("--button-selector", default="#example-button", help="Clickable CSS selector.")
    parser.add_argument("--text", default="AutoWK example text", help="Text to type.")
    return parse_with(parser, argv)


def run(client, args):
    client.create_session()
    try:
        client.navigate(args.url)
        client.document_onload()

        input_element = client.find_element_by_css_selector(args.input_selector)
        input_element.clear()
        input_element.input(args.text)
        print("Typed text into:", args.input_selector)

        button = client.find_element_by_css_selector(args.button_selector)
        button.click()
        print("Clicked:", args.button_selector)
    finally:
        safe_delete_and_close(client)


def main(argv=None):
    args = parse_args(argv)
    run(create_client(args), args)


if __name__ == "__main__":
    main()
