import scrapy
from OnlineParticipationDatasets import items
from OnlineParticipationDatasets.spiders.BonnSpider import BonnSpider
from datetime import datetime
import re
import locale


class Bonn2015Spider(BonnSpider):
    name = "bonn2015"
    start_urls = ['https://www.bonn-macht-mit.de/dialog/bürgerbeteiligung-am-haushalt-20152016/bhh/online-diskussion']

    def __init__(self, *args, **kwargs):
        super(Bonn2015Spider, self).__init__(*args, **kwargs)
