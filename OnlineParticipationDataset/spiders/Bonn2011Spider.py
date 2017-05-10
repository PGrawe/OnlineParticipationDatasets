import scrapy

class Bonn2011Spider(scrapy.Spider):
    name = "bonn2011"
    start_urls = ['http://bonn-packts-an-2011.de/www.bonn-packts-an.de/dito/forumc0d2.html']

    def parse(self, response):
        for thread in response.css('div.vorschlag.buergervorschlag'):
            yield scrapy.Request(thread,callback=self.parse_thread)

        # Here: Parse next Site
        next_page = response.xpath('//div[@class="list_pages"]/a[.,"vor"]/@href').extract_first()
        if next_page:
            yield scrapy.Request(
                response.urljoin(next_page),
                callback=self.parse
            )

    def parse_thread(self, response):
        # TODO: create Item, maybe with ItemLoader
        yield {
            'id' : response.xpath('//h2/text()').extract_first(),
            'title' : response.xpath('//div[@class="col_01"]/h3/text()').extract_first(),
            }
