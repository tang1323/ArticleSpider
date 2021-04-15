

import json
import requests



class YDMHttp(object):
    apiurl = 'http://api.yundama.com/api.php'
    username = ''
    password = ''
    appid = ''
    appkey = ''

    def __init__(self, username, password, appid, appkey):
        self.username = username
        self.password = password
        self.appid = str(appid)
        self.appkey = appkey

    def balance(self):
        date = {'method': 'balance','username': self.username, 'password': self.password, 'appid': self.appid, 'appkey': self.appkey}
        response_data = requests.post(self.apiurl, data=date)
        ret_data = json.loads(response_data.text)
        if ret_data["ret"] == 0:
            print("获取剩下积分",ret_data["balance"])
            return ret_data["balance"]
        else:
            return None


    def login(self):
        data = {"method": 'login', 'username':self.username, 'password': self.password, 'appid': self.appid, 'appkey': self.appkey}
        response_data = requests.post(self.apiurl, data=data)

        print("这是打印{0}".format(response_data.text))

        ret_data = json.loads(response_data.text)

        print(response_data.text)


        if ret_data["ret"] == 0:
            print("登录成功", ret_data["uid"])
            return ret_data["uid"]
        else:
            return None


    def decode(self, filename, codetype, timeout):
        data = {'method': 'upload', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey, 'codetype': str(codetype), 'timeout': str(timeout)}
        files = {'file':open(filename, 'rb')}
        response_data = requests.post(self.apiurl, files=files,data = data)

        ret_data = json.loads(response_data.text)
        if ret_data["ret"] == 0:
            print("识别成功", ret_data["text"])
            return ret_data["text"]
        else:
            return None

def ydm(file_path):
    # 用户名
    username = 'angming'

    # 密码
    password = '130796abc'

    # 软件ＩＤ，开发者分成必要参数。登录开发者后台【我的软件】获得！
    appid = 10749

    # 软件密钥，开发者分成必要参数。登录开发者后台【我的软件】获得！
    appkey = '189a7ca1bd420e2e64dde6a418c12c0f'
    # 图片文件
    filename = 'image/3.png'
    # 验证码类型，# 例：1004表示4位字母数字，不同类型收费不同。请准确填写，否则影响识别率。在此查询所有类型 http://www.yundama.com/price.html
    codetype = 2000
    # 超时时间，秒
    timeout = 60
    # 检查
    yundama = YDMHttp(username, password, appid, appkey)
    if (username == "username"):
        print('请设置好相关参数再测试')

    else:
        return yundama.decode(file_path, codetype, timeout)


if __name__ == "__main__":
    # 用户名
    username = "angming"
    # 密码
    password = '130796abc'

    # 软件ＩＤ，开发者分成必要参数。登录开发者后台【我的软件】获得！
    appid = 10749

    # 软件密钥，开发者分成必要参数。登录开发者后台【我的软件】获得！
    appkey = '189a7ca1bd420e2e64dde6a418c12c0f'
    filename = '/ArticleSpider/tools/image/5.png'
    # 验证码类型，# 例：1004表示4位字母数字，不同类型收费不同。请准确填写，否则影响识别率。在此查询所有类型 http://www.yundama.com/price.html
    codetype = 2000
    # 超时时间，秒
    timeout = 60

    if(username == "username"):
        print('请设置好相关参数再测试')

    else:
        yundama = YDMHttp(username, password, appid, appkey)

        # 登陆云打码
        uid = yundama.login();
        print('uid: %s' % uid)

        # 登陆云打码
        uid = yundama.login();
        print ('uid: %s' % uid)

        # 查询余额
        balance = yundama.balance();
        print ('balance: %s' % balance)

        # 开始识别，图片路径，验证码类型ID，超时时间（秒），识别结果
        code = yundama.decode("image/5.png", 2000, 60)
        print(code)













