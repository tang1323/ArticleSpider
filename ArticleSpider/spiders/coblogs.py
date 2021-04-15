# -*- coding: utf-8 -*-
import re
import scrapy
import datetime
from scrapy.http import Request
from urllib import parse

from ArticleSpider.items import CnblogsArticleItem,ArticleItemLoader
from ArticleSpider.utils.common import get_md5
import requests
import json


class CnblogsSpider(scrapy.Spider):
    name = 'cnblogs'
    allowed_domains = ['www.cnblogs.com']
    start_urls = ['https://www.cnblogs.com/']

    # 需要登录 的就要cookies_enabled设置为True,在第一个start_url中把cookies带过去给requests, 在下一个requests也会把cookies带上去
    # DOWNLOAD_DELAY下载速度10秒一次
    custom_settings = {
        "COOKIES_ENABLED": True,
        "DOWNLOAD_DELAY": 5
    }
    def parse(self, response):
        # /html/body/div[3]/div[3]/div[1]/div[1]#这是jsp页面加载后的一个xpath，是不对，如果想获取到正常值，得到检查里获取，得到以下那一行xpath语法，则是正确
        # // *[ @ id = "post-110287"] / div[1] / h1
        # re_selector = response.xpath("/html/body/div[3]/div[3]/div[1]/div[1]/h1")
        # re3_selector = response.xpath('//div[@class="entry-header"/h1/text()')# 现在这种xpath语法不再适用了
        """
        1. 获取文章列表中的文章url并交给scrapy下载并进行解析
        2. 获取下一页的url并交给scrapy进行下载，下载完成后交给parse


        :param response:
        :return:
        """

        # extract_first 提取list中第一个元素，若为空list，则返回默认值

        post_nodes = response.css('.post-item .post-item-text')  # 是id就用#,是class就用.,这是获取页面的所有链接
        for post_node in post_nodes:# 一个一个解析出来
            image_url = post_node.css('.post-item-text .post-item-summary img::attr(src)').extract_first("")#解析出图片url
            if image_url.startswith("//"):
                image_url = "https:"+image_url
            # print(image_url)
            post_url = post_node.css('.post-item-text a::attr(href)').extract_first("")#解析出文章的url
            # print(post_url)
            # 拿到post_url就要交给request，不要全部拿到才交给request
            yield Request(url=parse.urljoin(response.url,post_url),meta={"front_image_url":image_url},  callback=self.parse_detail)


        # 提取下一页并交给scrapy进行下载
        next_url = response.css('div.pager a:last-child::text').extract_first("")
        yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)
        if next_url == ">":
            next_url = response.css('div.pager a:last-child::attr(href)').extract_first("")
            # 拿到下一页的url又交给callback=self.parse函数获取post_url
            # 这里要用yield生成器来做
            """
            是可以停止的函数，它只会运行到第一个yield
            不像其他函数那样，会从上向下运行完
            所以它会停止。当它再次运行时，会接着从下一个yield的地方再次取数据运行
            或者调用它，用next()去获取
            scrapy是异步io框架，没有多线程，没有引入消息队列
            scrapy是单线程高并发异步io框架
            """
            yield Request(url=parse.urljoin(response.url, next_url),callback=self.parse)


    def parse_detail(self,response):
        match_re = re.match(".*?(\d+)", response.url)
        if match_re:
            # article_item = CnblogsArticleItem()
            # # 标题
            # title = response.css("#cb_post_title_url span::text").extract_first("")
            #
            # # 发布时间
            # create_date = response.css(".postDesc #post-date ::text").extract_first("")
            #
            # # 内容, 要获取这个html因为有的是图片，所以extract()[0]获取html能把所有获取到
            # content_res = response.css("#topics").extract()
            # content = ",".join(content_res)# 之前是List但在mysql不支持list类型，所以这个是转换成字符串类型的
            #
            # # 阅读数
            # favs_res = response.css("#post_view_count ::text").extract()
            # fav_nums = ",".join(favs_res)
            #
            # # 评论数
            # comment = response.css("#post_comment_count ::text").extract()
            # comment_nums = ",".join(comment)
            #
            # # 以前是标签，现在是作者了
            # tags = response.css(".postDesc a::text").extract()[0]
            #
            # # 感兴趣数
            # praise = response.css("#post_view_count ::text").extract()
            # praise_nums = ",".join(praise)
            #
            #
            #
            # article_item["url"] = response.url
            # article_item["title"] = title
            # article_item["create_date"] = create_date
            # article_item["content"] = content
            # article_item["fav_nums"] = fav_nums
            # article_item["comment_nums"] = comment_nums
            # article_item["tags"] = tags
            # if response.meta.get("front_image_url", ""):
            #     article_item["front_image_url"] = [response.meta.get("front_image_url", "")]
            # else:
            #     article_item["front_image_url"] = []
            # article_item["praise_nums"] = praise_nums
            # article_item["url_object_id"] = get_md5(article_item["url"])




            item_loader = ArticleItemLoader(item=CnblogsArticleItem(), response=response)
            item_loader.add_css("title", "#cb_post_title_url span::text")
            item_loader.add_css("content", "#cnblogs_post_body")
            item_loader.add_css("create_date", "#post-date ::text")
            item_loader.add_css("tags", ".postDesc a::text")
            item_loader.add_value("comment_nums", "#post_comment_count ::text")
            item_loader.add_value("praise_nums", "#post_view_count ::text")
            item_loader.add_value("fav_nums", "#post_view_count ::text")
            item_loader.add_value("url", response.url)
            if response.meta.get("front_image_url", []):
                item_loader.add_value("front_image_url", response.meta.get("front_image_url", []))
            item_loader.add_value("url_object_id", get_md5(response.url))

            article_item = item_loader.load_item()


            yield article_item








            # post_id = match_re.group(1)#得到这个网址的id
            # html = requests.get(url=parse.urljoin(response.url, "/chinaWu/ajax/CategoriesTags.aspx?blogId={}&postId={}".format(post_id)))
            # j_tag = json.loads(html.text)
            # print(j_tag)
            # pass
            # yield Request(url=parse.urljoin(response.url, "/kason/ajax/GetViewCount.aspx?postId={}".format(post_id)))


    # def parse_nums(self, response):
    #     j_data = json.loads(response.text)
    #     pass






















        # 解析列表页中的所有文章url并交给scrapy下载后并进行解析
        # post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        # for post_node in post_nodes:
        #     image_url = post_node.css("img::attr(src)").extract_first("")
        #     post_url = post_node.css("::attr(href)").extract_first("")
        #     yield Request(url=parse.urljoin(response.url, post_url),meta = {"front_image_url":image_url}, callback = self.parse_detail)
        #     # print(post_url)
        #
        # # 提取下一页并交给scrapy进行下载
        # next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
        # if next_url:
        #     yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    # def parse_detail(self, response):
    #     article_item = JobBoleArticleItem()
    #
    #     通过css选择器提取字段
    #     # front_image_url = response.meta.get("front_image_url", "")# 文章封面图
    #
    #     # 通过item loader加载item
    #     front_image_url = response.meta.get("front_image_url", "")# 文章封面图
    #     item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response = response)
    #     item_loader.add_css("title",".entry-header h1::text")# 提取标题
    #     # item_loader.add_xpath()
    #     item_loader.add_value("url",response.url)
    #     item_loader.add_value("url_object_id",get_md5(response.url))
    #     item_loader.add_css("create_date", "p.entry-meta-hide-on-mobile::text")# 提取日期
    #     item_loader.add_value("front_image_url", [front_image_url])# 文章封面图
    #     item_loader.add_css("praise_nums", ".vote-post-up h10::text")# 点赞数
    #     item_loader.add_css("comment_nums","a[href='#article-comment'] span::text")# 评论数
    #     item_loader.add_css("fav_nums", ".bookmark-btn::text")# 收藏数
    #     item_loader.add_css("tags", "p.entry-meta-hide-on-mobile a::text")# 标签列表
    #     item_loader.add_css("content", "div.entry")# 文章内容
    #
    #     article_item = item_loader.load_item()
    #
    #
    #     yield article_item




