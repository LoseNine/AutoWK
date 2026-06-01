import unittest
from unittest.mock import patch

from autowk import AutoWK
from autowk.AutoWKBase import AutoWKBase
from autowk.Element import Element


class CapturingAutoWK(AutoWK):
    def __init__(self):
        self.session_id = "session-id"
        self.calls = []

    def request(self, method, endpoint, body=None):
        self.calls.append((method, endpoint, body))
        return {"value": None}


class CapturingElementClient:
    def __init__(self):
        self.session_id = "session-id"
        self.calls = []

    def request(self, method, endpoint, body=None):
        self.calls.append((method, endpoint, body))
        return {"value": None}


class WebDriverPayloadTests(unittest.TestCase):
    def test_launch_webkit_does_not_load_default_placeholder_page(self):
        client = AutoWKBase("127.0.0.1", 12345, webkit_path="MiniBrowser.exe")

        with patch("subprocess.Popen") as popen:
            client.launch_webkit()

        args = popen.call_args.args[0]
        self.assertFalse(any(arg.startswith("--url=") for arg in args))
        self.assertFalse(any("closePage.html" in arg for arg in args))

    def test_no_argument_browser_actions_send_empty_json_object(self):
        client = CapturingAutoWK()

        client.back()
        client.forward()
        client.refresh()
        client.maximize_window()
        client.minimize_window()
        client.switch_to_parent_frame()

        for method, endpoint, body in client.calls:
            with self.subTest(endpoint=endpoint):
                self.assertEqual("POST", method)
                self.assertEqual({}, body)

    def test_element_click_and_clear_send_empty_json_object(self):
        client = CapturingElementClient()
        element = Element(client, "element-id")

        element.click()
        element.clear()

        for method, endpoint, body in client.calls:
            with self.subTest(endpoint=endpoint):
                self.assertEqual("POST", method)
                self.assertEqual({}, body)


if __name__ == "__main__":
    unittest.main()
