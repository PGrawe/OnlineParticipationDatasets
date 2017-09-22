import scrapy
from OnlineParticipationDataset import items
from datetime import datetime
import re
import locale


class Koeln2012Spider(scrapy.Spider):
    name = "koeln2012"
    start_urls = ['https://buergerhaushalt.stadt-koeln.de/2012/diskussion']

    def __init__(self, *args, **kwargs):
        super(Koeln2012Spider, self).__init__(*args, **kwargs)
        locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8') 

    def get_suggestion_id(self, response):
        return int(response.xpath('//span[@class="id"]/text()').extract_first() or 0)

    def get_suggestion_author(self, response):
        return response.xpath('//h3/strong/text()').extract_first()

    def get_suggestion_title(self, response):
        return response.xpath('.//h2[@class="title"]/text()').extract_first().strip()

    def get_suggestion_category(self, response):
        return response.xpath('.//div[@class="proposal_category"]/text()').extract_first().replace("Kategorie: ","")
    
    def get_suggestion_type(self, response):
        return response.xpath('.//div[@class="proposal_type"]/text()').extract_first()

    def get_suggestion_district(self,response):
        return response.xpath('.//div[@class="proposal_district"]/text()').extract_first().replace("Stadtbezirk: ","")

    def parse_content(self, lines):
        # return ''.join(map(lambda s: s.strip(), lines))
        return ' '.join(lines)

    def get_suggestion_content(self, response):
        return self.parse_content(response.xpath('.//div[@class="proposal_body"]/p/text()').extract())

    def get_suggestion_approval(self, response):
         return int(response.xpath('.//span[@class="value-1-data"]/text()')
                        .extract_first().replace(',','') or 0)

    def get_suggestion_refusal(self, response):
        return int(response.xpath('.//span[@class="value-3-data"]/text()')
                        .extract_first() or 0)
                
    def parse_suggestion_datetime(self, s):
        return datetime.strptime(s, '%d.%m.%Y - %H:%M Uhr')

    def get_suggestion_datetime(self, response):
        return self.parse_suggestion_datetime(
                response.xpath('.//span[@class="proposal_timestamp"]/text()').extract_first())

    def get_suggestion_comment_count(self, response):
        return int(response.xpath('.//td[@class="data"]/span/text()').extract_first() or 0)

    def parse_comment_id(self, s):
        if s is not None:
            return int(re.search(r"node\-(\d+)", s)[1],0)

    def get_comment_id(self, response):
        return self.parse_comment_id(response.xpath('./div/@id').extract_first())

    def get_comment_content(self, response):
        return self.parse_content(response.xpath('.//div[@class="content"]/p/text()').extract())

    def get_comment_title(self, response):
        return response.xpath('.//div[@class="content"]/h3/text()').extract_first().strip()

    def get_comment_author(self, response):
        return re.search(r"von\s(.*)\sam\s", response.xpath('.//span[@class="submitted"]/text()').extract_first())[1]

    def parse_datetime_comment(self, l):
        return datetime.strptime(re.search(r"am\s(\d+.*)", l.strip())[1], '%d. %B %Y - %H:%M')

    def get_comment_datetime(self, response):
        return self.parse_datetime_comment(response.xpath('.//span[@class="submitted"]/text()').extract_first())

    def get_comment_vote(self, response):
        return response.xpath('.//span[@rel="tag"]/text()').extract_first()

    def create_comment_item(self, response, suggestion_id):
        """
        Create a CommentItem, see :class:`~OnlineParticipationDataset.items.CommentItem`, from given response.

        :param response: scrapy response
        :return: scrapy item
        """
        comment_item = items.CommentItem()

        comment_item['comment_id'] = self.get_comment_id(response)
        comment_item['suggestion_id'] = suggestion_id
        comment_item['date_time'] = self.get_comment_datetime(response)
        comment_item['author'] = self.get_comment_author(response)
        comment_item['title'] = self.get_comment_title(response)
        comment_item['content'] = self.get_comment_content(response)

        vote = self.get_comment_vote(response)
        if vote == "sonstiges":
            comment_item['vote'] = 'misc'
        elif vote == 'unterstützt den Vorschlag':
            comment_item['vote'] = 'approval'
        elif vote == 'lehnt Vorschlag ab':
            comment_item['vote'] = 'refusal'
        elif response.xpath(
                './/div[@class="field-label"]/text()').extract_first() == 'Kommentarlabel:\xa0':
            comment_item['vote'] = 'offical'
        else:
            comment_item['vote'] = 'answer'

        return comment_item

    def create_comment_item_list(self, response, suggestion_id):
        """
        Create a list of CommentItems, see :class:`~OnlineParticipationDataset.items.CommentItem`, from given response.

        :param response: scrapy response
        :return: list with CommentItems
        """
        comment_items = []

        comment_path = '//div[contains(@class,"comments")]/div[@class="view-content"]/div'

        for div in response.xpath(comment_path):
            comment_items.append(self.create_comment_item(div,suggestion_id))

        return comment_items

    def create_suggestion_item(self, response):
        """
        Create a SuggestionItem, see :class:`~OnlineParticipationDataset.items.SuggestionItem`, from given response.

        :param response: scrapy response
        :return: scrapy item
        """
        suggestion_item = items.SuggestionItem()
        suggestion_item['suggestion_id'] = self.get_suggestion_id(response)
        suggestion_item['title'] = self.get_suggestion_title(response)
        suggestion_item['suggestion_type'] = self.get_suggestion_type(response)
        suggestion_item['date_time'] = self.get_suggestion_datetime(response)
        suggestion_item['category'] = self.get_suggestion_category(response)
        suggestion_item['author'] = self.get_suggestion_author(response)
        suggestion_item['district'] = self.get_suggestion_district(response)
        suggestion_item['approval'] = self.get_suggestion_approval(response)
        suggestion_item['refusal'] = self.get_suggestion_refusal(response)
        suggestion_item['content'] = self.get_suggestion_content(response)
        suggestion_item['comment_count'] = self.get_suggestion_comment_count(response)
        suggestion_item['comments'] = []
        return suggestion_item

    def parse(self, response):
        """
        Parse given response and yield items for suggestions and comments of all
        pages of bonn-packts-an-2017.

        :param response: scrapy response
        :return: generator
        """
        for thread_url in response.xpath('//div[@class="view-content"]/div//p/a/@href').extract():
            yield response.follow(thread_url, self.parse_thread)


        # Parse next Site
        next_page = response.xpath(
            '//div[@class="item-list"]/ul[@class="pager"]/li[@class="pager-next"]/a/@href').extract_first()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_thread(self, response):
        """
        Parse thread and yield a SuggestionItem, see :class:`~OnlineParticipationDataset.items.SuggestionItem`.

        :param response: scrapy response
        :return: generator
        """
        if 'suggestion' in response.meta:
            suggestion = response.meta['suggestion']
        else:
            suggestion = self.create_suggestion_item(response)
        # get comments of current page
        suggestion['comments'] += self.create_comment_item_list(response, suggestion['suggestion_id'])
        next_page = response.xpath(
            '//div[@class="item-list"]/ul[@class="pager clearfix"]/li[@class="pager-next"]/a/@href').extract_first()
        if next_page:
            request = response.follow(next_page, self.parse_thread)
            request.meta['suggestion'] = suggestion
            yield request
        else:
            yield suggestion

