# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from datetime import datetime


class SuggestionItem(scrapy.Item):
    # Item storing data of initial proposal.
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
    post_id = scrapy.Field(default='Unknown')
    post_author = scrapy.Field(default='Unknown')
    post_date_time = scrapy.Field(default=datetime.strptime("01/01/2999 13:37", "%d/%m/%Y %H:%M"))
    post_position = scrapy.Field(default='Unknown')
    post_title = scrapy.Field(default='Unknown')
    post_content = scrapy.Field(default='Unknown')
    post_parent = scrapy.Field(default='Unknown')
    post_children = scrapy.Field(default=[])
