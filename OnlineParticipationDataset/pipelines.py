# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
from datetime import datetime


class OnlineparticipationdatasetPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWriterPipeline(object):

    def open_spider(self, spider):
        self.file = open('downloads/items' + spider.name + '.json', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        item_dict = dict(item)
        item_dict['date_time'] = item_dict['date_time'].isoformat()
        line = json.dumps(item_dict) + "\n"
        self.file.write(line)
        return item
