# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SuggestionItem(scrapy.Item):
    # Item storing data of initial proposal.
    title = scrapy.Field()
    proposal = scrapy.Field()
    category = scrapy.Field()
    proposal_type = scrapy.Field()
    est_volume_first = scrapy.Field()
    est_volume_second = scrapy.Field()
    pro = scrapy.Field()
    contra = scrapy.Field()
    neutral = scrapy.Field()
    num_comments = scrapy.Field()


class CommentItem(scrapy.Item):
    # Item storing data of user-comments
    post_id = scrapy.Field()
    post_author = scrapy.Field()
    post_time = scrapy.Field()
    post_position = scrapy.Field()
    post_title = scrapy.Field()
    post_content = scrapy.Field()
    post_parent = scrapy.Field()
