# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from datetime import datetime


class Suggestion(scrapy.Item):
    # Item storing data of initial proposal.
    suggestion_id = scrapy.Field()
    item_type = scrapy.Field()
    author = scrapy.Field()
    date_time = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    category = scrapy.Field()
    suggestion_type = scrapy.Field()
    approval = scrapy.Field()
    refusal = scrapy.Field()
    abstention = scrapy.Field()
    children = scrapy.Field()
    parent = scrapy.Field()
    comment_count = scrapy.Field()
    comments = scrapy.Field()
    tags = scrapy.Field()
    district = scrapy.Field()
    address = scrapy.Field()


class Comment(scrapy.Item):
    # Item storing data of user-comments
    parent = scrapy.Field()
    item_type = scrapy.Field()    
    comment_id = scrapy.Field()
    suggestion_id = scrapy.Field()
    author = scrapy.Field()
    date_time = scrapy.Field()
    vote = scrapy.Field()
    level = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    parent_id = scrapy.Field()
    children = scrapy.Field()
