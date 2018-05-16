import scrapy
from OnlineParticipationDatasets import items
from OnlineParticipationDatasets.spiders.BonnSpider import BonnSpider
from datetime import datetime
import re
import locale


class Bonn2019Spider(BonnSpider):
    name = "bonn2019"
    start_urls = ['https://www.bonn-macht-mit.de/node/2900']

    def __init__(self, *args, **kwargs):
        super(Bonn2019Spider, self).__init__(*args, **kwargs)
