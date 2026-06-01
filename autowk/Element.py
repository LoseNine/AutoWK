import random
import math
import base64
import time


ELEMENT_KEY = "element-6066-11e4-a52e-4f735466cecf"
SHADOW_ROOT_KEY = "shadow-6066-11e4-a52e-4f735466cecf"


class Element:
    def __init__(self, client, element_id):
        self.client = client
        self.element_id = element_id

    @property
    def text(self):
        return self.get_text()

    def get_attribute(self, name):
        return self.client.request("GET", f"/session/{self.client.session_id}/element/{self.element_id}/attribute/{name}")["value"]

    def set_attribute(self, attribute_name, value):
        script = """
            var element = arguments[0];
            element.setAttribute(arguments[1], arguments[2]);
            return element.getAttribute(arguments[1]);
        """

        self.client.execute_script(script, [
            {"element-6066-11e4-a52e-4f735466cecf": self.element_id},
            attribute_name,
            value,
        ])
        return self

    def get_text(self):
        return self.client.request("GET", f"/session/{self.client.session_id}/element/{self.element_id}/text")["value"]

    def get_rect(self):
        return self.client.request("GET", f"/session/{self.client.session_id}/element/{self.element_id}/rect")["value"]

    def take_element_screenshot(self, filename="element_screenshot.png"):
        data = self.client.request("GET", f"/session/{self.client.session_id}/element/{self.element_id}/screenshot")["value"]
        with open(filename, "wb") as f:
            f.write(base64.b64decode(data))

    def is_displayed(self):
        return self.client.request("GET", f"/session/{self.client.session_id}/element/{self.element_id}/displayed")["value"]

    def click(self):
        """Compatibility helper."""
        return self.client.request("POST", f"/session/{self.client.session_id}/element/{self.element_id}/click", {})
    def clear(self):
        return self.client.request("POST", f"/session/{self.client.session_id}/element/{self.element_id}/clear", {})

    def input(self, text):
        payload = {
            "text": text
        }
        return self.client.request("POST", f"/session/{self.client.session_id}/element/{self.element_id}/value", payload)

    def get_open_shadow_root(self):
        resp = self.client.request("GET", f"/session/{self.client.session_id}/element/{self.element_id}/shadow")
        shadow_root_id = resp["value"][SHADOW_ROOT_KEY]
        return ShadowRoot(self.client, shadow_root_id)


    def find_element_by_css_selector(self, selector: str):
        url = f"/session/{self.client.session_id}/element/{self.element_id}/element"
        payload = {"using": "css selector", "value": selector}
        result=self.client.request("POST",url, payload)
        return Element(self.client, result["value"]["element-6066-11e4-a52e-4f735466cecf"])

    def find_elements_by_css_selector(self,selector: str):
        url = f"/session/{self.client.session_id}/element/{self.element_id}/elements"
        payload = {"using": "css selector", "value": selector}
        result=self.client.request("POST",url, payload)
        return [Element(self.client, el["element-6066-11e4-a52e-4f735466cecf"]) for el in result["value"]]

    def find_element_by_xpath(self, selector: str):
        url = f"/session/{self.client.session_id}/element/{self.element_id}/element"
        payload = {"using": "xpath", "value": selector}
        result=self.client.request("POST",url, payload)
        return Element(self.client, result["value"]["element-6066-11e4-a52e-4f735466cecf"])

    def find_elements_by_xpath(self,selector: str):
        url = f"/session/{self.client.session_id}/element/{self.element_id}/elements"
        payload = {"using": "xpath", "value": selector}
        result=self.client.request("POST",url, payload)
        return [Element(self.client, el["element-6066-11e4-a52e-4f735466cecf"]) for el in result["value"]]
    def drag_element_by_offset_line(self, offset_x, offset_y):
        payload = {
            "actions": [
                {
                    "type": "pointer",
                    "id": "mouse1",
                    "parameters": {
                        "pointerType": "mouse"
                    },
                    "actions": [
                        {
                            "type": "pointerMove",
                            "origin": {
                                "element-6066-11e4-a52e-4f735466cecf": self.element_id
                            },
                            "x": 0,
                            "y": 0,
                            "duration": 0
                        },
                        {
                            "type": "pointerDown",
                            "button": 0
                        },
                        {
                            "type": "pointerMove",
                            "origin": "pointer",
                            "x": offset_x,
                            "y": offset_y,
                            "duration": 500
                        },
                        {
                            "type": "pointerUp",
                            "button": 0
                        }
                    ]
                }
            ]
        }
        return self.client.request("POST", f"/session/{self.client.session_id}/actions", payload)

    def drag_element_by_offset_human(self, offset_x, offset_y, num_steps=30):
        # Internal action step.
        rect = self.get_rect()
        start_x = int(rect['x'] + rect['width'] / 2)
        start_y = int(rect['y'] + rect['height'] / 2)

        end_x = start_x + offset_x
        end_y = start_y + offset_y

        # Internal action step.
        mid_x = (start_x + end_x) / 2
        mid_y = (start_y + end_y) / 2
        offset_cx = random.randint(-30, 30)
        offset_cy = random.randint(-30, 30)
        control_x = mid_x + offset_cx
        control_y = mid_y + offset_cy

        actions = [
            {
                "type": "pointerMove",
                "duration": 0,
                "origin": {
                    "element-6066-11e4-a52e-4f735466cecf": self.element_id
                },
                "x": 0,
                "y": 0
            },
            {
                "type": "pointerDown",
                "button": 0
            }
        ]

        for i in range(1, num_steps + 1):
            t = i / num_steps
            t = 0.5 * (1 - math.cos(math.pi * t))  # ease-in-out

            x = int((1 - t) ** 2 * start_x + 2 * (1 - t) * t * control_x + t ** 2 * end_x)
            y = int((1 - t) ** 2 * start_y + 2 * (1 - t) * t * control_y + t ** 2 * end_y)

            if i < num_steps * 0.2 or i > num_steps * 0.8:
                duration = random.randint(20, 40)
            else:
                duration = random.randint(5, 15)

            actions.append({
                "type": "pointerMove",
                "duration": duration,
                "x": x,
                "y": y,
                "origin": "viewport"
            })

        actions.append({
            "type": "pointerUp",
            "button": 0
        })

        payload = {
            "actions": [
                {
                    "type": "pointer",
                    "id": "mouse1",
                    "parameters": {"pointerType": "mouse"},
                    "actions": actions
                }
            ]
        }

        return self.client.request("POST", f"/session/{self.client.session_id}/actions", payload)

    def __str__(self):
        str_=f"[Element] {self.client}"
        return str_


class ShadowRoot:
    def __init__(self, client, shadow_root_id):
        self.client = client
        self.shadow_root_id = shadow_root_id

    def find_element_by_css_selector(self, selector: str):
        return self._find_element("css selector", selector)

    def find_elements_by_css_selector(self, selector: str):
        return self._find_elements("css selector", selector)

    def find_element_by_xpath(self, selector: str):
        return self._find_element("xpath", selector)

    def find_elements_by_xpath(self, selector: str):
        return self._find_elements("xpath", selector)

    def _find_element(self, using, selector):
        result = self.client.request("POST", self._endpoint("element"), {"using": using, "value": selector})
        return Element(self.client, result["value"][ELEMENT_KEY])

    def _find_elements(self, using, selector):
        result = self.client.request("POST", self._endpoint("elements"), {"using": using, "value": selector})
        return [Element(self.client, el[ELEMENT_KEY]) for el in result["value"]]

    def _endpoint(self, action):
        return f"/session/{self.client.session_id}/shadow/{self.shadow_root_id}/{action}"
