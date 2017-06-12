# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from datetime import datetime


class SuggestionItem(scrapy.Item):
    # Item storing data of initial proposal.
    id = scrapy.Field(default = 'Unknown')
    author = scrapy.Field(default='Unknown')
    date_time = scrapy.Field(default=datetime.strptime("01/01/2999 13:37", "%d/%m/%Y %H:%M"))
    title = scrapy.Field(default='Unknown')
    suggestion = scrapy.Field(default='Unknown')
    category = scrapy.Field(default='Unknown')
    suggestion_type = scrapy.Field(default='Unknown')
    pro = scrapy.Field(default=0)
    contra = scrapy.Field(default=0)
    neutral = scrapy.Field(default=0)
    num_comments = scrapy.Field(default=0)


class CommentItem(scrapy.Item):
    # Item storing data of user-comments
    id = scrapy.Field(default='Unknown')
    suggestion_id = scrapy.Field(default='Unknown')
    author = scrapy.Field(default='Unknown')
    date_time = scrapy.Field(default=datetime.strptime("01/01/2999 13:37", "%d/%m/%Y %H:%M"))
    vote = scrapy.Field(default='Unknown')
    level = scrapy.Field(default=0)
    title = scrapy.Field(default='Unknown')
    content = scrapy.Field(default='Unknown')
    parent = scrapy.Field(default='Unknown')
    children = scrapy.Field(default=[])
