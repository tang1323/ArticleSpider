



from scrapy.cmdline import execute

import sys
import os



# print(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# execute(["scrapy", "crawl", "cnblogs"])
# execute(["scrapy", "crawl", "zhihu_sel"])

# execute(["scrapy", "crawl", "lagou"])
execute(["scrapy", "crawl", "lagou_cooike_pool"])














