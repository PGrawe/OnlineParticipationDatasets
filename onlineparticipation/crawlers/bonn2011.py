import scrapy

class Bonn2011Spider(scrapy.Spider):
    name = "bonn2011_spider"
    start_urls = ['http://bonn-packts-an-2011.de/www.bonn-packts-an.de/dito/forumc0d2.html']
