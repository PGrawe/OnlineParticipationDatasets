import scrapy
from OnlineParticipationDataset import items
from datetime import datetime
import re


class Bonn2011Spider(scrapy.Spider):
    name = "bonn2011"
    start_urls = ['http://bonn-packts-an-2011.de/www.bonn-packts-an.de/dito/forumc0d2.html']

    # def parse_id(self, str):
    #
    #     return

    def parse_datetime(self, str, format):
        return datetime.strptime(re.sub(r"(\s|[a-z])+", "", str.lower(), flags=re.UNICODE),format)

    def parse_datetime_sug(self,str):
        return self.parse_datetime(str,'%d.%m.%Y-%H:%M')

    def parse_datetime_com(self,str):
        return self.parse_datetime(str,'|%d.%m.%Y|%H:%M')


    def create_suggestion_item(self, response):
        sug_item = items.SuggestionItem()
        # parse id
        sug_item['id'] = response.xpath('.//div[@class="vorschlag buergervorschlag"]/h2/text()').extract_first()
        sug_item['title'] = response.xpath('.//div[@class="col_01"]/h3/text()').extract_first()
        sug_item['category'] = response.xpath('.//div[@class="vorschlag buergervorschlag"]/div[@class="image"]/img/@title').extract_first()
        sug_item['suggestion_type'] = response.xpath('.//div[@class="col_01"]/strong/text()').extract_first()
        sug_item['suggestion'] = response.xpath('.//div[@class="col_01"]/p/text()').extract_first()
        summary = response.xpath('.//div[@class="col_01"]/table')
        sug_item['pro'] = int(summary.xpath('.//td[starts-with(@id,"votePro")]/text()').extract_first())
        sug_item['contra'] = int(summary.xpath('.//td[starts-with(@id,"voteContra")]/text()').extract_first())
        sug_item['neutral'] = int(summary.xpath('.//td[starts-with(@id,"voteNeutral")]/text()').extract_first())
        sug_item['num_comments'] = int(float(response.xpath('count(//div[starts-with(@class,"kommentar")])').extract_first()))
        sug_item['date_time'] = self.parse_datetime_sug(response.xpath('.//div[@class="details"]/p/text()').extract_first())

    def parse(self, response):
        for thread in response.css('div.vorschlag.buergervorschlag'):
            thread_url = thread.xpath('.//div[@class="col_01"]/h3/a/@href').extract_first()
            yield response.follow(thread_url,self.parse_thread)


        # Here: Parse next Site
        # next_page = response.xpath('.//div[@class="list_pages"]/a[.="vor"]/@href').extract_first()
        # if next_page:
        #     yield response.follow(next_page,self.parse)

    def parse_thread(self, response):
        # TODO: create Item, maybe with ItemLoader
        # SuggestionItem
        # Parse all comments
        suggestion = self.create_suggestion_item(response)
        yield suggestion
