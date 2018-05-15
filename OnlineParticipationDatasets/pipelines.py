# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import copy
import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime

from scrapy.exporters import JsonItemExporter

import pymongo

path = "downloads"


class OnlineparticipationdatasetsPipeline(object):
    def process_item(self, item, spider):
        return item

class AbstractFlatWriterPipeline(ABC):

    @abstractmethod
    def open_spider(self, spider):
        pass

    @abstractmethod
    def close_spider(self, spider):
       pass

    def flatten(self, item):
        """Flat a given crapy item

            Creates list with suggestion and all its comments, all on one level.
        """
        if not 'comments' in item:
            return [item]
        item_list = item.pop('comments')
        i = 0
        # XXX List is changed while iterating it
        while i < len(item_list):
            # insert the children in between, right after the parent
            if 'children' in item_list[i]:
                comment_children = item_list[i].pop('children')
                item_list = item_list[:i+1] + comment_children + item_list[i+1:]
            i += 1
        return [item] + item_list

    def process_item(self, item, spider):
        '''
        Exports item to json-file.
        :param item: Item to be saved
        :param spider: Spider scraping items
        :return: Item
        '''
        item_list = self.flatten(copy.deepcopy(item))
        for obj in item_list:
            self.export_item(obj)
        return item
    
    @abstractmethod
    def export_item(self, item):
        pass

class JsonWriterPipeline(object):
    '''
    Pipeline for storing scraped items in plain json
    '''
    def open_spider(self, spider):
        '''
        Creates json-file in downloads folder on spider starting. Output file is named: items_<spider_name>.json
        :param spider: Spider scraping items
        :return: None
        '''
        if not os.path.isdir(path):
            os.makedirs(path)
        self.outfile = open("downloads/items_"+spider.name+".json", 'wb')
        self.exporter = JsonItemExporter(self.outfile, encoding='utf-8', ensure_ascii=False, indent=2)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        '''
        Closes json file on spider closing
        :param spider: Spider scraping
        :return: None
        '''
        self.exporter.finish_exporting()
        self.outfile.close()

    def process_item(self, item, spider):
        '''
        Exports item to json-file.
        :param item: Item to be saved
        :param spider: Spider scraping items
        :return: Item
        '''
        self.exporter.export_item(item)
        return item


class FlatJsonWriterPipeline(AbstractFlatWriterPipeline):
    '''
    Pipeline for storing scraped items in plain json
    '''
    def open_spider(self, spider):
        '''
        Creates json-file in downloads folder on spider starting. Output file is named: items_<spider_name>_flat.json
        :param spider: Spider scraping items
        :return: None
        '''
        if not os.path.isdir(path):
            os.makedirs(path)
        self.outfile = open("downloads/items_"+spider.name+"_flat.json", 'wb')
        self.exporter = JsonItemExporter(self.outfile, encoding='utf-8', ensure_ascii=False, indent=2)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        '''
        Closes json file on spider closing
        :param spider: Spider scraping
        :return: None
        '''
        self.exporter.finish_exporting()
        self.outfile.close()

    def export_item(self, item):
        self.exporter.export_item(item)
