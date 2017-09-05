import scrapy
from OnlineParticipationDataset import items
from datetime import datetime
import re
import locale


class Bonn2015Spider(scrapy.Spider):
    name = "bonn2015"
    start_urls = ['https://www.bonn-macht-mit.de/dialog/bürgerbeteiligung-am-haushalt-20152016/bhh/online-diskussion']
    comment_counter = 0

    def suggestion_id(self, response):
        return int(re.search('(?:node-)(\d+)',response.xpath('.//div[@class="panel-pane-content-inside"]/article/@class')
                             .extract_first())[1])

    def suggestion_author(self, response):
        return response.xpath('.//span[@class="username"]/text()').extract_first().strip()

    def suggestion_title(self, response):
        return response.xpath('.//h2[@class="node__title node-title"]/text()').extract_first().strip()

    def suggestion_category(self, response):
        return response.xpath(
            './/div[@class="additional-infos"]//div[contains(@class,"field-name-field-category")]//div[@class="field-item even"]/text()').extract_first()

    def suggestion_type(self,response):
        return response.xpath(
            './/div[@class="additional-infos"]//div[contains(@class,"field-name-field-proposal-financial-type")]//div[@class="field-item even"]/text()').extract_first()

    def parse_content(self, lines):
        return ''.join(map(lambda s: s.strip(), lines))

    def suggestion_content(self, response):
        return self.parse_content(response.xpath('.//div[contains(@class,"node-main-content")]//p/text()').extract())

    def suggestion_approval(self, response):
         return int(response.xpath('.//span[@title="Pro votes"]/text()')
                    .extract_first())

    def suggestion_refusal(self, response):
        return int(response.xpath('.//span[@title="Contra votes"]/text()')
            .extract_first())

    def suggestion_abstention(self, response):
        return int(response.xpath('.//span[@title="Neutral votes"]/text()')
            .extract_first())

    def suggestion_comment_count(self, response):
        return int(response.xpath('.//span[@class="count-comments count-icon"]/text()')
                .extract_first())
                
    def suggestion_parse_datetime(self, s):
        return datetime.strptime(
            re.sub(r"(\s|[a-z])+", "", s.lower(), flags=re.UNICODE), '%d.%m.%Y')

    def suggestion_datetime(self, response):
        return self.suggestion_parse_datetime(
                response.xpath('.//p[@class="user-and-date inline"]/text()').extract()[1])

    def parse_comment_id(self, s):
        if s is not None:
            return re.search(r"comment\-(\d+)", s)[1]

    def comment_id(self, response):
        return self.parse_comment_id(response.xpath('./@id').extract_first())

    def comment_content(self, response):
        return self.parse_content(response.xpath('./div/div[@class="comment-body"]//p/text()').extract())

    def comment_title(self, response):
        return response.xpath('./div/div[@class="comment-body"]/h3/a/text()').extract_first().strip()

    def comment_author(self, response):
        return response.xpath('./div/div[@class="comment-meta"]//span/text()').extract_first().strip()

    def parse_datetime_comment(self, l):
        s = ' '.join([s.strip() for s in l])
        s = s.replace('von','').strip()
        return datetime.strptime(s, 'am %d. %b. %Y at %H:%MUhr')

    def comment_datetime(self, response):
        return self.parse_datetime_comment(response.xpath('./div/div[@class="comment-meta"]/header/div/text()').extract())

    def create_comment_item(self, response, level=1):
        """
        Create a CommentItem, see :class:`~OnlineParticipationDataset.items.CommentItem`, from given response.

        :param response: scrapy response
        :return: scrapy item
        """
        comment_item = items.CommentItem()

        comment_item['level'] = level
        comment_item['comment_id'] = self.comment_id(response)
        # should obtain it from higher function
        # comment_item['suggestion_id'] = self.suggestion_id(response.xpath('//.'))
        comment_item['content'] = self.comment_content(response)
        comment_item['author'] = self.comment_author(response)
        comment_item['date_time'] = self.comment_datetime(response)
        comment_item['title'] = self.comment_title(response)

        children_list = []

        if level == 1:
            children_xpath = 'following-sibling::div/div[@class="indented"]/article'
        else:
            children_xpath = 'following-sibling::div[@class="indented"]/article'

        for child in response.xpath(children_xpath):
            children_list.append(self.create_comment_item(child, level+1))

        comment_item['children'] = children_list

        return comment_item

    def create_comment_item_list(self, response):
        """
        Create a list of CommentItems, see :class:`~OnlineParticipationDataset.items.CommentItem`, from given response.

        :param response: scrapy response
        :return: list with CommentItems
        """
        locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')
        comment_items = []
        # Get first level comments
        for comment in response.xpath('//section[@id="comments"]/div/article'):
            comment_items.append(self.create_comment_item(comment))
        return comment_items

    def create_suggestion_item(self, response):
        """
        Create a SuggestionItem, see :class:`~OnlineParticipationDataset.items.SuggestionItem`, from given response.

        :param response: scrapy response
        :return: scrapy item
        """
        suggestion_item = items.SuggestionItem()
        suggestion_item['suggestion_id'] = self.suggestion_id(response)
        suggestion_item['author'] = self.suggestion_author(response)
        suggestion_item['title'] = self.suggestion_title(response)
        suggestion_item['category'] = self.suggestion_category(response)
        suggestion_item['suggestion_type'] = self.suggestion_type(response)
        suggestion_item['content'] = self.suggestion_content(response)
        suggestion_item['approval'] = self.suggestion_approval(response)
        suggestion_item['refusal'] = self.suggestion_refusal(response)
        suggestion_item['abstention'] = self.suggestion_abstention(response)
        suggestion_item['comment_count'] = self.suggestion_comment_count(response)
        suggestion_item['date_time'] = self.suggestion_datetime(response)
        return suggestion_item

    def parse(self, response):
        """
        Parse given response and yield items for suggestions and comments of all
        pages of bonn-packts-an-2015.

        :param response: scrapy response
        :return: generator
        """
        for thread in response.xpath('//div[@class="view-content"]//div[@class="node-inside"]'):
            thread_url = thread.xpath('./header/h2/a/@href').extract_first()
            yield response.follow(thread_url, self.parse_thread)


        # Parse next Site
        # next_page = response.xpath(
        #     '//div[@class="item-list"]/ul[@class="pager"]/li[@class="pager-next"]/a/@href').extract_first()
        # if next_page:
        #     yield response.follow(next_page, self.parse)

    def parse_thread(self, response):
        """
        Parse thread and yield a SuggestionItem, see :class:`~OnlineParticipationDataset.items.SuggestionItem`.

        :param response: scrapy response
        :return: generator
        """
        suggestion = self.create_suggestion_item(response)
        suggestion['comments'] = self.create_comment_item_list(response)
        yield suggestion
