from autowk.AutoWkDriverClient import AutoWK
import time

if __name__ == "__main__":
    client = AutoWK()
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
        client.drag_and_drop_pos_human(525,436,848,436)
        print('拖拽完毕')


    except Exception as e:
        print(e)

    finally:
        time.sleep(50)
        client.delete_session()
        client.close()