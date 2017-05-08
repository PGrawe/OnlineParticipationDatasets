import scrapy

class Bonn2011Spider(scrapy.Spider):
    name = "bonn2011"
    start_urls = ['http://bonn-packts-an-2011.de/www.bonn-packts-an.de/dito/forumc0d2.html']

    def parse(self, response):
       # Parses top level responses (list of suggestions)
       #Follow each link to a suggestion
        for suggestion in response.css('div.vorschlag.buergervorschlag'):
            suggestion_link = response.urljoin(suggestion.css('.col_01>h3>a::attr(href)').extract_first())
            yield scrapy.Request(suggestion_link,callback=self.parse_comments)

        #Go to next top level page (if available)
        next_link=None
        for link in response.css('.list_pages>a'):
            if link.css('::text').extract_first()[0] == 'vor':
                next_link = response.urljoin(link.css('::attr href').extract_first())
        if next_link:
            yield scrapy.Request(next_link, callback=self.parse)


    def parse_comments(self, response):
        # TODO Parses the discussion-feed (extracts information and creates items)
        suggestion = response.css('.col_01>h3::text').extract_first()
        self.log('Suggestion: ' + suggestion)

