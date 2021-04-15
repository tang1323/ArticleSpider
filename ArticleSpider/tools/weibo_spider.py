

from selenium import webdriver

browser = webdriver.Chrome(executable_path="D:/解压文件/chromedriver_win32/chromedriver.exe")
browser.get("https://weibo.com/")
import time
time.sleep(10)
browser.find_element_by_xpath('//*[@id="loginname"]').send_keys('13232732408')
browser.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[2]/div/input').send_keys('130796tang')
browser.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[6]/a').click()
time.sleep(4)


for i in range(3):

    browser.execute_script("window.scrollTo(0, document.body.scrollHeight); var lenOfPage=document.body.scrollHeight; return lenOfPage")
    time.sleep(3)




