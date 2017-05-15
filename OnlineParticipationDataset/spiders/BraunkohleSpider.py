import scrapy
from selenium import webdriver
from OnlineParticipationDataset import items

class BraunkohleSpider(scrapy.Spider):
    name = "braunkohle"
    start_urls = ['https://www.leitentscheidung-braunkohle.nrw/perspektiven/de/home/beteiligen/draftbill/47589/para/9',
                  'https://www.leitentscheidung-braunkohle.nrw/perspektiven/de/home/beteiligen/draftbill/47589/para/11',
                  'https://www.leitentscheidung-braunkohle.nrw/perspektiven/de/home/beteiligen/draftbill/47589/para/12',
                  'https://www.leitentscheidung-braunkohle.nrw/perspektiven/de/home/beteiligen/draftbill/47589/para/13',
                  'https://www.leitentscheidung-braunkohle.nrw/perspektiven/de/home/beteiligen/draftbill/47589/para/14',
                  'https://www.leitentscheidung-braunkohle.nrw/perspektiven/de/home/beteiligen/draftbill/47589/para/17',
                  'https://www.leitentscheidung-braunkohle.nrw/perspektiven/de/home/beteiligen/draftbill/47589/para/16']

    def __init__(self, **kwargs):
        super(BraunkohleSpider, self).__init__(**kwargs)
        self.driver = webdriver.Firefox()

    def parse(self, response):
        sug_item = items.SuggestionItem
        title = response.css('.ecm_draftBillParagraphContent.push-top>h1::text').extract()
        proposal = response.css('.ecm_draftBillParagraphContent.push-top>div>h3::text').extract()
        suggestion=''
        for paragraph in response.css('.ecm_draftBillParagraphContent.push-top>div>p'):
            suggestion+=paragraph.css('::text').extract()
        #TODO Generate suggestion item. Give category based on start_urls







