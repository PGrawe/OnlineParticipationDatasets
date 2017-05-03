import scrapy

class Bonn2011Spider(scrapy.Spider):
    name = "bonn2011"
    start_urls = ['http://bonn-packts-an-2011.de/www.bonn-packts-an.de/dito/forumc0d2.html']
    # TODO: parse the list_pages for next page/last -> maybe in start_requests
    #response.css('div.list_pages a').extract()
    def parse(self, response):
        # div.vorschlag buergervorschlag doesn't work -> XPath
        for thread in response.css('div.vorschlaege'):
            # TODO: Follow each link
            yield {
                # TODO: Parse id
                'id' : thread.css('h2::text').extract_first()
                #'title' :
            }
