import scrapy
from OnlineParticipationDataset import items
from datetime import datetime
import re


class Bonn2011Spider(scrapy.Spider):
    name = "bonn2011"
    js = False
    start_urls = ['http://bonn-packts-an-2011.de/www.bonn-packts-an.de/dito/forumc0d2.html']

    def parse_id_and_author(self, s):
        r"""
        Extract suggestion id and author from given String.

        :param s: string with possible ID like [A_Z]\d+ and author after 'von '
        :return: tuple of strings
        """
        return (re.search('([B,V]\d+)',s)[0],re.search('(?:von\s)(\w+)',s)[1])

    def parse_datetime(self, s, format):
        """
        Create datetime for given string with given format. Removes spaces.

        :param s: String with date and time.
        :param format: Format for :func:`~datetime.strptime`
        :return: datetime obj
        """
        return datetime.strptime(
            re.sub(r"(\s|[a-z])+", "", s.lower(), flags=re.UNICODE),format)

    def parse_datetime_sug(self, s):
        """ Create datetime obj for given string from a suggestion.
        :param s: String with date and time from the suggestion.
        :return: datetime obj
        """
        return self.parse_datetime(s,'%d.%m.%Y-%H:%M')

    def parse_datetime_com(self, s):
        """
        Create datetime obj for given string from a comment.

        :param s: String with date and time from the comment.
        :return: datetime obj
        """
        return self.parse_datetime(s,'|%d.%m.%Y|%H:%M')

    def parse_comment_id(self, s):
        if s is not None:
            return int(re.search(r"ID\:\D*(\d+)",s)[1])

    def parse_comment_id_official(self,s):

        return

    def create_comment_item(self, response):
        comment_item = items.CommentItem()
        comment_class = response.xpath('@class').extract_first().replace('kommentar_','').split()

        comment_item['level'] = int(comment_class[0])
        comment_item['id'] = self.parse_comment_id(response.xpath('.//div[@class="col_01"]/comment()').extract_first())

        # XXX
        if(len(comment_class) == 2):
            if "ablehnung" == comment_class[1]:
                comment_item['vote'] = "refusal"
            elif "zustimmung" == comment_class[1]:
                comment_item['vote'] = "approval"
            elif "neutral" == comment_class[1]:
                comment_item['vote'] = "neutral"
            else:
                # If official the id is located elsewhere
                # comment_item['id'] =
                comment_item['vote'] = "official"
        else:
            comment_item['vote'] = "answer"


        return comment_item

    def parse_comment_tree(self, item_list, suggestion_id):
        pos_stack = []

        return item_list

    def create_comment_item_list(self, response):
        # Dont change resonse -> work with list to create a tree
        comment_items = []
        for comment in response.xpath('//div[starts-with(@class,"kommentar")]'):
            comment_items.append(self.create_comment_item(comment))
        suggestion_id,_=self.parse_id_and_author(
            response.xpath('.//div[@class="vorschlag buergervorschlag"]/h2/text()')
            .extract_first())
        return self.parse_comment_tree(comment_items,suggestion_id)

    def create_suggestion_item(self, response):
        """
        Create a SuggestionItem, see :class:`~OnlineParticipationDataset.items.SuggestionItem`, from given response.

        :param response: scrapy response
        :return: scrapy item
        """
        suggestion_item = items.SuggestionItem()
        # parse id
        suggestion_item['id'],suggestion_item['author'] = self.parse_id_and_author(
            response.xpath('.//div[@class="vorschlag buergervorschlag"]/h2/text()')
            .extract_first())
        suggestion_item['title'] = response.xpath('.//div[@class="col_01"]/h3/text()').extract_first()
        suggestion_item['category'] = response.xpath(
            './/div[@class="vorschlag buergervorschlag"]/div[@class="image"]/img/@title').extract_first()
        suggestion_item['suggestion_type'] = response.xpath('.//div[@class="col_01"]/strong/text()').extract_first()
        suggestion_item['suggestion'] = response.xpath('.//div[@class="col_01"]/p/text()').extract_first()
        summary = response.xpath('.//div[@class="col_01"]/table')
        suggestion_item['pro'] = int(
            summary.xpath('.//td[starts-with(@id,"votePro")]/text()')
            .extract_first())
        suggestion_item['contra'] = int(
            summary.xpath('.//td[starts-with(@id,"voteContra")]/text()')
            .extract_first())
        suggestion_item['neutral'] = int(
            summary.xpath('.//td[starts-with(@id,"voteNeutral")]/text()')
            .extract_first())
        suggestion_item['num_comments'] = int(
            # float(response.xpath('count(//div[starts-with(@class,"kommentar")])')
            #       .extract_first()))
                summary.xpath('.//td[starts-with(.,"Kommentare")]/../td[@class="r"]/text()')
                .extract_first())
        suggestion_item['date_time'] = self.parse_datetime_sug(
            response.xpath('.//div[@class="details"]/p/text()').extract_first())
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
        # next_page = response.xpath('.//div[@class="list_pages"]/a[.="vor"]/@href').extract_first()
        # if next_page:
        #     yield response.follow(next_page,self.parse)

    def parse_thread(self, response):
        """
        Parse thread and yield a SuggestionItem, see :class:`~OnlineParticipationDataset.items.SuggestionItem`.

        :param response: scrapy response
        :return: generator
        """

        yield self.create_suggestion_item(response)

        # TODO: Parse tree of comments
        yield from self.create_comment_item_list(response)
