
from datetime import datetime
from elasticsearch_dsl import DocType, Date, Nested, Boolean, analyzer, InnerObjectWrapper, Completion, Keyword, Text, Integer
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer

from elasticsearch_dsl.connections import connections
connections.create_connection(hosts=["localhost"])



class CustomAnalyzer(_CustomAnalyzer):
    def  get_analysis_definition(self):
        return {}

# lowercase大小写的转换
ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])

# 定义数据是怎么样保存到es中
class ArticleType(DocType):

    # 博客园在线文章类型
    suggest = Completion(analyzer=ik_analyzer)# 搜索时的自动补全功能,但本身代码有问题，所以自己定义了一个CustomAnalyzer类
    title = Text(analyzer="ik_max_word") # 标题
    create_date = Date() # 日期
    url = Keyword()  # 文章网址
    url_object_id = Keyword()
    front_image_url = Keyword() # 封面图片
    front_image_path = Keyword()
    praise_nums = Integer()  # 点赞数
    comment_nums = Integer()  # 评论数
    fav_nums = Integer()  # 收藏数
    tags = Text(analyzer="ik_max_word") # 标签
    content = Text(analyzer="ik_max_word") # 文章内容

    class Meta:
        index = "cnblogs"
        doc_type = "article"



# 运行之后就在es后台生成了叫cnblogs
if __name__ == "__main__":
    ArticleType.init()













