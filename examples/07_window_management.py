"""Manage browser windows and tabs."""

import argparse

from _common import add_browser_args, create_client, parse_with, safe_delete_and_close


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Demonstrate window handles, tabs, and window rect APIs.")
    add_browser_args(parser)
    parser.add_argument("--new-window-type", default="tab", choices=["tab", "window"], help="Type passed to new_window().")
    parser.add_argument("--rect-width", type=int, default=1200, help="Width passed to set_window_rect().")
    parser.add_argument("--rect-height", type=int, default=800, help="Height passed to set_window_rect().")
    return parse_with(parser, argv)


def run(client, args):
    client.create_session()
    try:
        client.navigate(args.url)
        client.document_onload()

        original = client.get_window_handle()
        print("Original handle:", original)
        print("Handles:", client.get_window_handles())
        print("Initial rect:", client.get_window_rect())

        client.set_window_rect(x=80, y=80, width=args.rect_width, height=args.rect_height)
        print("Updated rect:", client.get_window_rect())
        client.maximize_window()
        print("Maximized rect:", client.get_window_rect())
        client.minimize_window()
        print("Minimized window")

        new_window = client.new_window(args.new_window_type)
        new_handle = new_window["value"]["handle"]
        client.switch_to_window(new_handle)
        print("New handle:", new_handle)
        print("Handles after new window:", client.get_window_handles())

        client.close_window()
        client.switch_to_window(original)
        print("Back to original:", client.get_window_handle())
    finally:
        safe_delete_and_close(client)


def main(argv=None):
    args = parse_args(argv)
    run(create_client(args), args)


if __name__ == "__main__":
    main()
