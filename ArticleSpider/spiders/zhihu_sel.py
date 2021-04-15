# -*- coding: utf-8 -*-
import scrapy
import re

import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
# import json
# import datetime

try:
    import urlparse as parse# 这是在python2版本中的
except:
    from urllib import parse# 这是在python3版本中的
# from scrapy.loader import ItemLoader
# from ArticleSpider.items import ZhihuQuestionItem, ZhihuAnswerItem

class ZhihuSpider(scrapy.Spider):

    name = 'zhihu_sel'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/signin?next=%2F']



    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B*%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_info%2Cpaid_info_content%3Bdata%5B*%5D.mark_infos%5B*%5D.url%3Bdata%5B*%5D.author.follower_count%2Cbadge%5B*%5D.topics&offset={1}&limit={2}&sort_by=default&platform=desktop"
    headers = {
        "Host" : "www.zhihu.com",
        "Referer": "https://www.zhihu.com",
        'User-Agent':"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3080.5 Safari/537.36"

    }
    # 需要登录 的就要cookies_enabled设置为True
    custom_settings = {
        "COOKIES_ENABLED": True
    }

    def parse(self, response):
        pass


    def parse_question(self, response):
        pass

    def parse_answer(self, response):
        pass

    def start_requests(self):
        from selenium import webdriver
        # from selenium.webdriver.common.action_chains import ActionChains
        # from selenium.webdriver.chrome.options import Options
        from mouse import move, click


        """
        1.启动chrome（启动之前确保所有的chrome实例己经关闭）
        """
        chrome_options = Options()
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_experimental_option("excludeSwitches",['enable-automation'])
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")


        browser = webdriver.Chrome(executable_path="D:/DecomPression-File/chromedriver_win32 (2.45-70)/chromedriver.exe")

        try:
            browser.maximize_window()
        except:
            pass
        browser.get("https://www.zhihu.com/signin?next=%2F")
        browser.find_element_by_xpath("//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[1]/div[2]").click()

        browser.find_element_by_xpath("//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[2]/div/label/input").send_keys(Keys.CONTROL + "a")
        browser.find_element_by_xpath("//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[2]/div/label/input").send_keys("15218229343")

        browser.find_element_by_xpath("//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[3]/div/label/input").send_keys(Keys.CONTROL + "a")
        browser.find_element_by_xpath("//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[3]/div/label/input").send_keys("12345678m")
        browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[1]/div/form/button').click()
        # browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[1]/div/form/button').click()

        time.sleep(3)
        while True:
            browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[1]/div/form/button').click()
            has_en = False
            has_cn = False
            try:
                browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[1]/div/form/div[4]/div/div[2]/img')
                has_cn = True#中文
            except:
                pass

            try:
                browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[1]/div/form/div[4]/div/span/div/img')
                has_en = True#英文
            except:
                pass

            if has_cn or has_en:
                break


        time.sleep(3)



        #未登录前为false
        login_success = False
        while not login_success:
            try:
                notify_element = browser.find_element_by_class_name("Popover AppHeader-menu")
                login_success = True
            except:
                pass

            try:
                english_captcha_element = browser.find_element_by_class_name("Captcha-englishImg")#如果是英文验证码
            except:
                english_captcha_element = None

            try:
                chinese_captcha_element = browser.find_element_by_class_name("Captcha-chineseImg")#如果是中文验证码

            except:
                chinese_captcha_element = None


            # 这个是中文验证码的登录
            if chinese_captcha_element:
                # 精准获取xy坐标
                ele_postion = chinese_captcha_element.location
                x_relative = ele_postion["x"]
                y_relative = ele_postion["y"] + 25

                #但是他的计算方法并不是从窗口那里开始获取的，所以下面是固定的代码，可以去掉窗口位置,
                browser_navigation_panel_height = browser.execute_script(
                    'return window.outerHeight - window.innerHeight;'
                )#browser_navigation_panel_height就是地址栏的高度


                #做一个图片保存转换
                base64_text = chinese_captcha_element.get_attribute("src")
                import base64
                code = base64_text.replace("data:image/jpg;base64,",'').replace("%0A", "")# 获取文本后的前边的文本替换成空的，但是这个base64和一般的base64不太一样，还多了一段%0A，所以也要替换掉
                # print("这是中文验证码：")
                # print(code)

                fh = open("yzm_cn.jpeg", "wb")#保存这个图片叫yzm_cn.jpg
                fh.write(base64.b64decode(code))

                fh.close()

                from zheye import zheye
                z = zheye()
                positions = z.Recognize("yzm_cn.jpeg")


                pos_arr = []
                if len(positions) == 2:
                    if positions[0][1] > positions[1][1]:
                        pos_arr.append([positions[1][1], positions[1][0]])
                        pos_arr.append([positions[0][1], positions[0][0]])

                    else:
                        pos_arr.append([positions[0][1], positions[0][0]])
                        pos_arr.append([positions[1][1], positions[1][0]])
                else:
                    pos_arr.append([positions[0][1], positions[0][0]])



                if len(positions) == 2:
                    # 有两个倒立文字
                    first_position = [int(pos_arr[0][0] / 2), int(pos_arr[0][1] / 2)]   # 原始图片在zheye项目的相比小一半，所以除以2，这是第一个元素
                    second_position = [int(pos_arr[1][0] / 2), int(pos_arr[1][1] / 2)]  # 原始图片在zheye项目的相比小一半，所以除以2，这是第二个元素
                    move((x_relative + first_position[0]), y_relative + browser_navigation_panel_height + second_position[1])# 这是点击第一个元素
                    click()
                    move((x_relative + second_position[0]),y_relative + browser_navigation_panel_height + second_position[1])#这是点击第二个元素
                    click()
                else:

                    # 这是有一个倒立文字
                    first_position = [int(pos_arr[0][0] / 2),int(pos_arr[0][1] / 2)]  # 原始图片在zheye项目的相比小一半，所以除以2，这是第一个元素
                    move((x_relative + first_position[0]),y_relative + browser_navigation_panel_height + first_position[1])  # 这是点击第一个元素
                    click()


                #再做一次登录
                browser.find_element_by_xpath("//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[1]/div[2]").click()
                browser.find_element_by_xpath("//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[2]/div/label/input").send_keys(Keys.CONTROL +"a")
                browser.find_element_by_xpath("//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[2]/div/label/input").send_keys("15218229343")

                browser.find_element_by_xpath("//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[3]/div/label/input").send_keys(Keys.CONTROL + "a")
                browser.find_element_by_xpath("//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[3]/div/label/input").send_keys("12345678m")
                # browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[1]/div/form/button').click()



            # 英文验证码
            if english_captcha_element:

                # 做一个图片保存转换
                base64_text = english_captcha_element.get_attribute("src")
                import base64
                code = base64_text.replace("data:image/jpg;base64,",'').replace("%0A","")  # 获取文本后的前边的文本替换成空的，但是这个base64和一般的base64不太一样，还多了一段%0A，所以也要替换掉
                fh = open("yzm_en.jpeg", "wb") # 保存这个图片叫yzm_en.jpg

                fh.write(base64.b64decode(code))
                fh.close()

                from ArticleSpider.tools.chaojiying import Chaojiying_Client
                Chaojiying = Chaojiying_Client("1171242903", "130796abc", "905526")
                im = open('D:\BaiduNetdiskDownload\ArticleSpider\yzm_en.jpeg','rb').read()
                code = Chaojiying.PostPic(im, 1902)
                print("英文验证码:")
                print(code)

             #做一个while循环，怕一次不成功识别，循环到成功，再做一个break
                while True:
                    if code == "":
                        chaojiying = Chaojiying_Client('1171242903', '130796abc', '905526')
                        im = open('D:\BaiduNetdiskDownload\ArticleSpider\yzm_en.jpeg', 'rb').read()
                        code = chaojiying.PostPic(im, 1902)
                        print("chaojiyingshibie结果:")
                        print(code)
                    else:
                        break

                # browser.find_element_by_css_selector('.SignFlow-password input').send_keys(Keys.CONTROL + "a")
                browser.find_element_by_xpath(
                    '//*[@id="root"]/div/main/div/div/div/div[1]/div/form/div[4]/div/div/label/input').send_keys(
                    code["pic_str"])

                browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(Keys.CONTROL + "a")
                browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys("15218229343")

                browser.find_element_by_css_selector(".SignFlow-password input").send_keys(Keys.CONTROL + "a")
                browser.find_element_by_css_selector(".SignFlow-password input").send_keys("12345678m")
                # submit_ele = browser.find_element_by_css_selector(".Button.SignFlow-submitButton")
                browser.find_element_by_css_selector(".Button.SignFlow-submitButton").click()

            time.sleep(10)
        try:
            notify_element = browser.find_element_by_xpath('//*[@id="Popover17-toggle"]/img')
            login_success = True

            Cookies = browser.get_cookies()
            print(Cookies)
            cookie_dict = {}
            import pickle
            for cookie in Cookies:
                #写入文件
                #此处大家修改一下自己的文件所在路径
                f = open('./ArticleSpider/cookies/zhihu/' + cookie['name'] + '.zhihu', 'wb')
                pickle.dump(cookie,f)
                f.close()
                cookie_dict[cookie['name']] = cookie['value']
            browser.close()
            return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict)]
        except:
            pass











    # question的第一页answer的请求url
    # start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit={1}&offset={2}&sort_by=default"
    #
    # header = {
    #     "HOST": "www.zhihu.com",
    #     "Referer": "https://www.zhihu.com",
    #     "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
    # }








    # def parse(self, response):# 第五步才是爬虫的真正逻辑，有深度优先逻辑爬虫
    #     """
    #     提取出html页面的所有url 并跟踪这些url进行一步爬取
    #     如果提取的Url中格式为 /question/xxx 就下载之后直接进入解析函数
    #
    #     :param response:
    #     :return:
    #     """
    #     all_urls = response.css("a::attr(href)").extract()
    #     all_urls = [parse.urljoin(response.url, url) for url in all_urls]
    #     all_urls = filter(lambda x:True if x.startswith("https") else False, all_urls)# 如果是https的话返回一个True,如果 不是则返回 一个false
    #     for url in all_urls:
    #         print(url)
    #         match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
    #         if match_obj:
    #             # 如果提取到question相关的页面则下载后交由提取函数进行提取
    #             request_url = match_obj.group(1)
    #             yield scrapy.Request(request_url,headers= self.header,callback=self.parse_question)# 只有写的是yield才能到下载器下载,parse_question只能传函数的名称过来，一定不能传函数的调用
    #         else:
    #             # 如果不是question页面则直接进一步跟踪
    #             yield scrapy.Request(url, headers=self.header,callback=self.parse)# yield 可以看成是一个深度优先的一个入口
    #
    #
    # def parse_question(self, response):
    #     # 处理question页面，从页面中提取出具体的question item
    #
    #     if "QuestionHeader-title" in response.text:
    #         # 处理新版本
    #         match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
    #         if match_obj:
    #
    #             question_id = int(match_obj.group(2))# 知乎id是int 类型
    #         item_loader = ItemLoader(item=ZhihuQuestionItem(), response= response)
    #         item_loader.add_css("title", "h1.QuestionHeader-title::text")
    #         item_loader.add_css("content", ".QuestionHeader-datail")
    #         item_loader.add_css("url", response.url)
    #         item_loader.add_value("zhihu_id", question_id)
    #         item_loader.add_css("answer_num", ".List-headerText span::text")
    #         item_loader.add_css("comment_num", ".Question-Comment button::text")
    #         item_loader.add_css("watch_user_item", "//*[@class='NumberBoard-itemInner']/div/strong/text()")
    #         item_loader.add_css("topics", ".QuestionHeader-topics .Popover div::text")
    #
    #         question_id = item_loader.loader_item()
    #
    #
    #     else:
    #         # 处理旧版本的item
    #         match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
    #         if match_obj:
    #             question_id = int(match_obj.group(2))  # 知乎id是int 类型
    #         item_loader = ItemLoader(item=ZhihuAnswerItem(), response=response)
    #         item_loader.add_css("title", ".zh-question-title h2 a::text")
    #         item_loader.add_css("content", "#zh-question-detail")
    #         item_loader.add_css("url", response.url)
    #         item_loader.add_value("zhihu_id", question_id)
    #         item_loader.add_css("answer_num", "#zh-question-answer-num::text")
    #         item_loader.add_css("comment_num", "#zh-question-meta-wrap a[name='addcomment']::text")
    #         item_loader.add_css("watch_user_item", "#zh-question-side-header-wrap::text")
    #         item_loader.add_css("topics", ".zm-tag-editor-labels a::text")
    #
    #         question_item = item_loader.loader_item()
    #
    #     yield scrapy.Request(self.start_answer_url.format(question_id, 20, 0),headers=self.header, callback=self.parse_answer)
    #     yield question_item # 很重要：如果是yield出去是一个item,会交给pipelines来处理，如果yield出去是一个question,则交给下载器去下载
    #
    # def parse_answer(self, response):
    #     # 处理question的answer
    #     ans_json = json.loads(response.text)
    #     is_end = ans_json["paging"]["is_end"]
    #     totals_answer = ans_json["paging"]["totals"]
    #     next_url = ans_json["paging"]["next"]
    #
    #     #提取answer的具体字段
    #     for answer in ans_json["data"]:
    #         answer_item = ZhihuAnswerItem()
    #         answer_item["zhihu_id"] = answer["id"]
    #         answer_item["url"] = answer["url"]
    #         answer_item["question_id"] = answer["question"]["id"]
    #         answer_item["author_id"] = answer["author"]["id"] if "id" in answer["author"] else None# 有时候用户匿名，如果不是匿名则返回一个author_id,如果 是匿名则一个None
    #         answer_item["content"] = answer["content"] if "content" in answer else None
    #         answer_item["praise_num"] = answer["voteup_count"]
    #         answer_item["comment_num"] = answer["comment_count"]# 评论数量
    #         answer_item["create_time"] = answer["created_time"]# 创建的时间
    #         answer_item["update_time"] = answer["updated_time"]# 更新的时间
    #         answer_item["crawl_time"] =datetime.datetime.now()
    #
    #
    #         yield answer_item
    #
    #
    #     if not is_end:# 如果没有is_end，就继续请求next_url
    #         yield scrapy.Request(next_url, headers=self.header, callback=self.parse_answer)
    #
    #
    #
    # def start_requests(self):# 入口，第一步
    #     return [scrapy.Request('https://www.zhihu.com/signup?next=%2F', headers=self.header,callback=self.login)]# 调用login
    #
    #
    # def login(self, response):# 登录第二步
    #     response_text = response.text
    #     match_obj = re.match('.*name="_xsrf" value="(.*?)"', response.text, re.DOTALL)
    #     _xsrf = ''
    #     if match_obj:
    #         _xsrf = (match_obj.group(1))
    #     if _xsrf:
    #         post_url = "https://zhihu-web-analytics.zhihu.com/api/v1/logs/batch"
    #         post_data = {
    #             "_xsrf": _xsrf,
    #             "phone_num":"13232732408",
    #             "password":"tangming130796"
    #         }
    #         return [scrapy.FormRequest( # 第三步
    #             url = post_url,
    #             formdata = post_data,
    #             headers = self.header,
    #             callback = self.check_login
    #
    #         )]
    # def check_login(self,response):# 第四步
    #     # 验证服务器的返回数据判断是否成功
    #     text_json = json.loads(response.text)
    #     if "msg" in text_json and text_json["msg"] == "登录成功":
    #         for url in self.start_urls:
    #             yield scrapy.Request(url, dont_filter=True, headers= self.header)





