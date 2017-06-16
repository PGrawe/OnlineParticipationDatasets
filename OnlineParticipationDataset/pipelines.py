# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json,os
from datetime import datetime
from scrapy.exporters import JsonLinesItemExporter

path = "downloads"


class OnlineparticipationdatasetPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWriterPipeline(object):

    def open_spider(self, spider):
        if not os.path.isdir(path):
            os.makedirs(path)
        self.file = open("downloads/items_"+spider.name+".json", 'wb')
        self.exporter = JsonLinesItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        if hasattr(item,'date_time'):
            item['date_time'] = item['date_time'].isoformat()
        self.exporter.export_item(item)
        return item

class TreeGenerationPipeline(object):
    def open_spider(self, spider):
        if spider.tree:
            self.data = {}

    def process_item(self,item, spider):
        if spider.tree:
            self.data[item['id']]=item
            if item['parent'] in self.data.keys():
                if item['parent'] != 'None' and item not in self.data[item['parent']]['children']:
                    self.data[item['parent']]['children'].append(item)

    def close_spider(self, spider):
        if spider.tree:
            for id, item in self.data.items():
                if item['parent'] in self.data.keys():
                    if item['parent'] != 'None' and item not in self.data[item['parent']]['children']:
                        self.data[item['parent']]['children'].append(item)
            suggestions = [item for id, item in self.data.items() if item['parent'] == 'None']
            if not os.path.isdir(path):
                os.makedirs(path)
            file = open("downloads/items_tree_" + spider.name + ".json", 'wb')
            exporter = JsonLinesItemExporter(file, encoding='utf-8', ensure_ascii=False)
            exporter.start_exporting()
            for item in suggestions:
                exporter.export_item(item)
            exporter.finish_exporting()
            file.close()