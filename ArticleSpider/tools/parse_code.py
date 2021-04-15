
import base64
import json
import requests


def base64_api(uname, pwd, img):
    """
    快识别验证码识别接口
    :param uname:快识别用户名
    :param pwd:快识别密码
    :param img:图片路径
    :return:返回识别结果
    """
    with open(img, 'rb') as f:
        base64_data = base64.b64encode(f.read())
        b64 = base64_data.decode()
    # 65是汉字点选验证码，55是识别物体验证码
    data = {"username": uname, "password": pwd, "image": b64, 'typeid': 55}
    result = json.loads(requests.post("http://api.ttshitu.com/imageXYPlus", json=data).text)
    if result['success']:
        return result["data"]["result"]
    else:
        return result["message"]


if __name__ == "__main__":
    img_path = "D:\\Py-Project\\spider\\bilbil_sel\\yzm.png"
    result = base64_api(uname='tang1323', pwd='130796abc', img=img_path)
    print(result)


























