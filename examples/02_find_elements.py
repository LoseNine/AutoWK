"""Find elements by CSS and XPath selectors."""

import argparse

from _common import add_browser_args, create_client, parse_with, safe_delete_and_close


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Find page elements with CSS and XPath.")
    add_browser_args(parser)
    parser.add_argument("--css", default="body", help="CSS selector to find.")
    parser.add_argument("--xpath", default="//body", help="XPath selector to find.")
    return parse_with(parser, argv)


def run(client, args):
    client.create_session()
    try:
        client.navigate(args.url)
        client.document_onload()

        css_element = client.find_element_by_css_selector(args.css)
        css_elements = client.find_elements_by_css_selector(args.css)
        xpath_element = client.find_element_by_xpath(args.xpath)
        xpath_elements = client.find_elements_by_xpath(args.xpath)
        waited = client.wait_for_element_by_css_selector(args.css, timeout=5)

        print("CSS element:", css_element)
        print("CSS count:", len(css_elements))
        print("XPath element:", xpath_element)
        print("XPath count:", len(xpath_elements))
        print("Waited element:", waited)
    finally:
        safe_delete_and_close(client)


def main(argv=None):
    args = parse_args(argv)
    run(create_client(args), args)


if __name__ == "__main__":
    main()
