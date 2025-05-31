from autowk.AutoWkDriverClient import AutoWK
import time

if __name__ == "__main__":
    client = AutoWK(lang="en-US", timezone="America/Chicago")
    try:
        print("[STATUS]", client.status())
        client.create_session()

        print("[STATUS]", client.status())

        client.set_timeouts({"pageLoad": 10000})
        print("[GET TIMEOUTS]", client.get_timeouts())

        client.set_useragent("AA")
        client.navigate(r"https://steamdb.info/")
        print("[URL]", client.get_current_url())

        time.sleep(10)
        # 坐标直接用操作系统的截图，然后画板打开看x和y坐标
        client.click_pos_by_win(266, 326)
        print('拖拽完毕')


    except Exception as e:
        print(e)

    finally:
        time.sleep(500)
        client.delete_session()
        client.close()