import locale
from datetime import datetime
from typing import Generator

import scrapy
from scrapy.http import HtmlResponse

from OnlineParticipationDatasets import items
from OnlineParticipationDatasets.items import SuggestionItem


class MaengelmelderBraunschweigSpider(scrapy.Spider):
    name = "maengelmelder-braunschweig"
    start_id = 1358
    start_urls = ["https://www.mitreden.braunschweig.de/node/%d" % start_id]
    handle_httpstatus_list = [403, 404]

    def __init__(self, *args, **kwargs):
        super(MaengelmelderBraunschweigSpider, self).__init__(*args, **kwargs)
        locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')

    def parse(self, response: HtmlResponse) -> Generator:
        """
        Parse given response and yield items for post in Maengelmelder Braunschweig.
        """
        next_page = response.css("article.with-categories h3 a::attr('href')").extract_first()
        yield response.follow(next_page, MaengelmelderBraunschweigSpider.parse_posts)

    @staticmethod
    def parse_posts(response: HtmlResponse) -> Generator:
        """
        Parses this post if it belongs to Maengelmelder, and then continues with the previous post until the start url
        is reached.
        """
        if "Mängelmelder" == response.css(".user-date-and-time-icons .icons .fa-comment::text").extract_first():
            yield MaengelmelderBraunschweigSpider.parse_post(response)

        base_url, current_id = response.url.rsplit("/", 1)
        next_id = int(current_id) - 1
        if next_id > MaengelmelderBraunschweigSpider.start_id:
            next_page = "%s/%d" % (base_url, next_id)
            yield response.follow(next_page, MaengelmelderBraunschweigSpider.parse_posts)

    @staticmethod
    def parse_post(response: HtmlResponse) -> SuggestionItem:
        """
        Parse thread and yield a SuggestionItem, see :class:`~OnlineParticipationDataset.items.SuggestionItem`.
        """
        suggestion_item = items.SuggestionItem()
        suggestion_item['suggestion_id'] = response.url.split("/")[-1]
        suggestion_item['title'] = response.css("h2.node-title::text").extract_first()
        suggestion_item['date_time'] = datetime.strptime(response.css("p.user-and-date:first-child::text").extract()[1].strip(), "am %d.%m.%Y")
        suggestion_item['category'] = response.css(".category_button span::text").extract_first().strip()
        suggestion_item['author'] = response.css("span.username::text").extract_first()
        suggestion_item['address'] = response.css("p.user-and-date::text")[-1].extract().strip()
        suggestion_item['content'] = response.css(".field p::text").extract_first()
        return suggestion_item
