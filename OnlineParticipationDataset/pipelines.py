# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
from datetime import datetime
import copy
import logging
from scrapy.exporters import JsonItemExporter

path = "downloads"


class OnlineparticipationdatasetPipeline(object):
    def process_item(self, item, spider):
        return item


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


class FlatJsonWriterPipeline(object):
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

    def flatten(self,item):
        """Flat a given crapy item

            Creates list with suggestion and all its comments, all on one level.
        """
        item_list = item.pop('comments')
        i = 0
        # XXX List is changed while iterating it
        while i < len(item_list):
            # insert the children in between, right after the parent
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
            self.exporter.export_item(obj)
        return item


class TreeGenerationPipeline(object):
    '''
    Pipeline generating nested json output file according to discussion-tree structure coded in items
    '''
    def open_spider(self, spider):
        '''
        Initializes tree-reference
        :param spider: Spider scraping items
        :return: None
        '''
        self.data = {}
        self.stats={spider.name:datetime.now()}

    def process_item(self,item, spider):
        '''
        Adds all items to dict self.data and links items to their parents as children when possible (First pass of tree-generation).
        :param item: Item to be added to dict
        :param spider: Spider scraping items
        :return: Item
        '''
        self.data[item['id']]=item
        if item['parent'] in self.data.keys():
            if item['parent'] != 'None' and item not in self.data[item['parent']]['children']:
                self.data[item['parent']]['children'].append(item)

    def close_spider(self, spider):
        '''
        Updates dict self.data in order to link all children items to their parent (Second pass of tree-generation). Exports result to json in downloads-folder(filename: items_tree_<spider_name>.json)
        :param spider: Spider scraping items
        :return: None
        '''
        for id, item in self.data.items():
            if item['parent'] in self.data.keys():
                if item['parent'] != 'None' and item not in self.data[item['parent']]['children']:
                    self.data[item['parent']]['children'].append(item)
        suggestions = [item for id, item in self.data.items() if item['parent'] == 'None']
        self.sort_data(suggestions)
        if not os.path.isdir(path):
            os.makedirs(path)
        file = open("downloads/items_tree_" + spider.name + ".json", 'wb')
        exporter = JsonItemExporter(file, encoding='utf-8', ensure_ascii=False)
        exporter.start_exporting()
        for item in suggestions:
            exporter.export_item(item)
        exporter.finish_exporting()
        file.close()
        #TODO: Logging in own pipeline
        logging.info(suggestions)
        self.stats[spider.name]=datetime.now()-self.stats[spider.name]
        time_string = 'Total time elapsed for scraping: '+ str(self.stats[spider.name])
        logging.info(time_string)
        items_string = 'Total amount of scraped items: suggestions: '+str(spider.suggestions_counter)+', comments: '+str(spider.comments_counter)
        logging.info(items_string)

    def sort_data(self, suggestions):
        '''
        Sorts self.data (items) by date. (In place)
        :param suggestions: List of top level suggestion items.
        :return: Ordered list of top level suggestion items (by date).
        '''
        for suggestion in suggestions:
            if suggestion['children']:
                self.sort_children(suggestion['children'])
        return suggestions

    def sort_children(self, children):
        '''
        Sorts children items by date (In place)
        :param children: list of children items
        :return: None
        '''
        children.sort(key=lambda k: k['date_time'])
        for child in children:
            if child['children']:
                self.sort_children(child['children'])
