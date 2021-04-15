


# import requests
# try:
#     import cookielib
# except:
#     import http.cookiejar as cookielib
#
# import re
#
# session = requests.session()
# session.cookies = cookielib.LWPCookieJar(filename='cookies.txt')
#
# try:
#     session.cookies.load(ignore_discard=True)
# except:
#     print("cookie未能加载完成")
#
#
#
#
# agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
# header = {
#     "HOST": "www.zhihu.com",
#     "Referer": "https://www.zhihu.com",
#     "User-Agent": agent
# }
#
# def is_login():
#     # 通过个人中心页面返回状态来判断是来否为登录状态
#     inbox_url = "https://www.zhihu.com/inbox"
#     response = session.get(inbox_url, headers=header, allow_redirects=False)
#     if response.status_code != 200:
#         return False
#     else:
#         return True
#
#
# def get_xsrf():
#     # 选取_xsrf_code
#     response = requests.get("https://www.zhihu.com", headers = header)
#     match_obj = re.match('.*name="_xsrf" value="(.*?)"', response.text)
#     if match_obj:
#         return(match_obj.group(1))
#     else:
#         return ""
#
#
# def get_index():
#     response = session.get("https://www.zhihu.com", headers=header)
#     with open("index_page.html", "wb") as f:
#         f.write(response.text.encode("utf-8"))
#     print("ok")
#
#
# def zhihu_login(account, password):
#     # 知乎登录
#     if re.match("^1\d{10}", account):
#         print("手机号码登录")
#         post_url = "https://www.zhihu.com/login/phone_num"
#         post_data = {
#             "_xsrf": get_xsrf(),
#             "phone_num": account,
#             "password": password
#         }
#     else:
#         if "@" in account:
#             # 判断用户是否为邮箱
#             print("邮箱方式登录")
#             post_url = "https://www.zhihu.com/email"
#             post_data = {
#                 "_xsrf":get_xsrf(),
#                 "email":account,
#                 "password": password
#             }
#     response_text = session.post(post_url, data=post_data, headers=header)
#     session.cookies.save()
# get_xsrf()
# zhihu_login("13232732408", "tangming130796")
#
# get_index()
#
# is_login()
#
#
#
#
#



from selenium import webdriver
from scrapy.selector import Selector

browser = webdriver.Chrome(executable_path="D:/解压文件/chromedriver_win32/chromedriver.exe")


browser.get("https://www.zhihu.com/signin?next=%2F")

browser.find_element_by_css_selector("div#root div.SignFlow-tabs>div:nth-child(2)").click()
# browser.find_element_by_xpath("//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[1]/div[2]").click()
browser.find_element_by_xpath("//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[2]/div/label/input").send_keys("13232732408")
browser.find_element_by_css_selector(".Input-wrapper input[name='password']").send_keys("tangming130796")
browser.find_element_by_xpath("//*[@id='root']/div/main/div/div/div/div[1]/div/form/button").click()



print(browser.page_source)











