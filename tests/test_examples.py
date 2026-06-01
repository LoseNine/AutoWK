import importlib.util
import io
import py_compile
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"

EXPECTED_EXAMPLES = [
    "01_navigation.py",
    "02_find_elements.py",
    "03_text_and_attributes.py",
    "04_input_and_click.py",
    "05_screenshots.py",
    "06_history.py",
    "07_window_management.py",
    "08_frames.py",
    "09_cookies.py",
    "10_execute_script.py",
    "11_options.py",
    "12_shadow_root.py",
    "13_proxy_optional.py",
    "14_page_state_and_timeouts.py",
    "15_user_agent.py",
    "16_waits_and_nested_elements.py",
    "17_pointer_actions.py",
    "18_closed_shadow_root_optional.py",
    "19_fingerprint_profile.py",
    "20_socks_password_proxy.py",
]

COVERED_PUBLIC_APIS = [
    "add_cookie",
    "back",
    "clear",
    "click",
    "click_pos_by_js",
    "click_pos_by_win",
    "close_window",
    "delete_all_cookies",
    "delete_cookie",
    "document_onload",
    "drag_and_drop_pos",
    "drag_and_drop_pos_human",
    "drag_element_by_offset_human",
    "drag_element_by_offset_line",
    "execute_script",
    "find_element_by_css_selector",
    "find_element_by_xpath",
    "find_elements_by_css_selector",
    "find_elements_by_xpath",
    "forward",
    "get_all_cookies",
    "get_attribute",
    "get_closed_shadow_root",
    "get_cookie_by_name",
    "get_current_url",
    "get_open_shadow_root",
    "get_page_source",
    "get_rect",
    "get_text",
    "get_timeouts",
    "get_title",
    "get_useragent",
    "get_window_handle",
    "get_window_handles",
    "get_window_rect",
    "input",
    "is_displayed",
    "maximize_window",
    "minimize_window",
    "navigate",
    "new_window",
    "refresh",
    "set_attribute",
    "set_timeouts",
    "set_window_rect",
    "status",
    "switch_to_frame",
    "switch_to_parent_frame",
    "switch_to_window",
    "take_element_screenshot",
    "take_screenshot",
    "wait_for_element",
    "wait_for_element_by_css_selector",
    "wait_for_element_by_xpath",
]


class FakeElement:
    def __init__(self, client, element_id="element-id", text="Example text"):
        self.client = client
        self.element_id = element_id
        self.text = text

    def get_text(self):
        return self.text

    def get_attribute(self, name):
        return f"attr:{name}"

    def set_attribute(self, name, value):
        self.client.calls.append(("element.set_attribute", name, value))
        return self

    def get_rect(self):
        return {"x": 1, "y": 2, "width": 120, "height": 40}

    def is_displayed(self):
        return True

    def clear(self):
        self.client.calls.append(("element.clear", self.element_id))

    def input(self, text):
        self.client.calls.append(("element.input", text))

    def click(self):
        self.client.calls.append(("element.click", self.element_id))

    def take_element_screenshot(self, filename):
        Path(filename).write_bytes(b"fake element png")

    def find_element_by_css_selector(self, selector):
        self.client.calls.append(("element.find_css", selector))
        return FakeElement(self.client, "child-id", "Child text")

    def find_elements_by_css_selector(self, selector):
        self.client.calls.append(("element.find_all_css", selector))
        return [FakeElement(self.client, "child-1"), FakeElement(self.client, "child-2")]

    def find_element_by_xpath(self, selector):
        self.client.calls.append(("element.find_xpath", selector))
        return FakeElement(self.client, "child-xpath", "Child XPath text")

    def find_elements_by_xpath(self, selector):
        self.client.calls.append(("element.find_all_xpath", selector))
        return [FakeElement(self.client, "child-xpath-1"), FakeElement(self.client, "child-xpath-2")]

    def get_open_shadow_root(self):
        return FakeShadowRoot(self.client)

    def drag_element_by_offset_line(self, offset_x, offset_y):
        self.client.calls.append(("element.drag_line", offset_x, offset_y))

    def drag_element_by_offset_human(self, offset_x, offset_y, num_steps=30):
        self.client.calls.append(("element.drag_human", offset_x, offset_y, num_steps))


class FakeShadowRoot:
    def __init__(self, client):
        self.client = client

    def find_element_by_css_selector(self, selector):
        self.client.calls.append(("shadow.find_css", selector))
        return FakeElement(self.client, "shadow-child", "Shadow text")

    def find_elements_by_css_selector(self, selector):
        self.client.calls.append(("shadow.find_all_css", selector))
        return [FakeElement(self.client, "shadow-1"), FakeElement(self.client, "shadow-2")]


class FakeClient:
    def __init__(self):
        self.calls = []
        self.current_url = "about:blank"
        self.handles = ["main"]
        self.current_handle = "main"
        self.cookies = {}
        self.timeouts = {"implicit": 0, "pageLoad": 300000, "script": 30000}

    def create_session(self):
        self.calls.append(("create_session",))

    def delete_session(self):
        self.calls.append(("delete_session",))

    def close(self):
        self.calls.append(("close",))

    def navigate(self, url):
        self.current_url = url
        self.calls.append(("navigate", url))

    def document_onload(self):
        self.calls.append(("document_onload",))
        return True

    def get_title(self):
        self.calls.append(("get_title",))
        return "Example title"

    def get_current_url(self):
        self.calls.append(("get_current_url",))
        return self.current_url

    def get_page_source(self):
        return "<html><body>Example</body></html>"

    def status(self):
        self.calls.append(("status",))
        return {"value": {"ready": True, "message": "ok"}}

    def get_timeouts(self):
        self.calls.append(("get_timeouts",))
        return {"value": self.timeouts}

    def set_timeouts(self, timeouts):
        self.timeouts.update(timeouts)
        self.calls.append(("set_timeouts", timeouts))

    def execute_script(self, script, args=None):
        self.calls.append(("execute_script", script, args or []))
        if "document.readyState" in script:
            return "complete"
        if "navigator.userAgent" in script:
            return "Fake AutoWK User Agent"
        if "return arguments[0].getAttribute" in script:
            return "script-result"
        return "script-result"

    def find_element_by_css_selector(self, selector):
        self.calls.append(("find_css", selector))
        return FakeElement(self)

    def find_elements_by_css_selector(self, selector):
        self.calls.append(("find_all_css", selector))
        return [FakeElement(self, "one"), FakeElement(self, "two")]

    def find_element_by_xpath(self, selector):
        self.calls.append(("find_xpath", selector))
        return FakeElement(self, "xpath-id")

    def find_elements_by_xpath(self, selector):
        self.calls.append(("find_all_xpath", selector))
        return [FakeElement(self, "xpath-one"), FakeElement(self, "xpath-two")]

    def wait_for_element_by_css_selector(self, selector, timeout=10.0, interval=0.5):
        self.calls.append(("wait_css", selector, timeout, interval))
        return FakeElement(self, "waited")

    def wait_for_element_by_xpath(self, selector, timeout=10.0, interval=0.5):
        self.calls.append(("wait_xpath", selector, timeout, interval))
        return FakeElement(self, "waited-xpath")

    def wait_for_element(self, using, selector, timeout=10.0, interval=0.5):
        self.calls.append(("wait", using, selector, timeout, interval))
        return FakeElement(self, "waited-generic")

    def take_screenshot(self, filename):
        Path(filename).write_bytes(b"fake page png")

    def add_cookie(self, cookie):
        self.cookies[cookie["name"]] = cookie
        self.calls.append(("add_cookie", cookie))

    def get_all_cookies(self):
        return list(self.cookies.values())

    def get_cookie_by_name(self, name):
        return self.cookies.get(name)

    def delete_cookie(self, name):
        self.cookies.pop(name, None)
        self.calls.append(("delete_cookie", name))

    def delete_all_cookies(self):
        self.cookies.clear()
        self.calls.append(("delete_all_cookies",))

    def get_window_handle(self):
        return self.current_handle

    def get_window_handles(self):
        return list(self.handles)

    def new_window(self, window_type="tab"):
        handle = f"{window_type}-1"
        self.handles.append(handle)
        return {"value": {"handle": handle, "type": window_type}}

    def switch_to_window(self, handle):
        self.current_handle = handle
        self.calls.append(("switch_to_window", handle))

    def close_window(self):
        if self.current_handle in self.handles and self.current_handle != "main":
            self.handles.remove(self.current_handle)
        self.current_handle = "main"
        self.calls.append(("close_window",))

    def get_window_rect(self):
        return {"x": 10, "y": 20, "width": 1200, "height": 800}

    def set_window_rect(self, x=None, y=None, width=None, height=None):
        self.calls.append(("set_window_rect", x, y, width, height))

    def maximize_window(self):
        self.calls.append(("maximize_window",))

    def minimize_window(self):
        self.calls.append(("minimize_window",))

    def back(self):
        self.calls.append(("back",))

    def forward(self):
        self.calls.append(("forward",))

    def refresh(self):
        self.calls.append(("refresh",))

    def switch_to_frame(self, iframe):
        self.calls.append(("switch_to_frame", iframe))

    def switch_to_parent_frame(self):
        self.calls.append(("switch_to_parent_frame",))

    def get_useragent(self):
        return "Fake AutoWK User Agent"

    def click_pos_by_js(self, x, y):
        self.calls.append(("click_pos_by_js", x, y))

    def click_pos_by_win(self, x, y):
        self.calls.append(("click_pos_by_win", x, y))

    def drag_and_drop_pos(self, start_x, start_y, end_x, end_y):
        self.calls.append(("drag_and_drop_pos", start_x, start_y, end_x, end_y))

    def drag_and_drop_pos_human(self, start_x, start_y, end_x, end_y, num_steps=30):
        self.calls.append(("drag_and_drop_pos_human", start_x, start_y, end_x, end_y, num_steps))

    def get_closed_shadow_root(self, selector):
        self.calls.append(("get_closed_shadow_root", selector))
        return FakeElement(self, "closed-shadow-root")


def load_example(filename):
    path = EXAMPLES / filename
    if str(EXAMPLES) not in sys.path:
        sys.path.insert(0, str(EXAMPLES))
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ExampleTests(unittest.TestCase):
    def test_public_examples_are_numbered_and_complete(self):
        names = sorted(path.name for path in EXAMPLES.glob("[0-9][0-9]_*.py"))
        self.assertEqual(EXPECTED_EXAMPLES, names)

    def test_examples_compile(self):
        for path in EXAMPLES.glob("*.py"):
            if path.name == "__init__.py":
                continue
            with self.subTest(path=path.name):
                py_compile.compile(str(path), doraise=True)

    def test_public_examples_expose_parse_run_and_main(self):
        for filename in EXPECTED_EXAMPLES:
            module = load_example(filename)
            with self.subTest(filename=filename):
                self.assertTrue(callable(module.parse_args))
                self.assertTrue(callable(module.run))
                self.assertTrue(callable(module.main))

    def test_navigation_defaults_to_requested_site(self):
        module = load_example("01_navigation.py")
        args = module.parse_args([])
        self.assertEqual("https://xjbedu.site/", args.url)

    def test_dom_sensitive_examples_default_to_local_fixtures(self):
        for filename in [
            "03_text_and_attributes.py",
            "04_input_and_click.py",
            "08_frames.py",
            "12_shadow_root.py",
            "16_waits_and_nested_elements.py",
            "17_pointer_actions.py",
        ]:
            module = load_example(filename)
            with self.subTest(filename=filename):
                args = module.parse_args([])
                self.assertIn("examples/fixtures/", args.url.replace("\\", "/"))

    def test_examples_cover_public_api_names(self):
        combined = "\n".join(path.read_text(encoding="utf-8") for path in EXAMPLES.glob("*.py"))
        missing = [api for api in COVERED_PUBLIC_APIS if api not in combined]
        self.assertEqual([], missing)

    def test_examples_only_cover_current_minibrowser_automation(self):
        combined = "\n".join(path.read_text(encoding="utf-8") for path in EXAMPLES.glob("*.py"))
        for unsupported in [
            "AutoWKListen",
            "enableListen",
            "networkListenPort",
            "set_useragent",
            "clear_websitedata",
            "proxyType",
            "proxyHost",
            "proxyPort",
            "proxyUsername",
            "proxyPassword",
            "userDataDir",
            "--headless",
            "--timezone",
        ]:
            with self.subTest(unsupported=unsupported):
                self.assertNotIn(unsupported, combined)

    def test_examples_can_run_against_fake_client(self):
        for filename in EXPECTED_EXAMPLES:
            module = load_example(filename)
            client = FakeClient()
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as tmp:
                args = module.parse_args([])
                if hasattr(args, "output_dir"):
                    args.output_dir = tmp
                with redirect_stdout(io.StringIO()):
                    module.run(client, args)
                self.assertIn(("create_session",), client.calls)
                self.assertIn(("delete_session",), client.calls)
                self.assertIn(("close",), client.calls)

    def test_fingerprint_example_defaults_to_safari_fp_file(self):
        module = load_example("19_fingerprint_profile.py")
        args = module.parse_args([])
        self.assertEqual(Path("C:/safari/fp.txt"), args.fpfile)

    def test_fingerprint_example_has_visual_html_fixture(self):
        module = load_example("19_fingerprint_profile.py")
        html = module.FINGERPRINT_HTML_PATH.read_text(encoding="utf-8")
        self.assertIn("/fp-profile.json", html)
        self.assertIn("__autowkFingerprintResult", html)
        self.assertIn("data-summary-pass", html)

    def test_fingerprint_profile_parser_accepts_equals_and_colons(self):
        module = load_example("19_fingerprint_profile.py")
        with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as fp:
            fp.write("# comment\nuseragent=Example UA\nwebdriver:0\n languages : en-US,en \n")
            path = Path(fp.name)
        try:
            self.assertEqual(
                {"useragent": "Example UA", "webdriver": "0", "languages": "en-US,en"},
                module.load_fp_profile(path),
            )
        finally:
            path.unlink(missing_ok=True)

    def test_fingerprint_report_skips_sensitive_startup_keys(self):
        module = load_example("19_fingerprint_profile.py")
        report = module.build_fingerprint_report(
            {"socks5_proxy": "secret", "useragent": "Example UA"},
            {"navigator.userAgent": "Example UA"},
        )
        by_key = {item["key"]: item for item in report}
        self.assertEqual("SKIP", by_key["socks5_proxy"]["status"])
        self.assertEqual("<sensitive>", by_key["socks5_proxy"]["expected"])
        self.assertEqual("PASS", by_key["useragent"]["status"])

    def test_socks_proxy_example_builds_socks5h_url_from_colon_tuple(self):
        module = load_example("20_socks_password_proxy.py")
        args = module.parse_args(
            [
                "--mode",
                "args",
                "--proxy",
                "gw.example.test:1288:demo-user:demo-pass",
            ]
        )
        proxy_url = module.build_socks_proxy_url(args)
        self.assertEqual("socks5h://demo-user:demo-pass@gw.example.test:1288", proxy_url)
        self.assertEqual("socks5h://demo-user:<redacted>@gw.example.test:1288", module.redact_proxy_url(proxy_url))

    def test_socks_proxy_example_accepts_custom_webdriver_port(self):
        module = load_example("20_socks_password_proxy.py")
        args = module.parse_args(["--port", "13045"])
        self.assertEqual(13045, args.port)

    def test_socks_proxy_example_safely_formats_console_output(self):
        module = load_example("20_socks_password_proxy.py")
        self.assertEqual("bad:\\xa5", module.console_safe_text("bad:\xa5", encoding="ascii"))

    def test_socks_proxy_example_writes_temporary_fpfile_override(self):
        module = load_example("20_socks_password_proxy.py")
        with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as base:
            base.write("useragent=Example UA\n")
            base_path = Path(base.name)
        generated = None
        try:
            generated = module.write_proxy_fpfile(
                base_path,
                "socks5h://demo-user:demo-pass@gw.example.test:1288",
            )
            text = generated.read_text(encoding="utf-8")
            self.assertIn("useragent=Example UA", text)
            self.assertIn("proxy_type=socks5h", text)
            self.assertIn("http_proxy=socks5h://demo-user:demo-pass@gw.example.test:1288", text)
        finally:
            base_path.unlink(missing_ok=True)
            if generated:
                generated.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
