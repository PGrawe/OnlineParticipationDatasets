# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json,os
from datetime import datetime

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
        self.outfile = open("downloads/items_"+spider.name+".json", 'w')
        self.item_list = []

    def close_spider(self, spider):
        '''
        Closes json file on spider closing
        :param spider: Spider scraping
        :return: None
        '''
        json.dump(self.item_list, self.outfile, indent=2)
        self.outfile.close()

    def comment_dict(self, item):
        if type(item['date_time']) is datetime:
            item['date_time'] = item['date_time'].isoformat()
        if item['children']:
            item['children'] = [self.comment_dict(comment) for comment in item['children']]
        return dict(item)

    def process_item(self, item, spider):
        '''
        Exports item to json-file. Converts dates into iso-format.
        :param item: Item to be saved
        :param spider: Spider scraping items
        :return: Item
        '''
        if 'date_time' in item:
            item['date_time'] = item['date_time'].isoformat()
        item['comments'] = [self.comment_dict(comment) for comment in item['comments']]
        self.item_list.append(dict(item))
        # json.dump(dict(item), self.outfile, indent=2)
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
        exporter = JsonLinesItemExporter(file, encoding='utf-8', ensure_ascii=False)
        exporter.start_exporting()
        for item in suggestions:
            exporter.export_item(item)
        exporter.finish_exporting()
        file.close()

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
