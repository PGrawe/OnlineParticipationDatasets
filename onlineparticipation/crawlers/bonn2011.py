import scrapy

class Bonn2011Spider(scrapy.Spider):
    name = "bonn2011_spider"
    start_urls = ['http://bonn-packts-an-2011.de/www.bonn-packts-an.de/dito/forumc0d2.html?id=71&gpvId=-1&action=bhhbrowserjournalshow&articlelabel=&sorter_type=1&filter_type=0&fulltext=&order_type=newest&page_num=0']
