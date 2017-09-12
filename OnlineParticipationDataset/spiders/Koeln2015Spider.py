import scrapy
from OnlineParticipationDataset import items
from datetime import datetime
import re
import locale


class Koeln2015Spider(scrapy.Spider):
    name = "koeln2015"
    # start_urls = ['https://buergerhaushalt.stadt-koeln.de/2015/buergervorschlaege']
    start_urls = ['https://buergerhaushalt.stadt-koeln.de/2015/buergervorschlaege?&sort_bef_combine=php+ASC']

    def __init__(self, *args, **kwargs):
        super(Koeln2015Spider, self).__init__(*args, **kwargs)
        locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8') 

    def get_suggestion_id(self, response):
        return int(response.xpath('//div[@class="id"]/text()')
                             .extract_first() or 0)

    def get_suggestion_author(self, response):
        return re.search('von (.+),',response.xpath('.//div[@class="grid-7"]/span[@class="meta"]/text()').extract_first())[1]

    def get_suggestion_title(self, response):
        return response.xpath('.//div[@class="grid-7"]/h2/text()').extract_first().strip()

    def get_suggestion_category(self, response):
        return response.xpath(
            './/ul[@class="meta-list"]/li[starts-with(@class,"type")]/text()').extract_first()

    def get_suggestion_district(self,response):
        return response.xpath(
            './/ul[@class="meta-list"]/li[@class="district"]/text()').extract_first()

    def parse_content(self, lines):
        # return ''.join(map(lambda s: s.strip(), lines))
        return ''.join(lines)

    def get_suggestion_content(self, response):
        return self.parse_content(response.xpath('.//div[@class="teaser"]/p/text()').extract())

    def get_suggestion_approval(self, response):
         return int(response.xpath('.//dl[@class="thumb-up-down-rate mode1"]/dd[2]//div[@class="count"]/text()')
                        .extract_first() or 0)

    def get_suggestion_refusal(self, response):
        return int(response.xpath('.//dl[@class="thumb-up-down-rate mode1"]/dd[3]//div[@class="count"]/text()')
                        .extract_first() or 0)

    def parse_suggestion_datetime(self, s):
        return datetime.strptime(
            re.search(r".*,\s(.+)\r",s)[1], '%d. %B - %H:%M').replace(year=2014)

    def get_suggestion_datetime(self, response):
        return self.parse_suggestion_datetime(
                response.xpath('.//div[@class="grid-7"]/span[@class="meta"]/text()').extract_first())

    def parse_comment_id(self, s):
        if s is not None:
            return int(re.search(r"comment\-(\d+)", s)[1],0)

    def get_comment_id(self, response):
        return self.parse_comment_id(response.xpath('preceding-sibling::a/@id').extract()[-1])

    def get_comment_content(self, response):
        return self.parse_content(response.xpath('./div[@class="content"]//p/text()').extract())

    def get_comment_title(self, response):
        return response.xpath('./h3/text()').extract_first().strip()

    def get_comment_author(self, response):
        return response.xpath('./div/span/span/text()').extract_first().strip()

    def parse_datetime_comment(self, l):
        return datetime.strptime(l, ' am %d. %B %Y - %H:%M Uhr')

    def get_comment_datetime(self, response):
        return self.parse_datetime_comment(response.xpath('./div/span/text()').extract()[1])

    def create_comment_item(self, response, suggestion_id, level=1):
        """
        Create a CommentItem, see :class:`~OnlineParticipationDataset.items.CommentItem`, from given response.

        :param response: scrapy response
        :return: scrapy item
        """
        comment_item = items.CommentItem()

        comment_item['level'] = level
        comment_item['comment_id'] = self.get_comment_id(response)
        comment_item['suggestion_id'] = suggestion_id
        if level > 1:
            comment_item['parent_id'] = 0
        comment_item['date_time'] = self.get_comment_datetime(response)
        comment_item['author'] = self.get_comment_author(response)
        comment_item['title'] = self.get_comment_title(response)
        comment_item['content'] = self.get_comment_content(response)

        return comment_item

    def create_comment_item_list(self, response, level=1):
        """
        Create a list of CommentItems, see :class:`~OnlineParticipationDataset.items.CommentItem`, from given response.

        :param response: scrapy response
        :return: list with CommentItems
        """
        comment_items = []
        suggestion_id = self.get_suggestion_id(response)

        if level == 1:
            comment_path = './/div[@id="comments"]/div[starts-with(@class,"comment") or @class="indented"]'
        else: # is indented comment
            comment_path = './div[starts-with(@class,"comment") or @class="indented"]'

        for div in response.xpath(comment_path):
            if div.xpath('@class').extract_first() == "indented":
                # Create indented comment list
                comment_items += self.create_comment_item_list(div,level+1)
            else:
                # create comment
                comment_items.append(self.create_comment_item(div,suggestion_id,level))

        return comment_items

    def parse_comment_tree(self, item_list):
        """
        Parse list with CommentItems, see :class:`~OnlineParticipationDataset.items.CommentItem`, to restore the comment tree. Write parent and children to items. Items need to have values for level, comment_id and suggestion_id.

        :param item_list: list with CommentItems
        :return list with CommentItems
        """
        stack = []
        for position,item in enumerate(item_list):
            item['children'] = []
            while(len(stack) >= item['level']):
                stack.pop()
            # Check if not first level, i.e. stack not is empty
            # i.e. Top-Level got not parent_id
            if stack:
                # (pos,id)
                parent_tuple = stack[-1]
                # Parent is the last seen item
                item['parent_id'] = parent_tuple[1]
                # Add current item as child to parent
                item_list[parent_tuple[0]]['children'].append(item)
            # else:
            #     # Top-Level Comments
            #     item['parent_id'] = item['suggestion_id']
            stack.append(tuple((position,item['comment_id'])))
        return list(filter(lambda x: x['level'] <= 1, item_list))


    def create_suggestion_item(self, response):
        """
        Create a SuggestionItem, see :class:`~OnlineParticipationDataset.items.SuggestionItem`, from given response.

        :param response: scrapy response
        :return: scrapy item
        """
        suggestion_item = items.SuggestionItem()
        suggestion_item['suggestion_id'] = self.get_suggestion_id(response)
        suggestion_item['title'] = self.get_suggestion_title(response)
        suggestion_item['date_time'] = self.get_suggestion_datetime(response)
        suggestion_item['category'] = self.get_suggestion_category(response)
        suggestion_item['author'] = self.get_suggestion_author(response)
        suggestion_item['district'] = self.get_suggestion_district(response)
        suggestion_item['approval'] = self.get_suggestion_approval(response)
        suggestion_item['refusal'] = self.get_suggestion_refusal(response)
        suggestion_item['content'] = self.get_suggestion_content(response)
        suggestion_item['comment_count'] = 0
        suggestion_item['comments'] = []
        return suggestion_item

    def parse(self, response):
        """
        Parse given response and yield items for suggestions and comments of all
        pages of bonn-packts-an-2017.

        :param response: scrapy response
        :return: generator
        """
        for thread in response.xpath('//div[@class="view-content"]/div'):
            thread_url = thread.xpath('./div/h2/a/@href').extract_first()
            yield response.follow(thread_url, self.parse_thread)


        # Parse next Site
        next_page = response.xpath(
            '//div[@class="item-list"]/ul[@class="pager clearfix"]/li[@class="pager-next"]/a/@href').extract_first()
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
        suggestion['comments'] += self.create_comment_item_list(response)
        next_page = response.xpath(
            '//div[@class="item-list"]/ul[@class="pager clearfix"]/li[@class="pager-next"]/a/@href').extract_first()
        if next_page:
            request = response.follow(next_page, self.parse_thread)
            request.meta['suggestion'] = suggestion
            yield request
        else:
            suggestion['comment_count'] = len(suggestion['comments'])
            suggestion['comments'] = self.parse_comment_tree(suggestion['comments'])
            yield suggestion

