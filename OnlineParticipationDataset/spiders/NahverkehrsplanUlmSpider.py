import locale
from datetime import datetime
from itertools import count

import scrapy
from scrapy import Selector
from scrapy.http import HtmlResponse


class NahverkehrsplanUlmSpider(scrapy.Spider):
    name = "nahverkehrsplan-ulm"
    start_urls = ['https://www.zukunftsstadt-ulm.de/dialog/hier-konnten-sie-mit-uns-zu-den-einzelnen-bus-und-bahnlinien-diskutieren']

    def __init__(self, *args, **kwargs):
        super(NahverkehrsplanUlmSpider, self).__init__(*args, **kwargs)
        locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')

    def parse(self, response):
        """
        Parse given response and yield items for comments and comments for comments.

        :param response: scrapy response
        :return: generator
        """
        for thread_url in response.css("a.fa-comment::attr('href')").extract():
            yield response.follow(thread_url, parse_forum)


def parse_forum(response: HtmlResponse) -> dict:
    """
    Parse thread and yield a SuggestionItem for each comment,
    see :class:`~OnlineParticipationDataset.items.SuggestionItem`.

    :param response: scrapy response
    :return: generator
    """
    forum = response.css(".node-title::text").extract_first()

    # there could be more comments for the last top level comment on the next page, so we do not yield it directly
    if 'suggestion' in response.meta:
        suggestion = response.meta['suggestion']
        rest_comments = [get_reply(reply, reply_level(reply, response.css("#comments")), forum, suggestion["suggestion_id"])
                         for reply in response.css("section#comments > h3 ~ .indented article")]
        suggestion["comments"].extend(rest_comments)
        yield fix_reply_hierarchy(suggestion)

    comments = response.css("div.comment-wrapper")
    for comment in comments[:-1]:
        yield fix_reply_hierarchy(get_top_level_comment(comment, forum))

    if len(comments) > 0:
        last_comment = get_top_level_comment(comments[-1], forum)

        next_page = response.css(".pager-next a::attr(href)").extract_first()
        if next_page is not None:
            request = response.follow("https://www.zukunftsstadt-ulm.de" + next_page, parse_forum)
            request.meta['suggestion'] = last_comment
            yield request
        else:
            yield fix_reply_hierarchy(last_comment)


def fix_reply_hierarchy(comment_item: dict) -> dict:
    def insert_comment(comment: dict):
        if len(stack) == 0:
            comments.append(comment)
            stack.append(comment)
        elif comment["level"] == stack[-1]["level"] + 1:
            comment["parent_id"] = stack[-1]["comment_id"]
            stack[-1]["children"].append(comment)
            stack.append(comment)
        else:
            stack.pop()
            insert_comment(comment)

    comments = []
    stack = []
    for comment in comment_item["comments"]:
        insert_comment(comment)

    comment_item["comments"] = comments
    return comment_item


def get_top_level_comment(comment: Selector, forum: str) -> dict:
    suggestion_item = dict()
    comment_id = comment.css("article::attr(data-id)").extract_first()
    suggestion_item['suggestion_id'] = comment_id
    suggestion_item['title'] = comment.css("h4 a::text").extract_first()
    date_time_string = comment.css(".submitted").extract_first().split(" am ")[1].split(" Uhr")[0]
    suggestion_item['date_time'] = datetime.strptime(date_time_string, "%d. %b. %Y<br> um %H:%M")
    suggestion_item['forum'] = forum
    suggestion_item['author'] = comment.css(".submitted .username::text").extract_first()
    suggestion_item['content'] = "\n".join(comment.css(".comment-body .field-items p::text").extract())
    suggestion_item['comment_count'] = len(comment.css("h5"))
    suggestion_item['comments'] = get_comments(comment, comment_id, forum)
    return suggestion_item


def get_comments(comment: Selector, comment_id: int, forum: str) -> [dict]:
    return [get_reply(reply, reply_level(reply, comment), forum, comment_id)
            for reply in comment.css(".all-replies article")]


def reply_level(reply: Selector, comment: Selector) -> int:
    for level in count():
        if len(comment.css("%s #%s" % (".indented " * level, reply.root.attrib["id"]))) == 0:
            return level - 1


def get_reply(reply: Selector, level: int, forum: str, top_level_comment_id: int) -> dict:
    comment_item = dict()
    comment_item['suggestion_id'] = top_level_comment_id
    comment_item['level'] = level
    comment_item['comment_id'] = reply.css("article::attr(data-id)").extract_first()
    comment_item['title'] = reply.css("h5 a::text").extract_first()
    date_time_string = reply.css(".submitted").extract_first().split(" am ")[1].split(" Uhr")[0]
    comment_item['date_time'] = datetime.strptime(date_time_string, "%d. %b. %Y<br> um %H:%M")
    comment_item['forum'] = forum
    comment_item['author'] = reply.css(".submitted .username::text").extract_first()
    comment_item['content'] = "\n".join(reply.css(".comment-body .field-items p::text").extract())
    comment_item['children'] = []
    return comment_item
