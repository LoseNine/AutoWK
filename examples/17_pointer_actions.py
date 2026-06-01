"""Use coordinate clicks and drag helpers."""

import argparse

from _common import add_browser_args, create_client, fixture_url, parse_with, safe_delete_and_close


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Demonstrate coordinate and element drag action helpers.")
    add_browser_args(parser, default_url=fixture_url("waits_nested_pointer.html"))
    parser.add_argument("--selector", default="#drag-target", help="Element selector for element drag examples.")
    parser.add_argument("--start-x", type=int, default=100, help="Drag start X coordinate.")
    parser.add_argument("--start-y", type=int, default=100, help="Drag start Y coordinate.")
    parser.add_argument("--end-x", type=int, default=240, help="Drag end X coordinate.")
    parser.add_argument("--end-y", type=int, default=100, help="Drag end Y coordinate.")
    parser.add_argument("--offset-x", type=int, default=40, help="Element drag X offset.")
    parser.add_argument("--offset-y", type=int, default=0, help="Element drag Y offset.")
    parser.add_argument("--steps", type=int, default=8, help="Humanized drag step count.")
    return parse_with(parser, argv)


def run(client, args):
    client.create_session()
    try:
        client.navigate(args.url)
        client.document_onload()

        target = client.find_element_by_css_selector(args.selector)
        client.click_pos_by_win(args.start_x, args.start_y)
        client.click_pos_by_js(args.start_x, args.start_y)
        client.drag_and_drop_pos(args.start_x, args.start_y, args.end_x, args.end_y)
        client.drag_and_drop_pos_human(args.start_x, args.start_y, args.end_x, args.end_y, num_steps=args.steps)
        target.drag_element_by_offset_line(args.offset_x, args.offset_y)
        target.drag_element_by_offset_human(args.offset_x, args.offset_y, num_steps=args.steps)

        print("Ran pointer examples against:", args.selector)
    finally:
        safe_delete_and_close(client)


def main(argv=None):
    args = parse_args(argv)
    run(create_client(args), args)


if __name__ == "__main__":
    main()
