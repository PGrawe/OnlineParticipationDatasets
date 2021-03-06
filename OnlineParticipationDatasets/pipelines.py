# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import copy
import os
from abc import ABC, abstractmethod
import urllib.parse as up

from scrapy.exporters import JsonItemExporter

import pymongo
# import sqlalchemy

path = "downloads"


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
        if 'comments' not in item:
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

# class SQLPipeline(AbstractFlatWriterPipeline):

#     def __init__(self, db_url, stats=None):
#         self.db_url = db_url
#         self.stats = stats

#     @classmethod
#     def from_crawler(cls, crawler):
#         return cls(
#             db_url=crawler.settings.get('DB_URL', 'postgres://localhost:5432'),
#             stats=crawler.stats
#         )

#     def open_spider(self, spider):
#         parsed_url = up.urlparse(self.db_url)
#         if parsed_url.scheme != 'sqlite':
#             parsed_url = parsed_url._replace(path=f'/{spider.name}')
#             self.db_url = up.urlunparse(parsed_url)
#         self.engine = sqlalchemy.create_engine(self.db_url)

class MongoPipeline(AbstractFlatWriterPipeline):

    def __init__(self, mongo_host, mongo_port, stats=None):
        self.mongo_host = mongo_host
        self.mongo_port = mongo_port
        self.stats = stats
        # self.collections = ['items','suggestions']

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_host=crawler.settings.get('MONGO_HOST'),
            mongo_port=crawler.settings.get('MONGO_PORT'),
            stats=crawler.stats
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_host, self.mongo_port)
        self.db = self.client[spider.name]

    def close_spider(self, spider):
        if self.stats is not None:
            self.db['crawling_stats'].insert_one(self.stats.get_stats())
        # for collection in self.db.collection_names(False):
        #     if collection.endswith('_'):
        #         self.db[collection].rename(collection[:-1], dropTarget=True)
        self.client.close()

    def export_item(self, item):
        export_dict = dict(item)
        export_dict['_id'] = export_dict.pop(type(item).__name__.lower()+'_id')
        # self.db[type(item).__name__.lower() + 's_'].insert_one(export_dict)
        self.db[type(item).__name__.lower() + 's'].replace_one({'_id': export_dict['_id']},export_dict, upsert=True)
        return item


class JsonWriterPipeline(object):
    '''
    Pipeline for storing scraped items in plain json
    '''
    def open_spider(self, spider):
        '''
        Creates json-file in downloads folder on spider starting.
        Output file is named: items_<spider_name>.json
        :param spider: Spider scraping items
        :return: None
        '''
        if not os.path.isdir(path):
            os.makedirs(path)
        self.outfile = open("downloads/items_"+spider.name+".json", 'wb')
        self.exporter = JsonItemExporter(self.outfile,
                                         encoding='utf-8',
                                         ensure_ascii=False,
                                         indent=2)
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
        Creates json-file in downloads folder on spider starting.
        Output file is named: items_<spider_name>_flat.json
        :param spider: Spider scraping items
        :return: None
        '''
        if not os.path.isdir(path):
            os.makedirs(path)
        self.outfile = open("downloads/items_"+spider.name+"_flat.json", 'wb')
        self.exporter = JsonItemExporter(self.outfile,
                                         encoding='utf-8',
                                         ensure_ascii=False,
                                         indent=2)
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
