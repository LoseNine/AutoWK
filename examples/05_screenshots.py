"""Capture full-page and element screenshots."""

import argparse
from pathlib import Path

from _common import add_browser_args, create_client, parse_with, safe_delete_and_close


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Save page and element screenshots.")
    add_browser_args(parser)
    parser.add_argument("--selector", default="body", help="Element selector for element screenshot.")
    parser.add_argument("--output-dir", default="examples_output", help="Directory for screenshots.")
    return parse_with(parser, argv)


def run(client, args):
    client.create_session()
    try:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        client.navigate(args.url)
        client.document_onload()

        page_png = output_dir / "page.png"
        element_png = output_dir / "element.png"
        client.take_screenshot(str(page_png))
        client.find_element_by_css_selector(args.selector).take_element_screenshot(str(element_png))

        print("Page screenshot:", page_png)
        print("Element screenshot:", element_png)
    finally:
        safe_delete_and_close(client)


def main(argv=None):
    args = parse_args(argv)
    run(create_client(args), args)


if __name__ == "__main__":
    main()
