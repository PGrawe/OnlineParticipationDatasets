import scrapy

class Bonn2011Spider(scrapy.Spider):
    name = "bonn2011"
    start_urls = ['http://bonn-packts-an-2011.de/www.bonn-packts-an.de/dito/forumc0d2.html']
    # TODO: parse the list_pages for next page/last -> maybe in start_requests
    #response.css('div.list_pages a').extract()
    def parse(self, response):
        for thread in response.css('div.vorschlag.buergervorschlag'):
            # TODO: Follow each link
            yield {
                # TODO: Parse id
                'id' : thread.css('h2::text').extract_first(),
                'title' : thread.css('div.col_01 h3 a::text').extract_first(),
                'link' : thread.css('div.col_01 h3 a::attr(href)').extract_first()
            }
