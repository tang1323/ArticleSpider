# -*- coding: utf-8 -*-
import scrapy
import requests
import os
import time
import pickle
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from settings import BASE_DIR   # 在settings已经定位好了项目的根目录
from scrapy import Selector

import urllib.request
from io import BytesIO
from PIL import Image   # 这是安装pillow包，专门处理图像的
from selenium.webdriver import ActionChains     # 导入鼠标动作链对象
from ArticleSpider.items import LagouJobItemLoader, LagouJobItem
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from ArticleSpider.utils.common import get_md5


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['http://www.lagou.com/']

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36 Edg/80.0.361.111',
        'origin':'https://www.lagou.com',
        'referer': 'https://www.lagou.com/',
    }

    # 需要登录 的就要cookies_enabled设置为True，在第一个start_url中把cookies带过去给requests, 在下一个requests也会把cookies带上去
    # DOWNLOAD_DELAY:10 每10秒爬取一个
    custom_settings = {
        "COOKIES_ENABLED": True,
        "DOWNLOAD_DELAY": 10
    }

    # 这个是爬虫规则，可以自己自定义
    # 就是设置了一个Rule,它如果匹配这样的url，那它就会去爬取
    rules = (
        # 点进LinkExtractor，有个allow=()，如果这里的allow是符合这样的url我就callback到parse_item提取
        # allow=http://www.lagou.com/jobs/， 这里就不这么写了，前面已经有allowed_domains = ['www.lagou.com']
        # 它会自己urljoin起来
        # follow=True意思是比如这个页面详情有相似职位，它也会深入获取获取
        Rule(LinkExtractor(allow=r'jobs/\d+.html*'), callback='parse_item', follow=True),

        # 随便点进一个java的招聘，http://www.lagou.com/后面跟有guangzhou-zhaopin/这个的都可以爬取，无所谓
        # follow=True意思是比如这个页面详情有相似职位，它也会深入获取获取
        Rule(LinkExtractor(allow=("guangzhou-zhaopin/.*")), follow=True),

        # 点进公司也有一招聘职位，匹配gongsi/j这样的模式它就会去爬取，
        # follow=True意思是比如这个页面详情有相似职位，它也会深入获取获取
        Rule(LinkExtractor(allow=("gongsi/j\d+.html")), follow=True),
    )


    # 这是爬虫的第一个入口点，如果有需要登录的，都会在这用上selenium
    # def start_requests(self):
    #
    #     # 拉勾的帐号和密码
    #     USERNAME = '13232732408'
    #     PASSWORD = 'tang130796'
    #
    #     # 快识别打码的平台
    #     KUAI_USERNAME = 'tang1323'
    #     KUAI_PASSWORD = '130796abc'
    #     # 去使用selenium模拟登录后拿到cookie交给scrapy的request使用
    #     # 1.通过selenium模拟登录
    #     # 如果已经登录拿到cookies了，那就不用每次都要去登录了，从文件中读取cookies
    #     cookies = []
    #     # 检查这个文件是否存在
    #     if os.path.exists(BASE_DIR+"/cookies/lagou.cookie"):
    #         # 用loads打开这个文件
    #         cookies = pickle.loads(open(BASE_DIR+"/cookies/lagou.cookie", "rb"))
    #
    #     # 如果没有cookies才去登录
    #     if not cookies:
    #         from selenium import webdriver
    #         import time
    #         browser = webdriver.Chrome(executable_path="D:/DecomPression-File/chromedriver_win32 (2.45-70)/chromedriver.exe")
    #
    #         browser.maximize_window()
    #         # 先请求login登 录的页面
    #         browser.get("https://www.lagou.com/")
    #         # time.sleep(10000)
    #         browser.find_element_by_xpath('//*[@id="changeCityBox"]/ul/li[4]/a').click()
    #         time.sleep(0.5)
    #
    #         # 点击登录
    #         browser.find_element_by_css_selector("ul.passport a.login").click()
    #         time.sleep(0.5)
    #         # 用css输入帐号密码，是id就用#,是class就用.，
    #         # input[type="password"]是指input标签里面有个属性叫type="password"
    #         # 原本是.forms-top-block forms-top-password，如果有空格就用.连拼接起来
    #         # 原本是.input login_enter_password HtoC_JS，如果有空格就用.连拼接起来
    #         browser.find_element_by_css_selector('.forms-top-block.forms-top-password .input.login_enter_password.HtoC_JS').send_keys("13232732408")
    #         browser.find_element_by_css_selector('.forms-top-block.forms-top-password input[type="password"]').send_keys("tang130796")
    #         browser.find_element_by_css_selector('.login-btn.login-password.sense_login_password.btn-green').click()
    #         # time.sleep(10)
    #
    #         """保存图片到本地项目"""
    #         # page_source就是运行js完后的html网页
    #         sel_css = Selector(text=browser.page_source)
    #         #
    #         # # 这个和bilibili放在一样的路径下,图片标签
    #         img_urls = sel_css.find_element_by_css_selector(".geetest_item_wrap img::attr(src)").extract()
    #
    #
    #         # 用urlretrieve(),下载图片验证码到本地项目
    #         try:
    #             urllib.request.urlretrieve(img_urls, 'D:/BaiduNetdiskDownload/ArticleSpider/lagou_yzm.png')
    #         except:
    #             pass
    #
    #         time.sleep(3)
    #
    #         """这里是对图片以文件的形式打开，主要是为了获取图片的大小"""
    #         # 对图片验证码进行提取,取图片标签,geetest_table_box,geetest_item_img
    #         # 这个也跟bilibili一样，我在这里向上取一级
    #         img_label = browser.find_element_by_css_selector(".geetest_table_box img.geetest_item_img")
    #
    #         """
    #         这个在拉勾可有可无
    #         但是拉勾有三种验证码，汉字点选和物体识别的图片是放在同样的路径下
    #         所以打开这个只是计算图片的大小而已
    #         """
    #         # 获取点触图片链接
    #         src = img_label.get_attribute('src')
    #
    #         # 获取图片二进制内容
    #         img_content = requests.get(src).content
    #         f = BytesIO()
    #         f.write(img_content)
    #
    #         # 将图片以文件的形式打开，主要是为了获取图片的大小
    #         img0 = Image.open(f)
    #
    #         # 获取图片与浏览器该标签大小的比例
    #         scale = [img_label.size['width'] / img0.size[0],
    #                  img_label.size['height'] / img0.size[1]]
    #
    #         """对图片进行识别"""
    #         # 对接打码平台，识别验证码
    #         from ArticleSpider.tools.parse_code import base64_api
    #
    #         img_path = 'lagou_yzm.png'
    #
    #         # 与接口对应
    #         code_result = base64_api(KUAI_USERNAME, KUAI_PASSWORD, img_path)
    #         print("验证码识别结果：", code_result)
    #
    #         # 识别出来的坐标是用|隔开的，现在分隔一下
    #         result_list = code_result.split('|')
    #
    #         position = [[int(j) for j in i.split(',')] for i in
    #                     result_list]  # position = [[110,234],[145,247],[25,185]]
    #         for items in position:  # 模拟点击
    #
    #             # 实现动作链,browser是浏览器的一个对象
    #             # move_to_element_with_offset()翻译是移动到带偏移的元素
    #             # img_label是图片的标签，也是验证码在登录时候的位置
    #             # perform()是执行整个鼠标动作链
    #             ActionChains(browser).move_to_element_with_offset(img_label, items[0] * scale[0],
    #                                                                    items[1] * scale[1]).click().perform()
    #             time.sleep(1)
    #
    #         # 点击确认
    #         browser.find_element_by_css_selector('div.geetest_commit_tip').click()
    #         time.sleep(3)
    #         # 点击登录
    #         try:
    #             browser.find_element_by_css_selector(
    #                 ".login-btn.login-password.sense_login_password.btn-green").click()
    #         except:
    #             pass
    #
    #         # 用get_cookies()获取cookies
    #         cookies = browser.get_cookies()
    #         # 写入cookie到文件中,pickle将文本序列化到文件当中，非常好用的一个库
    #
    #         # BASE_DIR定位到当前项目下，cookies是左边的一个文件夹，wb是以二进制的方式写入到lagou.cookie中
    #         pickle.dump(cookies, open(BASE_DIR+"/cookies/lagou.cookie", "wb"))
    #
    #
    #     # 在else我们要把cookies放到我们的scrapy用
    #     # 但不能直接把cookies交给我们的scrapy.request用
    #     # 我们得到的cookies是一个list,我们要变成dict类型才交给selenium使用用
    #     cookie_dict = {}
    #     for cookie in cookies:
    #         # cookie就是一个对象了
    #         cookie_dict[cookie["name"]] = cookie["value"]
    #
    #     # 这是从spider源码复制过来的，因为start_requests很多
    #     """
    #     是可以停止的函数，它只会运行到第一个yield
    #     不像其他函数那样，会从上向下运行完
    #     所以它会停止。当它再次运行时，会接着从下一个yield的地方再次取数据运行
    #     或者调用它，用next()去获取
    #     scrapy是异步io框架，没有多线程，没有引入消息队列
    #     scrapy是单线程高并发异步io框架
    #     """
    #     for url in self.start_urls:
    #         yield scrapy.Request(url, dont_filter=True, cookie=cookie_dict)

    def start_requests(self):
        return [scrapy.Request('https://www.lagou.com/', callback=self.login)]


    def login(self, response):

        # 拉勾的帐号和密码
        USERNAME = '13232732408'
        PASSWORD = 'tang130796'

        # 快识别打码的平台
        KUAI_USERNAME = 'tang1323'
        KUAI_PASSWORD = '130796abc'


        # 去使用selenium模拟登录后拿到cookie交给scrapy的request使用
        # 1.通过selenium模拟登录
        # 如果已经登录拿到cookies了，那就不用每次都要去登录了，从文件中读取cookies
        cookies = []
        # 检查这个文件是否存在
        if os.path.exists(BASE_DIR+"/cookies/lagou.cookie"):
            # 用pickle.load打开解码这个文件
            cookies = pickle.load(open(BASE_DIR+"/cookies/lagou.cookie", "rb"))

        # 如果没有cookies才去登录
        if not cookies:
            from selenium import webdriver
            import time
            browser = webdriver.Chrome(executable_path="D:/DecomPression-File/chromedriver_win32 (2.45-70)/chromedriver.exe")

            browser.maximize_window()
            # 先请求login登 录的页面
            browser.get("https://www.lagou.com/")
            # time.sleep(10000)
            browser.find_element_by_xpath('//*[@id="changeCityBox"]/ul/li[4]/a').click()
            time.sleep(0.5)

            # 点击登录
            browser.find_element_by_css_selector("ul.passport a.login").click()
            time.sleep(0.5)
            # 用css输入帐号密码，是id就用#,是class就用.，
            # input[type="password"]是指input标签里面有个属性叫type="password"
            # 原本是.forms-top-block forms-top-password，如果有空格就用.连拼接起来
            # 原本是.input login_enter_password HtoC_JS，如果有空格就用.连拼接起来
            browser.find_element_by_css_selector('.forms-top-block.forms-top-password .input.login_enter_password.HtoC_JS').send_keys("13232732408")
            browser.find_element_by_css_selector('.forms-top-block.forms-top-password input[type="password"]').send_keys("tang130796")
            browser.find_element_by_css_selector('.login-btn.login-password.sense_login_password.btn-green').click()
            time.sleep(3)



            """保存图片到本地项目"""
            # page_source就是运行js完后的html网页
            sel_css = Selector(text=browser.page_source)
            print(sel_css)
            #
            # 这个和bilibili放在一样的路径下,图片标签
            img_urls = sel_css.css(".geetest_item_wrap img::attr(src)").extract()[0]


            # 用urlretrieve(),下载图片验证码到本地项目
            try:
                urllib.request.urlretrieve(img_urls, 'D:/BaiduNetdiskDownload/ArticleSpider/lagou_yzm.png')
            except:
                pass

            time.sleep(3)

            """这里是对图片以文件的形式打开，主要是为了获取图片的大小"""
            # 对图片验证码进行提取,取图片标签,geetest_table_box,geetest_item_img
            # 这个也跟bilibili一样，我在这里向上取一级
            img_label = browser.find_element_by_css_selector(".geetest_table_box img.geetest_item_img")

            """
            这个在拉勾可有可无
            但是拉勾有三种验证码，汉字点选和物体识别的图片是放在同样的路径下
            所以打开这个只是计算图片的大小而已
            """
            # 获取点触图片链接
            src = img_label.get_attribute('src')

            # 获取图片二进制内容
            img_content = requests.get(src).content
            f = BytesIO()
            f.write(img_content)

            # 将图片以文件的形式打开，主要是为了获取图片的大小
            img0 = Image.open(f)

            # 获取图片与浏览器该标签大小的比例
            scale = [img_label.size['width'] / img0.size[0],
                     img_label.size['height'] / img0.size[1]]

            """对图片进行识别"""
            # 对接打码平台，识别验证码
            from ArticleSpider.tools.parse_code import base64_api

            img_path = 'D:\\BaiduNetdiskDownload\\ArticleSpider\\lagou_yzm.png'

            # 与接口对应
            code_result = base64_api(KUAI_USERNAME, KUAI_PASSWORD, img_path)
            print("验证码识别结果：", code_result)

            # 识别出来的坐标是用|隔开的，现在分隔一下
            result_list = code_result.split('|')

            position = [[int(j) for j in i.split(',')] for i in
                        result_list]  # position = [[110,234],[145,247],[25,185]]
            for items in position:  # 模拟点击

                # 实现动作链,browser是浏览器的一个对象
                # move_to_element_with_offset()翻译是移动到带偏移的元素
                # img_label是图片的标签，也是验证码在登录时候的位置
                # perform()是执行整个鼠标动作链
                ActionChains(browser).move_to_element_with_offset(img_label, items[0] * scale[0],
                                                                       items[1] * scale[1]).click().perform()
                time.sleep(1)

            # 点击确认
            browser.find_element_by_css_selector('div.geetest_commit_tip').click()
            time.sleep(3)
            # 点击登录
            try:
                browser.find_element_by_css_selector(
                    ".login-btn.login-password.sense_login_password.btn-green").click()
            except:
                pass

            # 用get_cookies()获取cookies,变里获取的是一个对象
            cookies = browser.get_cookies()
            # 写入cookie到文件中,pickle将文本序列化到文件当中，非常好用的一个库

            # BASE_DIR定位到当前项目下，cookies是左边的一个文件夹，wb是以二进制的方式写入到lagou.cookie中
            pickle.dump(cookies, open(BASE_DIR+"/cookies/lagou.cookie", "wb"))


        # 在else我们要把cookies放到我们的scrapy用
        # 但不能直接把cookies交给我们的scrapy.request用
        # 我们得到的cookies是一个list,我们要变成dict类型才交给selenium使用
        cookie_dict = {}
        for cookie in cookies:
            # cookie就是一个对象了，里面有name和value
            cookie_dict[cookie["name"]] = cookie["value"]

        # 然后这里每一个url都要带上我们的cookies,所以做一个遍历
        for url in self.start_urls:
            yield scrapy.Request(url, dont_filter=True, cookies=cookie_dict)





    def parse_item(self, response):
        # 解析拉勾网的职位
        # 1.要想无界面启动selenium，先设置headless模式
        chrome_options = Options()  # 实例化这个Options(),要在webdriver.Chrome加上参数
        chrome_options.add_argument("--headless")  # 这个就是无界面启动selenium，一定要写的
        chrome_options.add_argument("--disable-gpu")  # 谷歌文档提到需要加上这个属性来规避bug

        # 2.设置selenium不加载图片, blink-settings=imagesEnabled=false是固定的
        # chrome_options.add_argument("blink-settings=imagesEnabled=false")

        """
        1.启动chrome（启动之前确保所有的chrome实例己经关闭）
        """
        browser = webdriver.Chrome(
            executable_path="D:/DecomPression-File/chromedriver_win32 (2.45-70)/chromedriver.exe",
            chrome_options=chrome_options)

        # 把得到的url给这里
        browser.get(response.url)

        # page_source就是运行js完后的html网页
        temp_xc = Selector(text=browser.page_source)

        time.sleep(3)
        # 实例化一个对象， LagouJobItem是拉勾的item
        # Lg = LagouJobItem()
        # item_loader = LagouJobItemLoader(item=LagouJobItem(), response=response)

        # print(response.text)
        # title = item_loader.add_css("title", ".position-head-wrap-name::text()")
        title = temp_xc.css(".job-name::attr(title)").extract_first("")
        print(type(title))

        # item_loader.add_css("url", response.url)
        # item_loader.add_css("url_object_id")
        url_object_id = get_md5(response.url)


        LG = LagouJobItem()
        LG["title"] = title
        LG["url"] = response.url
        LG["url_object_id"] = url_object_id


        return LG















