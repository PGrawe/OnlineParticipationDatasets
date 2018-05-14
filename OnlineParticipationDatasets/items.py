# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from datetime import datetime


class SuggestionItem(scrapy.Item):
    # Item storing data of initial proposal.
    id=scrapy.Field(default='Unknown')
    suggestion_id = scrapy.Field(default='Unknown')
    author = scrapy.Field(default='Unknown')
    date_time = scrapy.Field(default=datetime.strptime("01/01/2999 13:37", "%d/%m/%Y %H:%M"))
    title = scrapy.Field(default='Unknown')
    content = scrapy.Field(default='Unknown')
    category = scrapy.Field(default='Unknown')
    suggestion_type = scrapy.Field(default='Unknown')
    approval = scrapy.Field(default=0)
    refusal = scrapy.Field(default=0)
    abstention = scrapy.Field(default=0)
    children = scrapy.Field(default=[])
    parent = scrapy.Field(default='None')
    comment_count = scrapy.Field(default=0)
    comments = scrapy.Field(default=[])
    tags = scrapy.Field(default=[])
    district = scrapy.Field(default='Unknown')
    address = scrapy.Field(default='Unknown')


class CommentItem(scrapy.Item):
    # Item storing data of user-comments
    parent = scrapy.Field(default ='Unknown')
    id = scrapy.Field(default='Unknown')
    comment_id = scrapy.Field(default='Unknown')
    suggestion_id = scrapy.Field(default='Unknown')
    author = scrapy.Field(default='Unknown')
    date_time = scrapy.Field(default=datetime.strptime("01/01/2999 13:37", "%d/%m/%Y %H:%M"))
    vote = scrapy.Field(default='Unknown')
    level = scrapy.Field(default=0)
    title = scrapy.Field(default='Unknown')
    content = scrapy.Field(default='Unknown')
    parent_id = scrapy.Field(default='Unknown')
    children = scrapy.Field(default=[])
