"""Wait for elements and search within an element."""

import argparse

from _common import add_browser_args, create_client, fixture_url, parse_with, safe_delete_and_close


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Demonstrate wait helpers and nested element lookup.")
    add_browser_args(parser, default_url=fixture_url("waits_nested_pointer.html"))
    parser.add_argument("--container-selector", default="#container", help="Container CSS selector.")
    parser.add_argument("--child-selector", default=".message", help="Child CSS selector within the container.")
    parser.add_argument("--xpath", default="//*[@id='nested-button']", help="XPath selector to wait for.")
    parser.add_argument("--timeout", type=float, default=5.0, help="Wait timeout in seconds.")
    return parse_with(parser, argv)


def run(client, args):
    client.create_session()
    try:
        client.navigate(args.url)
        client.document_onload()

        waited_css = client.wait_for_element_by_css_selector(args.container_selector, timeout=args.timeout)
        waited_xpath = client.wait_for_element_by_xpath(args.xpath, timeout=args.timeout)
        generic_wait = client.wait_for_element("css selector", args.child_selector, timeout=args.timeout)
        nested_one = waited_css.find_element_by_css_selector(args.child_selector)
        nested_many = waited_css.find_elements_by_css_selector(args.child_selector)
        nested_xpath = waited_css.find_element_by_xpath(".//*[@id='nested-button']")
        nested_xpath_many = waited_css.find_elements_by_xpath(".//*[@id='nested-button']")

        print("Waited CSS element:", waited_css)
        print("Waited XPath element:", waited_xpath)
        print("Generic wait element:", generic_wait)
        print("Nested element text:", nested_one.get_text())
        print("Nested CSS count:", len(nested_many))
        print("Nested XPath element:", nested_xpath)
        print("Nested XPath count:", len(nested_xpath_many))
    finally:
        safe_delete_and_close(client)


def main(argv=None):
    args = parse_args(argv)
    run(create_client(args), args)


if __name__ == "__main__":
    main()
