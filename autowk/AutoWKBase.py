import http.client
import subprocess
import os
import psutil
from pathlib import Path
import json

def get_webkit_executable_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    exe_path = os.path.join(current_dir, ".", "bin", "MiniBrowser.exe")
    exe_path = os.path.abspath(exe_path)
    return exe_path

def get_webdriver_executable_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    exe_path = os.path.join(current_dir, ".", "bin", "WebDriver.exe")
    exe_path = os.path.abspath(exe_path)
    return exe_path
class AutoWKBase:
    def __init__(self, host, port,webkit_path=None,webdriver_bat=None):

        self.host = host
        self.port = port
        self.headers = {"Content-Type": "application/json"}
        self.session_id = None
        self.conn = None

        if not webkit_path and not webdriver_bat:
            self.webkit_path = get_webkit_executable_path()
            self.webdriver_bat = get_webdriver_executable_path()

        self.minibrowseraddr = f"{self.host}:{self.port + 1}"
    def launch_webkit(self):
        env = os.environ.copy()
        env["WEBKIT_INSPECTOR_SERVER"] = self.minibrowseraddr
        #给进行通信的窗口设置大小，实际上启动完就可以关闭了
        args = [
            self.webkit_path,
            "--x=0",
            "--y=0",
            "--width=10",
            "--height=10"
        ]

        self.webkit_process = subprocess.Popen(args, env=env)

    def launch_webdriver(self):
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and 'WebDriver.exe' in proc.info['name']:
                    subprocess.run(["taskkill", "/f", "/im", "WebDriver.exe"], stdout=subprocess.DEVNULL)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        args = [
            self.webdriver_bat,
            f"--target={self.minibrowseraddr}",
            f"--port={str(self.port)}",
        ]

        self.webdriver_process = subprocess.Popen(args)

    def connect(self):
        self.conn = http.client.HTTPConnection(self.host, self.port)

    def request(self, method, endpoint, body=None):
        if body is None or body == {}:
            body = {"capabilities": {"firstMatch": [{}]}}
        self.conn.request(method, endpoint, body=json.dumps(body) if body else None, headers=self.headers)
        return json.loads(self.conn.getresponse().read().decode("utf-8"))

    def create_session(self):
        result = self.request("POST", "/session")
        self.session_id = result["value"]["sessionId"]

    def delete_session(self):
        return self.request("DELETE", f"/session/{self.session_id}")

    def close(self):
        print("[INFO] Closing connection and shutting down MiniBrowser and WebDriver...")
        if self.conn:
            self.conn.close()
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name']:
                    if 'MiniBrowser.exe' in proc.info['name']:
                        print(f"[INFO] Terminating process: {proc.info['name']} (PID {proc.pid})")
                        proc.terminate()
                    if 'WebDriver.exe' in proc.info['name']:
                        print(f"[INFO] Terminating process: {proc.info['name']} (PID {proc.pid})")
                        subprocess.run(["taskkill", "/f", "/im", "WebDriver.exe"], stdout=subprocess.DEVNULL)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        print("[INFO] autowk processes terminated.")