from autowk.AutoWkDriverClient import AutoWK
import time

if __name__ == "__main__":
    """自动化1236滑块验证码"""
    client = AutoWK()
    try:
        client.create_session()

        print("[STATUS]", client.status())

        client.set_timeouts({"pageLoad": 10000})
        print("[GET TIMEOUTS]", client.get_timeouts())

        client.navigate(r"https://steamdb.info/")
        print("[URL]", client.get_current_url())
        print(client.get_all_cookies())
        print(client.get_window_handles())
        handles = client.request("GET", f"/session/{client.session_id}/window/handles")["value"]

        time.sleep(10)
        client.click_pos_by_win(266,326)
        print('拖拽完毕')


    except Exception as e:
        print(e)

    finally:
        time.sleep(500)
        client.delete_session()
        client.close()