import random
import math
import base64
import time



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
        script = \
        f"""
            var element = arguments[0];
            element.setAttribute('{attribute_name}', '{value}');
            return element.getAttribute('{attribute_name}');
        """

        self.client.execute_script(script, [{"element-6066-11e4-a52e-4f735466cecf": self.element_id}])
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
        """和屏幕分辨率有关，无法点击请调整分辨率100%"""
        return self.client.request("POST", f"/session/{self.client.session_id}/element/{self.element_id}/click")
    def clear(self):
        return self.client.request("POST", f"/session/{self.client.session_id}/element/{self.element_id}/clear")

    def input(self, text):
        payload = {
            "text": text
        }
        return self.client.request("POST", f"/session/{self.client.session_id}/element/{self.element_id}/value", payload)

    def get_open_shadow_root(self):
        resp = self.client.request("GET", f"/session/{self.client.session_id}/element/{self.element_id}/shadow")
        shadow_root_id = resp["value"]["shadow-6066-11e4-a52e-4f735466cecf"]
        return Element(self.client, shadow_root_id)


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
        # 先拿到元素位置信息
        rect = self.get_rect()
        start_x = int(rect['x'] + rect['width'] / 2)
        start_y = int(rect['y'] + rect['height'] / 2)

        end_x = start_x + offset_x
        end_y = start_y + offset_y

        # 计算贝塞尔曲线的控制点（偏移不大）
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

