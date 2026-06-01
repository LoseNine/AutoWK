"""Run JavaScript and pass element arguments."""

import argparse

from _common import add_browser_args, create_client, parse_with, safe_delete_and_close


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Demonstrate execute_script().")
    add_browser_args(parser)
    parser.add_argument("--selector", default="body", help="Element selector passed to JavaScript.")
    return parse_with(parser, argv)


def run(client, args):
    client.create_session()
    try:
        client.navigate(args.url)
        client.document_onload()

        ready_state = client.execute_script("return document.readyState;")
        user_agent = client.get_useragent()
        element = client.find_element_by_css_selector(args.selector)
        result = client.execute_script(
            "return arguments[0].getAttribute('data-autowk-example') || arguments[0].tagName;",
            [{"element-6066-11e4-a52e-4f735466cecf": element.element_id}],
        )

        print("Ready state:", ready_state)
        print("User agent:", user_agent)
        print("Element script result:", result)
    finally:
        safe_delete_and_close(client)


def main(argv=None):
    args = parse_args(argv)
    run(create_client(args), args)


if __name__ == "__main__":
    main()
