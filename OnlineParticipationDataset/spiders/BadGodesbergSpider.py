from datetime import datetime

from OnlineParticipationDataset.spiders.RaddialogBonnSpider import RaddialogBonnSpider


class BadGodesbergSpider(RaddialogBonnSpider):
    name = "badgodesberg"
    start_urls = ['https://www.bonn-macht-mit.de/node/2399']

    def __init__(self, *args, **kwargs):
        super(BadGodesbergSpider, self).__init__(*args, **kwargs)

    def parse_datetime_comment(self, l):
        s = ' '.join([s.strip() for s in l])
        s = s.replace('von','').strip()
        return datetime.strptime(s, 'am %d. %b. %Y at %H:%MUhr')
