import scrapy
from OnlineParticipationDataset import items
from datetime import datetime
import re


class Bonn2015Spider(scrapy.Spider):
    name = "bonn2015"
    start_urls = ['https://www.bonn-macht-mit.de/dialog/bürgerbeteiligung-am-haushalt-20152016/bhh/online-diskussion']

    def suggestion_id(self,response):
        return int(re.search('(?:node-)(\d+)',response.xpath('.//div[@class="panel-pane-content-inside"]/article/@class')
            .extract_first())[1])

    def suggestion_author(self,response):
        return response.xpath('.//span[@class="username"]/text()').extract_first().strip()

    def suggestion_title(self,response):
        return response.xpath('.//h2[@class="node__title node-title"]/text()').extract_first().strip()

    def suggestion_category(self, response):
        return response.xpath(
            './/div[@class="additional-infos"]//div[contains(@class,"field-name-field-category")]//div[@class="field-item even"]/text()').extract_first()

    def suggestion_type(self,response):
        return response.xpath(
            './/div[@class="additional-infos"]//div[contains(@class,"field-name-field-proposal-financial-type")]//div[@class="field-item even"]/text()').extract_first()

    def suggestion_content(sef,response):
        content = response.xpath('.//div[contains(@class,"node-main-content")]//p/text()').extract()
        content = [line.strip() for line in content]
        return ''.join(content)

    def suggestion_approval(self,response):
         return int(response.xpath('.//span[@title="Pro votes"]/text()')
            .extract_first())

    def suggestion_refusal(self,response):
        return int(response.xpath('.//span[@title="Contra votes"]/text()')
            .extract_first())

    def suggestion_abstention(self,response):
        return int(response.xpath('.//span[@title="Neutral votes"]/text()')
            .extract_first())

    def suggestion_comment_count(self, response):
        return int(response.xpath('.//span[@class="count-comments count-icon"]/text()')
                .extract_first())
                
    def suggestion_parse_datetime(self, s):
        return datetime.strptime(
            re.sub(r"(\s|[a-z])+", "", s.lower(), flags=re.UNICODE),'%d.%m.%Y')

    def suggestion_datetime(self,response):
        return self.suggestion_parse_datetime(
                response.xpath('.//p[@class="user-and-date inline"]/text()').extract()[1])

    def parse_datetime_comment(self, s):
        s = s.split("|")
        s = "-".join(s[1:])
        return datetime.strptime(
            re.sub(r"(\s|[a-z])+", "", s.lower(), flags=re.UNICODE),'%d.%m.%Y-%H:%M')

    def parse_comment_id(self, s):
        if s is not None:
            return re.search(r"ID\:\D*(\d+)",s)[1]

    def comment_id(self,response):
        return self.parse_comment_id(response.xpath('.//div[@class="col_01"]/comment()').extract_first())

    def parse_comment_id_official(self,s):
        return re.search(r"Nr\.\s*(\d+)",s)[1]

    def comment_id_official(self,response):
        return self.parse_comment_id_official(response.xpath('.//div[@class="user"]/text()').extract_first())

    def comment_content(self,response):
        return response.xpath('.//div[@class="col_01"]/p/text()').extract_first().strip()

    def comment_title(self,response):
        return response.xpath('.//div[@class="col_01"]/h2/text()').extract_first().strip()

    def parse_comment_author(self,s):
        return re.search(r"von\s+(\w+)\s+",s)[1]

    def comment_author(self,response):
        return self.parse_comment_author(response.xpath('.//div[@class="user"]/text()').extract_first())

    def comment_datetime(self,response):
        return self.parse_datetime_comment(response.xpath('.//div[@class="user"]/text()').extract_first())

    def create_comment_item(self, response):
        """
        Create a CommentItem, see :class:`~OnlineParticipationDataset.items.CommentItem`, from given response.

        :param response: scrapy response
        :return: scrapy item
        """
        comment_item = items.CommentItem()
        comment_class = response.xpath('@class').extract_first().replace('kommentar_','').split()

        comment_item['level'] = int(comment_class[0])
        comment_item['comment_id'] = self.comment_id(response)
        comment_item['suggestion_id'] = self.suggestion_id(response.xpath('..'))
        comment_item['content'] = self.comment_content(response)
        comment_item['author'] = self.comment_author(response)
        comment_item['date_time'] = self.comment_datetime(response)
        comment_item['title'] = self.comment_title(response)

        # If official the id is located elsewhere
        # if len < 2 its an answer on a comment with vote
        if(len(comment_class) == 2):
            if "ablehnung" == comment_class[1]:
                comment_item['vote'] = "refusal"
            elif "zustimmung" == comment_class[1]:
                comment_item['vote'] = "approval"
            elif "neutral" == comment_class[1]:
                comment_item['vote'] = "neutral"
            elif "stellungnahme" == comment_class[1] or "verwaltung" == comment_class[1]:

                comment_item['comment_id'] = self.comment_id_official(response)
                comment_item['vote'] = "official"
            else:
                comment_item['vote'] = "misc"
        else:
            comment_item['vote'] = "answer"

        return comment_item

    def parse_comment_tree(self, item_list):
        """
        Parse list with CommentItems, see :class:`~OnlineParticipationDataset.items.CommentItem`, to restore the comment tree. Write parent and children to items. Items need to have values for level, commment_id and suggestion_id.

        :param item_list: list with CommmentItems
        :return list with CommmentItems
        """
        stack = []
        for position,item in enumerate(item_list):
            item['children'] = []
            while(len(stack) >= item['level']):
                stack.pop()
            # Check if not first level, i.e. stack not is empty
            if stack:
                # (pos,id)
                parent_tuple = stack[-1]
                # Parent is the last seen item
                item['parent_id'] = parent_tuple[1]
                # Add current item as child to parent
                item_list[parent_tuple[0]]['children'].append(item)
            else:
                # Top-Level Comments
                item['parent_id'] = item['suggestion_id']
            stack.append(tuple((position,item['comment_id'])))
        return list(filter(lambda x: x['level'] <= 1, item_list))

    def create_comment_item_list(self, response):
        """
        Create a list of CommentItems, see :class:`~OnlineParticipationDataset.items.CommentItem`, from given response.

        :param response: scrapy response
        :return: list with CommentItems
        """
        comment_items = []
        for comment in response.xpath('//div[starts-with(@class,"kommentar")]'):
            comment_items.append(self.create_comment_item(comment))
        return self.parse_comment_tree(comment_items)

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
            yield response.follow(thread_url,self.parse_thread)


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
        suggestion = self.create_suggestion_item(response)
        # suggestion['comments'] = self.create_comment_item_list(response)
        yield suggestion
