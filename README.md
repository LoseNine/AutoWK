## AutoWK 自动化浏览器框架
> 🚀 一个基于原生 WebKit二次开发的自动化浏览器框架，支持命令行参数控制窗口位置与代理配置，并通过 Python 客户端驱动自动操作浏览器。
<p align="center">
  <img src="icon.png" alt="AutoWK Logo" width="230">
</p>

## ✨ 项目亮点

- ✅ 🧠 基于 WebKit 源码构建，小而精致的浏览器内核
- ✅ 🛠️ 自动启动 WebKit 与 WebDriver 进程
- ✅ 📜 支持命令行传参（窗口位置、尺寸、代理类型、代理认证）
- ✅ 💪 网络改造，支持 HTTP/SOCKS5 等代理模式
- ✅ 📏 Python API 调用控制浏览器行为
- ✅ 🧪 人类行为模拟，底层行为重写，自定义行为动作都是isTrusted。
---


## 快速开始
> 🚀 交流群QQ：391116392
1. 安装依赖：

   ```bash
   pip install autowk==0.2.4
   ```

2. 编写代码，启动自动化：

### 示例代码 ：过steam的定制5s盾
```python
from autowk.AutoWkDriverClient import AutoWK
import time

if __name__ == "__main__":
    client = AutoWK(lang="en-US",timezone="America/Chicago")
    try:
        client.create_session()

        print("[STATUS]", client.status())

        client.set_timeouts({"pageLoad": 10000})
        print("[GET TIMEOUTS]", client.get_timeouts())
        
        client.navigate(r"https://steamdb.info/")
        print("[URL]", client.get_current_url())

        time.sleep(10)
        #坐标直接用操作系统的截图，然后画板打开看x和y坐标
        client.click_pos_by_win(266,326)
        print('拖拽完毕')


    except Exception as e:
        print(e)

    finally:
        time.sleep(500)
        client.delete_session()
        client.close()
```
### 示例代码 ：过12306滑块验证码
```python
from autowk.AutoWkDriverClient import AutoWK
import time

if __name__ == "__main__":
    """自动化1236滑块验证码"""
    client = AutoWK(lang="en-US",timezone="America/Chicago")
    try:
        client.create_session()

        print("[STATUS]", client.status())

        client.set_timeouts({"pageLoad": 10000})
        print("[GET TIMEOUTS]", client.get_timeouts())

        client.navigate(r"https://www.12306.cn/index/view/infos/ticket_check.html")
        print("[URL]", client.get_current_url())

        #输入座次
        input_ele=client.find_element_by_css_selector("input#ticket_check_trainNum").input("1462")

        time.sleep(3)
        #选择地点
        drap=client.find_element_by_css_selector("div.model-select-text")
        drap.set_attribute("data-value","TXP")
        print('attr:', drap.get_attribute("data-value"))
        print('选择完毕')

        time.sleep(3)
        #拖拽滑块验证码
        btn=client.find_element_by_css_selector("li a.btn.btn-primary").click()
        time.sleep(5)
        #拖拽滑块验证码，这里用的是拖拽模拟人类行为，所以用的是drag_and_drop_pos_human方法
        #坐标需要自己定位一下
        client.drag_and_drop_pos_human(525,436,848,436)
        print('拖拽完毕')


    except Exception as e:
        print(e)

    finally:
        time.sleep(5)
        client.delete_session()
        client.close()
```

---

## 支持的启动命令行参数（MiniBrowser.exe）

| 参数                 | 示例                            | 说明                       |
|--------------------|----------------------------------|--------------------------|
| `--x=`             | `--x=100`                        | 设置窗口左上角 X 坐标             |
| `--y=`             | `--y=200`                        | 设置窗口左上角 Y 坐标             |
| `--width=`         | `--width=1280`                   | 设置窗口宽度                   |
| `--height=`        | `--height=720`                   | 设置窗口高度                   |
| 语言时区               |----------------------------------|--------------------------|
| `--lang=`          | `--lang=en-US`                 | 设置浏览器内部所有语言                 |
| `--timezone=`      | `--timezone=America/Chicago`      | 设置浏览器内部时区                 |
| 密码代理               |----------------------------------|--------------------------|
| `--proxyType=`     | `--proxyType=HTTP`             | 代理类型：`HTTP` / `SOCKS5` 等 |
| `--proxyHost=`     | `--proxyHost=127.0.0.1`          | 代理服务器地址                  |
| `--proxyPort=`     | `--proxyPort=1080`               | 代理端口                     |
| `--proxyUsername=` | `--proxyUsername=admin`          | 代理认证用户名                  |
| `--proxyPassword=` | `--proxyPassword=123456`         | 代理认证密码                   |
```cmd
例子:minibrowser.exe --proxyType=SOCKS5  --proxyHost=1.1.1.1  --proxyPort=1000 --proxyUsername=ruyi  --proxyPassword=wifi --x=500 --y=100  --width=500 --height=500 
```
---


## TODO

- ✅ 可以提出需要的功能
---
