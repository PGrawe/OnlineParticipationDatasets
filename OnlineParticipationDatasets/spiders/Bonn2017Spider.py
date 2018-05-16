import scrapy
from OnlineParticipationDatasets import items
from OnlineParticipationDatasets.spiders.BonnSpider import BonnSpider
from datetime import datetime
import re
import locale


class Bonn2017Spider(BonnSpider):
    name = "bonn2017"
    start_urls = ['https://www.bonn-macht-mit.de/node/871']

    def __init__(self, *args, **kwargs):
        super(Bonn2017Spider, self).__init__(*args, **kwargs)
