import scrapy

class Bonn2011Spider(scrapy.Spider):
    name = "bonn2011"
    start_urls = ['http://bonn-packts-an-2011.de/www.bonn-packts-an.de/dito/forumc0d2.html']

    def parse(self, response):
        for thread in response.css('div.vorschlag.buergervorschlag'):
            yield {
                # TODO: Parse id
                'id' : thread.css('h2::text').extract_first(),
                'title' : thread.css('div.col_01 h3 a::text').extract_first(),
                'link' : thread.css('div.col_01 h3 a::attr(href)').extract_first()
                # yield request?
            }

        # Here: Parse next Site
        next_page = response.xpath('//div[@class="list_pages"]/a[.,"vor"]/@href').extract_first()
        if next_page:
            yield scrapy.Request(
                response.urljoin(next_page),
                callback=self.parse
            )
        #Here: Parse threads with parse2?
