import scrapy
from OnlineParticipationDataset import items
from OnlineParticipationDataset.spiders.Bonn2017Spider import Bonn2017Spider
from datetime import datetime
import re
import locale


class Bonn2019Spider(Bonn2017Spider):
    name = "bonn2019"
    start_urls = ['https://www.bonn-macht-mit.de/node/2900']

    def __init__(self, *args, **kwargs):
        super(Bonn2019Spider, self).__init__(*args, **kwargs)
