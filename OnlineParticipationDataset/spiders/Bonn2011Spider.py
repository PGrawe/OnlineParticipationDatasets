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


    def create_comment_items(self, response):
        comment_stack = list()
        comments = response.xpath('//div[starts-with(@class,"kommentar")]').extract()
        #TODO: get ID and push to stack
        return

    def create_suggestion_item(self, response):
        """
        Create a SuggestionItem, see :class:`~OnlineParticipationDataset.items.SuggestionItem`, from given response.

        :param response: scrapy response
        :return: scrapy item
        """
        sug_item = items.SuggestionItem()
        # parse id
        sug_item['id'],sug_item['author'] = self.parse_id_and_author(
            response.xpath('.//div[@class="vorschlag buergervorschlag"]/h2/text()')
            .extract_first())
        sug_item['title'] = response.xpath('.//div[@class="col_01"]/h3/text()').extract_first()
        sug_item['category'] = response.xpath(
            './/div[@class="vorschlag buergervorschlag"]/div[@class="image"]/img/@title').extract_first()
        sug_item['suggestion_type'] = response.xpath('.//div[@class="col_01"]/strong/text()').extract_first()
        sug_item['suggestion'] = response.xpath('.//div[@class="col_01"]/p/text()').extract_first()
        summary = response.xpath('.//div[@class="col_01"]/table')
        sug_item['pro'] = int(
            summary.xpath('.//td[starts-with(@id,"votePro")]/text()')
            .extract_first())
        sug_item['contra'] = int(
            summary.xpath('.//td[starts-with(@id,"voteContra")]/text()')
            .extract_first())
        sug_item['neutral'] = int(
            summary.xpath('.//td[starts-with(@id,"voteNeutral")]/text()')
            .extract_first())
        sug_item['num_comments'] = int(
            # float(response.xpath('count(//div[starts-with(@class,"kommentar")])')
            #       .extract_first()))
                summary.xpath('.//td[starts-with(.,"Kommentare")]/../td[@class="r"]/text()')
                .extract_first())
        sug_item['date_time'] = self.parse_datetime_sug(
            response.xpath('.//div[@class="details"]/p/text()').extract_first())
        return sug_item

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
        #TODO:
        # Parse all comments
        yield self.create_suggestion_item(response)
