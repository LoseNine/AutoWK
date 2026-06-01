"""Switch into an iframe and back to the top page."""

import argparse

from _common import add_browser_args, create_client, fixture_url, parse_with, safe_delete_and_close


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Demonstrate iframe switching.")
    add_browser_args(parser, default_url=fixture_url("frames.html"))
    parser.add_argument("--frame-selector", default="#example-frame", help="Iframe CSS selector.")
    parser.add_argument("--inside-selector", default="#inside-frame", help="Selector to find inside the frame.")
    return parse_with(parser, argv)


def run(client, args):
    client.create_session()
    try:
        client.navigate(args.url)
        client.document_onload()

        iframe = client.find_element_by_css_selector(args.frame_selector)
        client.switch_to_frame(iframe)
        inside = client.find_element_by_css_selector(args.inside_selector)
        print("Inside frame element:", inside)

        client.switch_to_parent_frame()
        client.switch_to_frame(None)
        print("Returned to top frame")
    finally:
        safe_delete_and_close(client)


def main(argv=None):
    args = parse_args(argv)
    run(create_client(args), args)


if __name__ == "__main__":
    main()
