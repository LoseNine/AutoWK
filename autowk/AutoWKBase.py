import http.client
import json
import os
import subprocess


def get_bin_file_path(filename):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    exe_path = os.path.join(current_dir, "bin", filename)
    return os.path.abspath(exe_path)


class AutoWKError(Exception):
    """Base exception for AutoWK runtime errors."""


class AutoWKRequestError(AutoWKError):
    """Raised when WebDriver returns an invalid or failed response."""


class AutoWKBase:
    def __init__(self, host, port, webkit_path=None, webdriver_bat=None, timeout=30):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.headers = {"Content-Type": "application/json"}
        self.session_id = None
        self.conn = None
        self.webkit_process = None
        self.webdriver_process = None
        self.webkit_path = webkit_path or get_bin_file_path("MiniBrowser.exe")
        self.webdriver_bat = webdriver_bat or get_bin_file_path("WebDriver.exe")
        self.minibrowseraddr = f"{self.host}:{self.port + 1}"

    def launch_webkit(self, x=0, y=0, width=10, height=10, lang="en-US", timezone="America/Chicago",
                      proxyType='', proxyHost='', proxyPort='', proxyUsername='', proxyPassword='',
                      userDataDir='', fpfile='', userAgent='', headless=False, enableListen=False,
                      networkListenPort=0):
        env = os.environ.copy()
        env["WEBKIT_INSPECTOR_SERVER"] = self.minibrowseraddr
        args = [
            self.webkit_path,
            f"--x={x}",
            f"--y={y}",
            f"--width={width}",
            f"--height={height}",
            f"--lang={lang}",
            f"--timezone={timezone}",
        ]

        if proxyType and proxyHost and proxyPort:
            args.append(f"--proxyType={proxyType}")
            args.append(f"--proxyHost={proxyHost}")
            args.append(f"--proxyPort={proxyPort}")
            if proxyUsername and proxyPassword:
                args.append(f"--proxyUsername={proxyUsername}")
                args.append(f"--proxyPassword={proxyPassword}")

        if userDataDir:
            args.append(f"--userDataDir={userDataDir}")

        if fpfile:
            args.append(f"--fpfile={fpfile}")

        if userAgent:
            args.append(f"--userAgent={userAgent}")

        if headless:
            args.append("--headless")

        if enableListen:
            args.append("--enableListen")
            if networkListenPort:
                args.append(f"--networkListenPort={networkListenPort}")

        self.webkit_process = subprocess.Popen(args, env=env)

    def launch_webdriver(self):
        args = [
            self.webdriver_bat,
            f"--target={self.minibrowseraddr}",
            f"--port={str(self.port)}",
        ]
        self.webdriver_process = subprocess.Popen(args)

    def connect(self):
        self.conn = http.client.HTTPConnection(self.host, self.port, timeout=self.timeout)

    def request(self, method, endpoint, body=None):
        if self.conn is None:
            raise AutoWKRequestError("WebDriver connection is not initialized. Call connect() first.")

        self.conn.request(method, endpoint, body=json.dumps(body) if body is not None else None, headers=self.headers)
        response = self.conn.getresponse()
        raw_body = response.read().decode("utf-8", errors="replace")

        try:
            payload = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            raise AutoWKRequestError(
                f"{method} {endpoint} returned non-JSON response "
                f"({getattr(response, 'status', 'unknown')} {getattr(response, 'reason', '')}): {raw_body[:200]}"
            ) from exc

        status = getattr(response, "status", 200)
        if status >= 400:
            value = payload.get("value") if isinstance(payload, dict) else payload
            message = value.get("message") if isinstance(value, dict) else value
            raise AutoWKRequestError(f"{method} {endpoint} failed with HTTP {status}: {message}")

        return payload

    def create_session(self):
        result = self.request("POST", "/session", {"capabilities": {"firstMatch": [{}]}})
        try:
            self.session_id = result["value"]["sessionId"]
        except (KeyError, TypeError) as exc:
            raise AutoWKRequestError(f"POST /session response did not include a sessionId: {result!r}") from exc

    def delete_session(self):
        return self.request("DELETE", f"/session/{self.session_id}")

    def close(self):
        print("[INFO] Closing connection and shutting down AutoWK-owned processes...")
        if self.conn:
            self.conn.close()
            self.conn = None

        for process in (self.webdriver_process, self.webkit_process):
            self._terminate_process(process)
        print("[INFO] autowk processes terminated.")

    @staticmethod
    def _terminate_process(process, seen=None):
        if not process:
            return
        if seen is None:
            seen = set()

        pid = getattr(process, "pid", None)
        process_key = pid if pid is not None else id(process)
        if process_key in seen:
            return
        seen.add(process_key)

        if not AutoWKBase._process_is_running(process):
            return

        for child in AutoWKBase._find_child_processes(process):
            AutoWKBase._terminate_process(child, seen)

        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)

    @staticmethod
    def _find_child_processes(process):
        pid = getattr(process, "pid", None)
        if not pid:
            return []

        try:
            import psutil
        except ImportError:
            return []

        try:
            return psutil.Process(pid).children(recursive=True)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return []

    @staticmethod
    def _process_is_running(process):
        if hasattr(process, "poll"):
            return process.poll() is None
        if hasattr(process, "is_running"):
            return process.is_running()
        return True
