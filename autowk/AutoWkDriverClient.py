import random
import math
import base64

from .Element import Element
from .AutoWKBase import AutoWKBase


class AutoWK(AutoWKBase):
    def __init__(self, host="127.0.0.1", port=12345):
        super().__init__(host, port)

        self.launch_webkit()
        self.launch_webdriver()
        self.connect()

    def get_all_cookies(self):
        return self.request("GET", f"/session/{self.session_id}/cookie")["value"]

    def get_cookie_by_name(self, name: str):
        return self.request("GET", f"/session/{self.session_id}/cookie/{name}")["value"]

    def add_cookie(self, cookie: dict):
        """
        cookie = {
            "name": "foo",
            "value": "bar",
            "path": "/",
            "domain": "localhost",
            "secure": False,
            "httpOnly": False,
            "expiry": 1744070400
        }
        """
        payload = {"cookie": cookie}
        return self.request("POST", f"/session/{self.session_id}/cookie", payload)

    def delete_cookie(self, name: str):
        return self.request("DELETE", f"/session/{self.session_id}/cookie/{name}")

    def delete_all_cookies(self):
        return self.request("DELETE", f"/session/{self.session_id}/cookie")
    def status(self):
        return self.request("GET", "/status")

    def get_timeouts(self):
        return self.request("GET", f"/session/{self.session_id}/timeouts")

    def set_timeouts(self, timeouts):
        return self.request("POST", f"/session/{self.session_id}/timeouts", timeouts)

    def navigate(self, url):
        response=self.request("POST", f"/session/{self.session_id}/url", {"url": url})
        return response

    def get_current_url(self):
        return self.request("GET", f"/session/{self.session_id}/url")["value"]

    def back(self):
        return self.request("POST", f"/session/{self.session_id}/back")

    def forward(self):
        return self.request("POST", f"/session/{self.session_id}/forward")

    def refresh(self):
        return self.request("POST", f"/session/{self.session_id}/refresh")

    def get_title(self):
        return self.request("GET", f"/session/{self.session_id}/title")["value"]

    def get_page_source(self):
        return self.request("GET", f"/session/{self.session_id}/source")["value"]

    def maximize_window(self):
        return self.request("POST", f"/session/{self.session_id}/window/maximize")

    def minimize_window(self):
        return self.request("POST", f"/session/{self.session_id}/window/minimize")
    def get_window_rect(self):
        return self.request("GET", f"/session/{self.session_id}/window/rect")["value"]

    def set_window_rect(self, x=None, y=None, width=None, height=None):
        payload = {}
        for k, v in zip(["x", "y", "width", "height"], [x, y, width, height]):
            if v is not None:
                payload[k]=v
        return self.request("POST", f"/session/{self.session_id}/window/rect", payload)

    def get_window_handles(self):
        return self.request("GET", f"/session/{self.session_id}/window/handles")["value"]

    def get_window_handle(self):
        return self.request("GET", f"/session/{self.session_id}/window")["value"]

    def close_window(self):
        return self.request("DELETE", f"/session/{self.session_id}/window")

    def switch_to_window(self, handle):
        return self.request("POST", f"/session/{self.session_id}/window", {"handle": handle})

    def new_window(self, window_type="tab"):
        return self.request("POST", f"/session/{self.session_id}/window/new", {"type": window_type})

    def execute_script(self, script, args=[]):
        response = self.request("POST", f"/session/{self.session_id}/execute/sync", {
            "script": script,
            "args": args
        })
        return response["value"]  # 直接返回执行结果

    def take_screenshot(self, filename="screenshot.png"):
        data = self.request("GET", f"/session/{self.session_id}/screenshot")["value"]
        with open(filename, "wb") as f:
            f.write(base64.b64decode(data))

    def find_element_by_css_selector(self, selector):
        result = self.request("POST", f"/session/{self.session_id}/element", {"using": "css selector", "value": selector})
        return Element(self, result["value"]["element-6066-11e4-a52e-4f735466cecf"])

    def find_elements_by_css_selector(self, selector):
        result = self.request("POST", f"/session/{self.session_id}/elements", {"using": "css selector", "value": selector})
        return [Element(self, el["element-6066-11e4-a52e-4f735466cecf"]) for el in result["value"]]

    def find_element_by_xpath(self, selector):
        result = self.request("POST", f"/session/{self.session_id}/element", {"using": "xpath", "value": selector})
        return Element(self, result["value"]["element-6066-11e4-a52e-4f735466cecf"])

    def find_elements_by_xpath(self, selector):
        result = self.request("POST", f"/session/{self.session_id}/elements", {"using": "xpath", "value": selector})
        return [Element(self, el["element-6066-11e4-a52e-4f735466cecf"]) for el in result["value"]]

    def click_pos_by_js(self, x, y):
        """已经优化过isTrusted"""
        script = f"""
        function simulateClick(x, y) {{
            const el = document.elementFromPoint(x, y);
            if (el) {{
                const event = new MouseEvent('ruyiclick', {{
                    bubbles: true,
                    cancelable: true,
                    clientX: x,
                    clientY: y,
                    composed: true
                }});
                Object.defineProperty(event, '_ruyi', {{ value: true, configurable: true }});
                el.dispatchEvent(event);
                return 'dispatched';
            }}
            return 'no target';
        }}
        simulateClick({x}, {y});
        """
        self.execute_script(script)

    def click_pos_by_win(self, x, y):
        payload = {"actions": [{"type": "pointer", "id": "mouse1", "parameters": {"pointerType": "mouse"}, "actions": [{"type": "pointerMove", "duration": 119, "x": x, "y": y, "origin": "viewport"}, {"type": "pointerDown", "button": 0}, {"type": "pointerUp", "button": 0}]}]}
        return self.request("POST", f"/session/{self.session_id}/actions", payload)

    def drag_and_drop_pos(self, start_x, start_y, end_x, end_y):
        payload = {
            "actions": [
                {
                    "type": "pointer",
                    "id": "mouse1",
                    "parameters": {
                        "pointerType": "mouse"
                    },
                    "actions": [
                        # 移动到起点
                        {
                            "type": "pointerMove",
                            "duration": 0,
                            "x": start_x,
                            "y": start_y,
                            "origin": "viewport"
                        },
                        # 按下鼠标左键
                        {
                            "type": "pointerDown",
                            "button": 0
                        },
                        # 拖拽到终点
                        {
                            "type": "pointerMove",
                            "duration": 500,  # 拖拽过程，500ms
                            "x": end_x,
                            "y": end_y,
                            "origin": "viewport"
                        },
                        # 松开鼠标左键
                        {
                            "type": "pointerUp",
                            "button": 0
                        }
                    ]
                }
            ]
        }
        return self.request("POST", f"/session/{self.session_id}/actions", payload)

    def drag_and_drop_pos_human(self, start_x, start_y, end_x, end_y, num_steps=30):
        # 控制点靠近直线，只有小幅度偏移
        mid_x = (start_x + end_x) / 2
        mid_y = (start_y + end_y) / 2
        offset_x = random.randint(-30, 30)  # 仅小幅度，模拟人类小调整
        offset_y = random.randint(-30, 30)

        control_x = mid_x + offset_x
        control_y = mid_y + offset_y

        num_steps = 30  # 更多步数，更平滑
        actions = [
            {
                "type": "pointerMove",
                "duration": 0,
                "x": start_x,
                "y": start_y,
                "origin": "viewport"
            },
            {
                "type": "pointerDown",
                "button": 0
            }
        ]

        for i in range(1, num_steps + 1):
            # 速度曲线（ease-in-out）
            t = i / num_steps
            t = 0.5 * (1 - math.cos(math.pi * t))  # 使用cos函数制造加速-减速效果

            # 贝塞尔曲线插值
            x = int((1 - t) ** 2 * start_x + 2 * (1 - t) * t * control_x + t ** 2 * end_x)
            y = int((1 - t) ** 2 * start_y + 2 * (1 - t) * t * control_y + t ** 2 * end_y)

            # 动态调整每步持续时间
            # 开始慢 -> 中间快 -> 结束慢
            if i < num_steps * 0.2 or i > num_steps * 0.8:
                duration = random.randint(20, 40)  # 边缘慢一点
            else:
                duration = random.randint(5, 15)  # 中间快一点

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
                    "parameters": {
                        "pointerType": "mouse"
                    },
                    "actions": actions
                }
            ]
        }

        return self.request("POST", f"/session/{self.session_id}/actions", payload)


