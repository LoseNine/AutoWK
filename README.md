# AutoWK 自动化浏览器框架

AutoWK 是一个面向 Windows 的 WebKit 自动化浏览器框架。包内自带当前编译出的
`MiniBrowser.exe`、`WebDriver.exe` 和运行所需 DLL，通过 Python API 启动浏览器并执行
WebDriver 风格的页面自动化操作。

当前发布版本：`0.4.3`

## 项目亮点

- 基于 WebKit / MiniBrowser 运行时，安装包内置浏览器与 WebDriver。
- Python API 控制导航、元素查找、输入、点击、脚本执行、窗口、Cookie、iframe 和截图。
- 支持页面截图和元素截图。
- 支持 open shadow root；当前 MiniBrowser 也提供 closed shadow root 访问能力。
- 支持 WebDriver Actions 形式的坐标点击、拖拽和模拟人类轨迹拖拽。
- 支持通过 `fpfile` 配置启动参数、指纹参数和代理参数。
- 支持 HTTP / SOCKS 代理配置；SOCKS 密码代理示例已放在 `examples/20_socks_password_proxy.py`。
- 默认首页已调整为 `https://xjbedu.site/`，并去除了旧的默认关闭页。
- 自动化启动时使用单个 MiniBrowser 窗口承载会话，避免额外弹出一个无用初始窗口。
- 关闭时只清理当前 AutoWK 实例启动的浏览器和 WebDriver 进程。

当前 README 只描述 `0.4.3` 已保留并测试覆盖的能力。

## 安装

```bash
pip install autowk==0.4.3
```

AutoWK 当前只面向 64 位 Windows。wheel 内含 Windows 原生可执行文件和 DLL，不适用于
Linux 或 macOS。

## 快速开始

```python
from autowk import AutoWK


client = AutoWK(lang="en-US", timezone="America/Chicago")
try:
    client.create_session()
    client.navigate("https://xjbedu.site/")
    client.document_onload()

    print("Title:", client.get_title())
    print("URL:", client.get_current_url())
finally:
    try:
        client.delete_session()
    finally:
        client.close()
```

旧路径仍然兼容：

```python
from autowk.AutoWkDriverClient import AutoWK
from autowk.AutoWKOptions import Options
```

## 命令行诊断

`0.4.3` 提供基础诊断命令：

```bash
python -m autowk
autowk --version
autowk doctor
autowk paths
```

`autowk doctor` 会检查内置 `MiniBrowser.exe`、`WebDriver.exe` 是否存在，以及默认本地端口是否可用。
它不会启动浏览器。

## examples 示例

示例都在 `examples/` 目录，文件名按 `01_xxx.py` 编号。默认导航示例访问
`https://xjbedu.site/`，需要 DOM 固定结构的示例使用 `examples/fixtures/` 下的本地 HTML。

```bash
python examples\01_navigation.py
python examples\05_screenshots.py --output-dir examples_output
python examples\11_options.py --fpfile C:\safari\fp.txt
python examples\19_fingerprint_profile.py --fpfile C:\safari\fp.txt
python examples\20_socks_password_proxy.py --mode fpfile --fpfile C:\safari\fp.txt
```

当前示例覆盖：

| 示例 | 功能 |
| --- | --- |
| `01_navigation.py` | 打开 `https://xjbedu.site/`，读取标题和 URL |
| `02_find_elements.py` | CSS / XPath 查找单个和多个元素 |
| `03_text_and_attributes.py` | 文本、属性读取和属性设置 |
| `04_input_and_click.py` | 输入、清空、点击 |
| `05_screenshots.py` | 页面截图和元素截图 |
| `06_history.py` | 后退、前进、刷新 |
| `07_window_management.py` | 窗口大小、句柄、新建窗口和切换 |
| `08_frames.py` | iframe 切换和返回父 frame |
| `09_cookies.py` | Cookie 添加、读取、删除 |
| `10_execute_script.py` | 执行 JavaScript |
| `11_options.py` | 通过 `fpfile` 启动 MiniBrowser |
| `12_shadow_root.py` | open shadow root 查询 |
| `13_proxy_optional.py` | 通过 `fpfile` 传入代理配置 |
| `14_page_state_and_timeouts.py` | 页面 readyState、timeout 设置 |
| `15_user_agent.py` | 读取当前 User-Agent |
| `16_waits_and_nested_elements.py` | 等待元素、子元素查找 |
| `17_pointer_actions.py` | 坐标点击、拖拽、人类轨迹拖拽 |
| `18_closed_shadow_root_optional.py` | closed shadow root 查询 |
| `19_fingerprint_profile.py` | 本地 HTML 指纹检测页，对齐 `fpfile` 配置 |
| `20_socks_password_proxy.py` | SOCKS 密码代理，支持直接读取 `fpfile` 或临时生成代理 fpfile |

## MiniBrowser 启动参数

AutoWK 会自动启动 MiniBrowser。常用参数可以通过 `AutoWK(...)` 或 `Options(...)` 传入：

| 参数 | Python 参数 | 说明 |
| --- | --- | --- |
| `--x=` | `x` | 浏览器窗口左上角 X 坐标 |
| `--y=` | `y` | 浏览器窗口左上角 Y 坐标 |
| `--width=` | `width` | 浏览器窗口宽度 |
| `--height=` | `height` | 浏览器窗口高度 |
| `--lang=` | `lang` | 浏览器语言，例如 `en-US` |
| `--timezone=` | `timezone` | 浏览器时区，例如 `America/Chicago` |
| `--userDataDir=` | `userDataDir` | 用户数据目录，用于隔离缓存、Cookie、本地存储等 |
| `--fpfile=` | `fpfile` | 指纹和启动配置文件 |
| `--userAgent=` | `userAgent` | 启动时设置 User-Agent |
| `--proxyType=` | `proxyType` | 代理类型，例如 `HTTP`、`SOCKS5` |
| `--proxyHost=` | `proxyHost` | 代理主机 |
| `--proxyPort=` | `proxyPort` | 代理端口 |
| `--proxyUsername=` | `proxyUsername` | 代理用户名 |
| `--proxyPassword=` | `proxyPassword` | 代理密码 |

示例：

```python
from autowk import AutoWK


client = AutoWK(
    x=80,
    y=60,
    width=1280,
    height=800,
    lang="en-US",
    timezone="America/Chicago",
    fpfile=r"C:\safari\fp.txt",
)
```

## fpfile 配置

`fpfile` 是 MiniBrowser 的启动配置文件，当前示例主要覆盖浏览器指纹、代理和启动行为。
`examples/19_fingerprint_profile.py` 会启动本地 HTML 服务读取浏览器实际暴露的指纹值，并与
`fpfile` 中可页面读取的字段进行对比。

常见字段示例：

```txt
useragent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/605.1.15 (KHTML, like Gecko)
language=en-US
languages=en-US,en
timezone=America/Chicago
hardware_concurrency=8
maxTouchPoints=0
webdriver=0

unmasked_renderer=Apple GPU
unmasked_vendor=Apple Inc.
canvas_noise=500
clientrect_noise=20

canvas_alpha=0
canvas_depth=0
canvas_stencil=0
canvas_antialias=1
canvas_premultipliedAlpha=0
canvas_preserveDrawingBuffer=0
canvas_failIfMajorPerformanceCaveat=0
canvas_powerPreference=high-performance

webgl_param_UNMASKED_RENDERER_WEBGL=Apple GPU
webgl_param_UNMASKED_VENDOR_WEBGL=Apple Inc.
webgl_param_DEPTH_BITS=24
webgl_param_MAX_TEXTURE_SIZE=4096
webgl_param_MAX_VIEWPORT_DIMS=4096
```

代理也可以写入 `fpfile`。SOCKS 密码代理示例会生成如下形式的临时配置：

```txt
proxy_type=socks5h
http_proxy=socks5h://username:password@gw.example.com:1288
```

代理账号密码属于敏感信息。示例输出会隐藏密码，但浏览器启动参数或 fpfile 本身仍可能被本机进程列表、
日志或文件读取到，请不要在不可信机器上使用真实代理凭据。

## AutoWK API 摘要

### 会话和状态

- `create_session()`
- `delete_session()`
- `close()`
- `status()`
- `get_timeouts()`
- `set_timeouts(timeouts)`
- `document_onload(interval=0.5)`

### 页面控制

- `navigate(url)`
- `get_current_url()`
- `get_title()`
- `get_page_source()`
- `back()`
- `forward()`
- `refresh()`
- `execute_script(script, args=None)`

### 元素查找

- `find_element_by_css_selector(selector)`
- `find_elements_by_css_selector(selector)`
- `find_element_by_xpath(selector)`
- `find_elements_by_xpath(selector)`
- `wait_for_element(using, selector, timeout=10.0, interval=0.5)`
- `wait_for_element_by_css_selector(selector, timeout=10.0, interval=0.5)`
- `wait_for_element_by_xpath(selector, timeout=10.0, interval=0.5)`

### Element 方法

- `get_attribute(name)`
- `set_attribute(name, value)`
- `get_text()` / `text`
- `get_rect()`
- `is_displayed()`
- `click()`
- `clear()`
- `input(text)`
- `take_element_screenshot(filename)`
- `find_element_by_css_selector(selector)`
- `find_elements_by_css_selector(selector)`
- `find_element_by_xpath(selector)`
- `find_elements_by_xpath(selector)`
- `drag_element_by_offset_line(offset_x, offset_y)`
- `drag_element_by_offset_human(offset_x, offset_y, num_steps=30)`

### 窗口、frame 和 shadow root

- `get_window_rect()`
- `set_window_rect(x=None, y=None, width=None, height=None)`
- `maximize_window()`
- `minimize_window()`
- `get_window_handle()`
- `get_window_handles()`
- `new_window(window_type="tab")`
- `switch_to_window(handle)`
- `close_window()`
- `switch_to_frame(iframe)`
- `switch_to_parent_frame()`
- `Element.get_open_shadow_root()`
- `get_closed_shadow_root(css_selector)`

### Cookie 和截图

- `get_all_cookies()`
- `get_cookie_by_name(name)`
- `add_cookie(cookie)`
- `delete_cookie(name)`
- `delete_all_cookies()`
- `take_screenshot(filename="screenshot.png")`

### 鼠标和拖拽

- `click_pos_by_js(x, y)`
- `click_pos_by_win(x, y)`
- `drag_and_drop_pos(start_x, start_y, end_x, end_y)`
- `drag_and_drop_pos_human(start_x, start_y, end_x, end_y, num_steps=30)`

## 开发和验证

```bash
python -m unittest discover -s tests
Get-ChildItem -Path autowk,examples -Filter *.py -Recurse | ForEach-Object { python -m py_compile $_.FullName }
python -m build
python -m twine check dist\*
```

## 许可证

AutoWK 的 Python 代码使用 BSD 2-Clause License。安装包同时包含 WebKit runtime、相关 DLL 和
WebInspector 第三方资源，它们遵循各自上游许可证。重新分发前请查看 `LICENSE`、`NOTICE`、
`THIRD_PARTY_NOTICES.md` 和 `licenses/` 下的许可证文件。
