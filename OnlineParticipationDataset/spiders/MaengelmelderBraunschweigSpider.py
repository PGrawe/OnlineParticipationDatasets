from typing import Generator

import scrapy
from scrapy import Selector
from scrapy.http import HtmlResponse

from OnlineParticipationDataset import items
from datetime import datetime
import re
import locale

from OnlineParticipationDataset.items import SuggestionItem


class MaengelmelderBraunschweigSpider(scrapy.Spider):
    name = "maengelmelder-braunschweig"
    start_urls = ['https://www.mitreden.braunschweig.de/node/1358']

    def __init__(self, *args, **kwargs):
        super(MaengelmelderBraunschweigSpider, self).__init__(*args, **kwargs)
        locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')

    def parse(self, response: HtmlResponse) -> Generator:
        """
        Parse given response and yield items for post in Maengelmelder Braunschweig.
        """
        for post in response.css("article.with-categories"):
            yield MaengelmelderBraunschweigSpider.parse_post(post)

        next_page = response.css("a[title='Zur nächsten Seite']::attr('href')").extract_first()
        if next_page:
            yield response.follow(next_page, self.parse)

    @staticmethod
    def parse_post(article: Selector) -> SuggestionItem:
        """
        Parse thread and yield a SuggestionItem, see :class:`~OnlineParticipationDataset.items.SuggestionItem`.

        :param response: scrapy response
        :return: generator
        """
        # suggestion = self.create_suggestion_item(response)
        # suggestion['comments'] = self.create_comment_item_list(response, suggestion['suggestion_id'])
        suggestion_item = items.SuggestionItem()
        suggestion_item['suggestion_id'] = article.css("h3 a::attr('href')").extract_first().replace("/node/", "") # TODO page entfernen
        suggestion_item['title'] = article.css("h3 a::text").extract_first()
        suggestion_item['date_time'] = datetime.strptime(article.css("p.user-and-date:first-child::text").extract()[1].strip(), "am %d.%m.%Y")
        suggestion_item['category'] = article.css(".category_button span::text").extract_first().strip()
        suggestion_item['author'] = article.css("span.username::text").extract_first()
        # suggestion_item['approval'] = self.get_suggestion_approval(response)
        suggestion_item['address'] = article.css("p.user-and-date::text")[-1].extract().strip()
        suggestion_item['content'] = article.css(".field p::text").extract_first()
        # suggestion_item['comment_count'] = self.get_suggestion_comment_count(response)
        return suggestion_item
