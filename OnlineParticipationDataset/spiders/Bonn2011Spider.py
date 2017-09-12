import scrapy
import re
from OnlineParticipationDataset import items
from datetime import datetime


class Bonn2011Spider(scrapy.Spider):
    name = "bonn2011"
    start_urls = ['http://bonn-packts-an-2011.de/www.bonn-packts-an.de/dito/forumc0d2.html']

    def get_suggestion_id(self,response):
        return (re.search('([A-Z]\d+)',response.xpath('.//div[starts-with(@class,"vorschlag")]/h2/text()')
            .extract_first()))[0]

    def get_suggestion_author(self,response):
        return (re.search('(?:von\s)(\w+)',response.xpath('.//div[starts-with(@class,"vorschlag")]/h2/text()')
            .extract_first()))[1]

    def get_suggestion_title(self,response):
        return response.xpath('.//div[@class="col_01"]/h3/text()').extract_first()

    def get_suggestion_category(self,response):
        return response.xpath(
            './/div[starts-with(@class,"vorschlag")]/div[@class="image"]/img/@title').extract_first()

    def get_suggestion_type(self,response):
        return response.xpath('.//div[@class="col_01"]/strong/text()').extract_first()

    def get_suggestion_content(sef,response):
        return response.xpath('.//div[@class="col_01"]/p/text()').extract_first()

    def get_suggestion_summary_response(self,response):
        return response.xpath('.//div[@class="col_01"]/table')

    def get_suggestion_approval(self,response):
         return int(
             self.get_suggestion_summary_response(response).xpath('.//td[starts-with(@id,"votePro")]/text()')
            .extract_first() or 0)

    def get_suggestion_refusal(self,response):
        return int(
            self.get_suggestion_summary_response(response).xpath('.//td[starts-with(@id,"voteContra")]/text()')
            .extract_first())

    def get_suggestion_abstention(self,response):
        return int(
            self.get_suggestion_summary_response(response).xpath('.//td[starts-with(@id,"voteNeutral")]/text()')
            .extract_first())

    def get_suggestion_comment_count(self, response):
        return int(
            # float(response.xpath('count(//div[starts-with(@class,"kommentar")])')
            #       .extract_first()))
                self.get_suggestion_summary_response(response).xpath('.//td[starts-with(.,"Kommentare")]/../td[@class="r"]/text()')
                .extract_first())
                
    def parse_suggestion_tags(self, l):
        return [s.rsplit('(',1)[0].strip() for s in l]

    def get_suggestion_tags(self, response):
        return self.parse_suggestion_tags(response.xpath('.//div[@class="kasten cloud"]/div[@class="text"]//a/text()').extract())

    def parse_datetime(self, s):
        return datetime.strptime(
            re.sub(r"(\s|[a-z])+", "", s.lower(), flags=re.UNICODE),'%d.%m.%Y-%H:%M')

    def get_suggestion_datetime(self,response):
        return self.parse_datetime(
                response.xpath('.//div[@class="details"]/p/text()').extract_first())

    def parse_datetime_comment(self, s):
        s = s.split("|")
        s = "-".join(s[1:])
        return self.parse_datetime(s)

    def parse_comment_id(self, s):
        if s is not None:
            return re.search(r"ID\:\D*(\d+)",s)[1]

    def get_comment_id(self,response):
        return self.parse_comment_id(response.xpath('.//div[@class="col_01"]/comment()').extract_first())

    def parse_comment_id_official(self,s):
        return re.search(r"Nr\.\s*(\d+)",s)[1]

    def get_comment_id_official(self,response):
        return self.parse_comment_id_official(response.xpath('.//div[@class="user"]/text()').extract_first())

    def get_comment_content(self,response):
        return response.xpath('.//div[@class="col_01"]/p/text()').extract_first().strip()

    def get_comment_title(self,response):
        return response.xpath('.//div[@class="col_01"]/h2/text()').extract_first().strip()

    def parse_comment_author(self,s):
        return re.search(r"von\s+(\w+)\s+",s)[1]

    def get_comment_author(self,response):
        return self.parse_comment_author(response.xpath('.//div[@class="user"]/text()').extract_first())

    def get_comment_datetime(self,response):
        return self.parse_datetime_comment(response.xpath('.//div[@class="user"]/text()').extract_first())

    def create_comment_item(self, response, suggestion_id):
        """
        Create a CommentItem, see :class:`~OnlineParticipationDataset.items.CommentItem`, from given response.

        :param response: scrapy response
        :return: scrapy item
        """
        comment_item = items.CommentItem()
        comment_class = response.xpath('@class').extract_first().replace('kommentar_','').split()

        comment_item['level'] = int(comment_class[0])
        comment_item['comment_id'] = self.get_comment_id(response)
        comment_item['suggestion_id'] = suggestion_id
        comment_item['parent_id'] = 0
        comment_item['date_time'] = self.get_comment_datetime(response)
        comment_item['author'] = self.get_comment_author(response)
        comment_item['title'] = self.get_comment_title(response)
        comment_item['content'] = self.get_comment_content(response)

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

                comment_item['comment_id'] = self.get_comment_id_official(response)
                comment_item['vote'] = "official"
            else:
                comment_item['vote'] = "misc"
        else:
            comment_item['vote'] = "answer"

        return comment_item

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

    def create_comment_item_list(self, response, suggestion_id):
        """
        Create a list of CommentItems, see :class:`~OnlineParticipationDataset.items.CommentItem`, from given response.

        :param response: scrapy response
        :return: list with CommentItems
        """
        comment_items = []
        for comment in response.xpath('//div[starts-with(@class,"kommentar")]'):
            comment_items.append(self.create_comment_item(comment, suggestion_id))
        return self.parse_comment_tree(comment_items)

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
        suggestion_item['approval'] = self.get_suggestion_approval(response)
        suggestion_item['refusal'] = self.get_suggestion_refusal(response)
        suggestion_item['abstention'] = self.get_suggestion_abstention(response)
        suggestion_item['tags'] = self.get_suggestion_tags(response)
        suggestion_item['content'] = self.get_suggestion_content(response)
        suggestion_item['comment_count'] = self.get_suggestion_comment_count(response)
        return suggestion_item

    def parse(self, response):
        """
        Parse given response and yield items for suggestions and comments of all
        pages of bonn-packts-an-2011.

        :param response: scrapy response
        :return: generator
        """
        for thread in response.xpath('//div[starts-with(@class,"vorschlag")]'):
            thread_url = thread.xpath('.//div[@class="col_01"]/h3/a/@href').extract_first()
            yield response.follow(thread_url,self.parse_thread)


        # Here: Parse next Site
        next_page = response.xpath('.//div[@class="list_pages"]/a[.="vor"]/@href').extract_first()
        if next_page:
            yield response.follow(next_page,self.parse)

    def parse_thread(self, response):
        """
        Parse thread and yield a SuggestionItem, see :class:`~OnlineParticipationDataset.items.SuggestionItem`.

        :param response: scrapy response
        :return: generator
        """
        suggestion = self.create_suggestion_item(response)
        suggestion['comments'] = self.create_comment_item_list(response, suggestion['suggestion_id'])
        yield suggestion
