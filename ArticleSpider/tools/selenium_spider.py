
# 设置chromedriver不加载图片
from selenium import webdriver
# chrome_opt = webdriver.ChromeOptions()
# prefs = {"profile.managed_default_content_settings.images":2}# 不加载图片的语句
# chrome_opt.add_experimental_option('prefs', prefs)# 不加载图片的语句
# browser = webdriver.Chrome(executable_path="D:/解压文件/chromedriver_win32/chromedriver.exe",chrome_options=chrome_opt)
# browser.get("https://www.taobao.com")


# phantomjs，无界面的浏览器，多进程情况下phantomjs性能下降很严重



browser = webdriver.PhantomJS(executable_path="D:/解压文件/phantomjs-2.1.1-windows/phantomjs-2.1.1-windows/bin/phantomjs.exe")
browser.get("https://detail.tmall.com/item.htm?id=617738137391&ali_trackid=2:mm_50570328_39070332_145428725:1590637180_243_1840856525&spm=a231o.7712113/g.1004.1&pvid=200_11.27.93.104_4234_1590637177315&sku_properties=10004:7169121965;5919063:6536025")

print(browser.page_source)
browser.quit()




