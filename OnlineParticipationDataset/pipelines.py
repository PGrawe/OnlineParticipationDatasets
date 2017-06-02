# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
from datetime import datetime
from scrapy.exporters import JsonLinesItemExporter


class OnlineparticipationdatasetPipeline(object):
    def process_item(self, item, spider):
        return item




class JsonWriterPipeline(object):

    def open_spider(self, spider):
        self.file = open("items_"+spider.name+".json", 'wb')
        self.exporter = JsonLinesItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item