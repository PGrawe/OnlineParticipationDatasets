import scrapy
from OnlineParticipationDataset import items
from datetime import datetime
import re


class Bonn2011Spider(scrapy.Spider):
    name = "bonn2011"
    start_urls = ['http://bonn-packts-an-2011.de/www.bonn-packts-an.de/dito/forumc0d2.html']

    def suggestion_id(self,response):
        return (re.search('([B,V]\d+)',response.xpath('.//div[@class="vorschlag buergervorschlag"]/h2/text()')
            .extract_first()))[0]

    def suggestion_author(self,response):
        return (re.search('(?:von\s)(\w+)',response.xpath('.//div[@class="vorschlag buergervorschlag"]/h2/text()')
            .extract_first()))[1]

    def suggestion_title(self,response):
        return response.xpath('.//div[@class="col_01"]/h3/text()').extract_first()

    def suggestion_category(self,response):
        return response.xpath(
            './/div[@class="vorschlag buergervorschlag"]/div[@class="image"]/img/@title').extract_first()

    def suggestion_type(self,response):
        return response.xpath('.//div[@class="col_01"]/strong/text()').extract_first()

    def suggestion_content(sef,response):
        return response.xpath('.//div[@class="col_01"]/p/text()').extract_first()

    def suggestion_summary_response(self,response):
        return response.xpath('.//div[@class="col_01"]/table')

    def suggestion_approval(self,response):
         return int(
             self.suggestion_summary_response(response).xpath('.//td[starts-with(@id,"votePro")]/text()')
            .extract_first())

    def suggestion_refusal(self,response):
        return int(
            self.suggestion_summary_response(response).xpath('.//td[starts-with(@id,"voteContra")]/text()')
            .extract_first())

    def suggestion_abstention(self,response):
        return int(
            self.suggestion_summary_response(response).xpath('.//td[starts-with(@id,"voteNeutral")]/text()')
            .extract_first())

    def suggestion_comment_count(self, response):
        return int(
            # float(response.xpath('count(//div[starts-with(@class,"kommentar")])')
            #       .extract_first()))
                self.suggestion_summary_response(response).xpath('.//td[starts-with(.,"Kommentare")]/../td[@class="r"]/text()')
                .extract_first())

    def parse_datetime(self, s):
        """
        Create datetime for given string with given format. Removes spaces.

        :param s: String with date and time.
        :param format: Format for :func:`~datetime.strptime`
        :return: datetime obj
        """
        return datetime.strptime(
            re.sub(r"(\s|[a-z])+", "", s.lower(), flags=re.UNICODE),'%d.%m.%Y-%H:%M')

    # def parse_datetime_sug(self, s):
    #     """ Create datetime obj for given string from a suggestion.
    #     :param s: String with date and time from the suggestion.
    #     :return: datetime obj
    #     """
    #     return self.parse_datetime(s,'%d.%m.%Y-%H:%M',r"(\s|[a-z])+")

    def suggestion_datetime(self,response):
        return self.parse_datetime(
                response.xpath('.//div[@class="details"]/p/text()').extract_first())

    def parse_datetime_commment(self, s):
        """
        Create datetime obj for given string from a comment.

        :param s: String with date and time from the comment.
        :return: datetime obj
        """
        s = s.split("|")
        s = "-".join(s[1:])
        return self.parse_datetime(s)

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
        return self.parse_datetime_commment(response.xpath('.//div[@class="user"]/text()').extract_first())

    def create_comment_item(self, response):
        comment_item = items.CommentItem()
        comment_class = response.xpath('@class').extract_first().replace('kommentar_','').split()

        comment_item['level'] = int(comment_class[0])
        comment_item['comment_id'] = self.comment_id(response)
        comment_item['suggestion_id'] = self.suggestion_id(response.xpath('..'))
        comment_item['content'] = self.comment_content(response)
        comment_item['author'] = self.comment_author(response)
        comment_item['date_time'] = self.comment_datetime(response)
        comment_item['title'] = self.comment_title(response)
        comment_item['children'] = []

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
        stack = []
        for position,item in enumerate(item_list):
            while(len(stack) >= item['level']):
                stack.pop()
            # Check if not first level, i.e. stack not is empty
            if stack:
                # (pos,id)
                parent_tuple = stack[-1]
                # Parent is the last seen item
                item['parent'] = parent_tuple[1]
                # Add current item as child to parent
                item_list[parent_tuple[0]]['children'].append(item['comment_id'])
            else:
                # Top-Level Comments
                item['parent'] = item['suggestion_id']
            stack.append(tuple((position,item['comment_id'])))
        return item_list

    def create_comment_item_list(self, response):
        # Dont change resonse -> work with list to create a tree
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
        pages of bonn-packts-an-2011.

        :param response: scrapy response
        :return: generator
        """
        for thread in response.css('div.vorschlag.buergervorschlag'):
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

        yield self.create_suggestion_item(response)

        # TODO: Parse tree of comments
        yield from self.create_comment_item_list(response)
