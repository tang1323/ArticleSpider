# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

# item的功能是数据传递作用,pipelines的功能是保存数据的作用
from datetime import datetime
import scrapy
import re
import redis
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst,Join, Identity

from ArticleSpider.utils.common import extract_num# 去common调用extract_num这个函数
from ArticleSpider.settings import SQL_DATETIME_FORMAT,SQL_DATE_FORMAT
from models.es_types import ArticleType

from elasticsearch_dsl.connections import connections   # 这是连接es数据库的
from w3lib.html import remove_tags  # 有一些我们获取的字段是分散在一段html中，现在用这个来去除不必要的html


# 通过这个连接上es
es = connections.create_connection(ArticleType._doc_type.using)

# 这个是连接redis的，用来计算每次爬取数据统计加一
redis_cli = redis.StrictRedis(host="localhost")


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

def add_cnblogs(value):# 谁调用这个方法谁后面就有一个-tangming
    return value+"男"


def date_convert(value):
    # 处理时间的格式，datetime类型变成date,而且只取日期
    try:
        create_date = datetime.strptime(value, "%Y/%m/%d").date()
    except Exception as e:
        create_date = datetime.now().date()
        return create_date

def get_nums(value):
    # 把点赞数量或者评论数量变成int类型，这样在数据更好检索
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums

def remove_comment_tags(value):
    # 去掉tag中提取的评论
    # if "评论" in value:
    #     return ""
    # else:
    #     return value
    # value = "三国梦-lk,编辑,收藏"，先split成列表，然后取三国梦-lk
    return value.split(",")[0]


def return_value(value):
    return value


# 知乎和其他网站都可以用这个方法，这是分词用的生成一个suggest
def gen_suggests(index, info_tuple):
    # 根据字符串生成搜索建议数组
    used_words = set()# 为什么要设置一个set，是因为在后面要去重
    suggests = []# 这就是我们要返回的一个数组
    for text, weight in info_tuple:
        if text:
            # 调用es的anlyzer接口分析字符串, 分词和大小的转换
            words = es.indices.analyze(index=index, analyzer="ik_max_word", params={'filter':["lowercase"]}, body=text)
            anylyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"])>1])# 大于一是过滤单个字符的，那是没有意义的
            # 已经存在过的单词过滤掉
            new_works = anylyzed_words - used_words
        else:
            new_works = set()

        if new_works:
            suggests.append({"input":list(new_works), "weight":weight})
    return suggests


# 我们都用这个自定义的itemLoader来做解析，这个是给文章cnblogs的item
class ArticleItemLoader(ItemLoader):
    """
    是用了itemloader才有这个预处理， input_processor，output_processsor
    可以这么来看 Item 和 Itemloader：Item提供保存抓取到数据的容器，而 Itemloader提供的是填充容器的机制。
    第一个是输入处理器（input_processor） ，当这个item，title这个字段的值传过来时，可以在传进来的值上面做一些预处理。
    第二个是输出处理器（output_processor） ， 当这个item，title这个字段被预处理完之后，输出前最后的一步处理。
    """
    # 自定义itemLoader
    default_output_processor = TakeFirst()# list转换成str



class CnblogsArticleItem(scrapy.Item):
    """
    是用了itemloader才有这个预处理， input_processor，output_processsor
    可以这么来看 Item 和 Itemloader：Item提供保存抓取到数据的容器，而 Itemloader提供的是填充容器的机制。
    第一个是输入处理器（input_processor） ，当这个item，title这个字段的值传过来时，可以在传进来的值上面做一些预处理。
    第二个是输出处理器（output_processor） ， 当这个item，title这个字段被预处理完之后，输出前最后的一步处理。
    """
    title = scrapy.Field(
        input_processor = MapCompose(lambda x:x+ "-风骚", add_cnblogs),# 预处理函数,会调用lambda函数,也会拿到一个value值给add_jobbole
    )# 标题

    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert),
        output_processsor = TakeFirst()
    )# 日期

    url = scrapy.Field()# 文章网址

    url_object_id = scrapy.Field()

    front_image_url = scrapy.Field(
        output_processor = MapCompose(return_value)
    )# 封面图片

    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor = MapCompose(get_nums)
    )# 点赞数

    comment_nums = scrapy.Field(
        input_processor = MapCompose(get_nums)
    ) # 评论数

    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    ) # 感兴趣数

    tags = scrapy.Field(
        input_processor = MapCompose(remove_comment_tags),
        # output_processor = Join(",")# list转换成str
    ) # 标签

    content = scrapy.Field() # 文章内容


    def get_insert_sql(self):
        insert_sql = """
                    insert into cnblogs_article(title, url, url_object_id, front_image_url, front_image_path, praise_nums, comment_nums, tags, content, create_date, fav_nums)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)ON DUPLICATE KEY UPDATE create_date = VALUES(create_date)
                """
        params = (
            self.get("title", ""),
            self.get("url", ""),
            self.get("url_object_id", ""),
            self.get("front_image_url", ""),
            self.get("front_image_path", ""),
            self.get("praise_nums", 0),
            self.get("comment_nums", 0),
            self.get("tags", ""),
            self.get("content", ""),
            self.get("create_date", "1970-07-01"),
            self.get("fav_nums", 0),
        )

        return insert_sql, params# 返回到pipelines中的do_insert，因为那里调用了get_sql，得返回去值



    # 将item转换成es的数据
    def save_to_es(self):
        article = ArticleType()
        article.title = self['title']
        article.create_date = self["create_date"]
        article.content = (self["content"])
        if "front_image_url" in self:
            article.front_image_url = self["front_image_url"]
        if "front_image_path" in self:
            article.front_image_path = self["front_image_path"]
        article.praise_nums = self["praise_nums"]
        article.fav_nums = self["fav_nums"]
        article.comment_nums = self["comment_nums"]
        article.url = self["url"]
        article.tags = self["tags"]
        article.id = self["url_object_id"]


        # 生成搜索建议词
        article.suggest = gen_suggests(ArticleType._doc_type.index, ((article.title, 10), (article.tags, 7)))

        article.save()
        # 数据加1操作
        redis_cli.incr("cnblogs_count")

        return






class ZhihuQuestionItem(scrapy.Item):
    # 知乎的问题item
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()# 话题(主题）
    url = scrapy.Field()# url
    content = scrapy.Field()# 提问的内容
    answer_num = scrapy.Field()# 回答的数量
    comments_num = scrapy.Field()# 评论的数量
    watch_user_num = scrapy.Field()# 关注的数量
    click_num = scrapy.Field() # 点击的数量
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        # 这里必须与pipelines下的do_insert()方法下的调用get_insert_sql一致，也与其他网站调用都是写统一的函数。像上面的JobboleArticleItem一样
        insert_sql = """
            insert into zhihu_question(zhihu_id, topics, url, title, content, answer_num, comment_num,
                watch_user_num, click_num, crawl_time
            )VALUES(%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE content = VALUES(content),answer_num = VALUES(answer_num),comments_num = VALUES(comment_num),
            watch_user_num = VALUES(watch_user_num), click_num =VALUES(click_num), crawl_time = VALUES(crawl_time)
        
        """
        zhihu_id = self["zhihu_id"][0]
        topics = ",".join(self["topics"])
        url = self["url"][0]
        title ="".join(self["title"])
        content = "".join(self["content"])
        answer_num = "".join(self["answer_num"])
        comments_num = extract_num("".join(self["comments_num"]))
        watch_user_num = extract_num("".join(self["watch_user_num"]))
        click_num = extract_num("".join(self["click_num"]))
        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)# 上strtime是想把time转换成str类型的



        params = (zhihu_id, topics, url, title, content, answer_num, comments_num, watch_user_num, click_num, crawl_time)
        return insert_sql, params


class ZhihuAnswerItem(scrapy.Item):
    # 知乎的问题回答item
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()# 问题的id
    author_id = scrapy.Field()# 作者的id
    content = scrapy.Field()# 内容
    praise_num = scrapy.Field()#点赞数量
    comments_num = scrapy.Field()# 评论的数量
    create_time = scrapy.Field()# 创建的时间
    update_time = scrapy.Field()# 更新的时间
    crawl_time = scrapy.Field()# 当前我们所获取的时间

    def get_insert_sql(self):
        insert_sql = """
                    insert into zhihu_answer(zhihu_id, url, question_id, author_id, content, praise_num,
                    comment_num, create_num, update_time, crawl_time, crawl_update_time
                    )VALUES(%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE content = VALUES(content), comment_num = VALUES(comment_num), praise_num = VALUES(praise_num),
                    update_time = VALUES(update_time)
                  
                """


        create_time = datetime.datetime.fromtimestamp(self["create_time"]).strftime(SQL_DATETIME_FORMAT)
        update_time = datetime.datetime.fromtimestamp(self["update_time"]).strftime(SQL_DATETIME_FORMAT)

        params = (
            self["zhihu_id"], self["url"], self["question_id"], self["author_id"],self["content"],
            self["praise_num"], self["comments_num"], create_time,update_time,
            self["crawl_time"].strftime(SQL_DATETIME_FORMAT), self["crawl_update_time"]
        )
        return insert_sql, params


def remove_splash(value):
    # 去掉城市的斜线
    return value.replace("/", "")

def remove_one(value):
    # 20:02 发布于拉勾网
    # 这里我们用切分，中间刚好是空格， 这两种都可以
    # return value.split(" ", -2)
    return value.split(" ", 1)

def get_salary(value):
    # 把点赞数量或者评论数量变成int类型，这样在数据更好检索
    # match_re = re.match(".*?(\d+).*", value)
    # 这里解析25K-30K只能取前面的25
    match_re = re.match(r".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
        nums *= 1000
    else:
        nums = 0
    return nums

def date_lagou_convert(value):
    # 处理时间的格式，datetime类型变成date,而且只取日期
    try:
        create_time = datetime.strptime(value, "%Y-%m-%d").date()
    except Exception as e:
        create_time = datetime.now().date()
        return create_time

def handle_jobaddr(value):
    # split() 把\n切分成，隔开成列表
    # strip() 方法用于移除字符串头尾指定的字符（默认为空格或换行符
    addr_list = value.split("\n")
    addr_list = [item.strip() for item in addr_list if item.strip()!="查看地图"]
    # 两者一样，但前面的是列表类型
    # for item in addr_list:
    #     if item.strip() != "查看地图":
    #         item.strip()
    return "".join(addr_list)



# 我们都用这个自定义的itemLoader来做解析
class LagouJobItemLoader(ItemLoader):
    # 自定义itemLoader
    default_output_processor = TakeFirst()# list转换成str

class LagouJobItem(scrapy.Item):
    # 拉勾网职位信息
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    salary = scrapy.Field(
        input_processor=MapCompose(get_salary),
    )
    job_city = scrapy.Field(
        # 调用这个函数，去除在字段不必要的东西， 斜线
        input_processor = MapCompose(remove_splash),
    )
    work_years = scrapy.Field(
        # 调用这个函数，去除在字段不必要的东西， 斜线
        input_processor = MapCompose(remove_splash),
    )
    degree_need = scrapy.Field(
        # 调用这个函数，去除在字段不必要的东西， 斜线
        input_processor = MapCompose(remove_splash),
    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field(
        input_processor = MapCompose(remove_one),
    )
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field()
    job_addr = scrapy.Field(
        # 要提取的字段在html中，所以去除html，剩下的就是要的字段
        # MapCompose里的参数函数是依次进行的
        input_processor = MapCompose(remove_tags, handle_jobaddr),
    )
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    tags = scrapy.Field(
        # 有多个标签，可以用,号隔开，同时也变成字符串
        input_processor = Join(",")
    )
    crawl_time = scrapy.Field(
        # 处理时间的格式，datetime类型变成date,而且只取日期
        # input_processor=MapCompose(date_lagou_convert),

    )

    # 这个函数名要保持一致
    def get_insert_sql(self):
        insert_sql = """
            insert into lagou_job(title, url, url_object_id, salary, job_city, work_years, degree_need,
            job_type, publish_time, job_advantage, job_desc, job_addr, company_name, company_url,
            tags, crawl_time) VALUES  (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE salary=VALUES(salary), job_desc=VALUES(job_desc)
        """
        params = (
            self["title"], self["url"], self["url_object_id"], self["salary"], self["job_city"],
            self["work_years"], self["degree_need"], self["job_type"], self["publish_time"],
            self["job_advantage"], self["job_desc"], self["job_addr"], self["company_name"],
            self["company_url"], self["tags"], self["crawl_time"]
        )
        return insert_sql, params























