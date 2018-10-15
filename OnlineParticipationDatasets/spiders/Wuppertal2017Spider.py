import locale
from datetime import datetime
from typing import Generator, List, Any, Optional

import scrapy
from scrapy.http import HtmlResponse


class Wuppertal2017Spider(scrapy.Spider):
    name = "wuppertal2017"
    start_urls = ["https://buergerbudget.wuppertal.de/cb/t711bwqTXj3GSGiEVwa3li3YZDqvq4pL?type=phase1&ajax_call=true&sort_order=order_by_multi_vote&search=&topics_to_show=500&filter_phases=197&_=1527933477600",
                  "https://buergerbudget.wuppertal.de/cb/t711bwqTXj3GSGiEVwa3li3YZDqvq4pL?type=phase1&ajax_call=true&sort_order=order_by_multi_vote&search=&topics_to_show=500&filter_phases=198&_=1527933477599"]

    def __init__(self, *args, **kwargs):
        super(Wuppertal2017Spider, self).__init__(*args, **kwargs)
        locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')

    def parse(self, response: HtmlResponse) -> Generator:
        for suggestion_url in response.css(".topic-title > a:last-of-type::attr('href')").extract():
            yield response.follow(suggestion_url, Wuppertal2017Spider.parse_suggestion)

    @staticmethod
    def parse_suggestion(suggestion: HtmlResponse) -> dict:
        suggestion_item = dict()
        suggestion_item['suggestion_id'] = suggestion.url.split("/")[-1].split("?")[0]
        suggestion_item['title'] = suggestion.css("h2::text").extract_first()
        suggestion_item['date_time'] = datetime.strptime(suggestion.css(".fa-calendar")[0].root.tail.strip(), "%Y-%m-%d")
        suggestion_item['tags'] = [element_text.strip() for element_text in suggestion.xpath("//*[@class='fa fa-sticky-note-o']/../..//strong/text()").extract()]
        suggestion_item['author'] = suggestion.css(".fa-user")[0].root.tail.strip()
        suggestion_item['approval_phase_1'] = int(suggestion.css(".fa-thumbs-up")[0].root.tail.strip().split(" ")[0])
        suggestion_item['approval_phase_3'] = int(suggestion.css(".fa-check-square-o")[0].root.tail.strip().split(" ")[0])
        suggestion_item.update(Wuppertal2017Spider.get_status(suggestion.css(".checkpoints-title ~ div::attr('class')").extract()))
        suggestion_item['content'] = "".join([text.strip() for text in suggestion.css(".description *::text").extract()])
        suggestion_item['comment_count'] = int(suggestion.css(".count-comments::text").extract_first().split(" ")[0])
        suggestion_item['costs'] = Wuppertal2017Spider.get_costs(suggestion)
        suggestion_item.update(Wuppertal2017Spider.get_subsections(suggestion.css(".param-text-area-description::text").extract()))
        return suggestion_item

    @staticmethod
    def get_costs(suggestion: HtmlResponse) -> Optional[int]:
        try:
            return int("".join(c for c in suggestion.css(".fa-eur")[0].root.tail.strip() if c.isdigit()))
        except IndexError:
            return None

    @staticmethod
    def get_subsections(texts: [str]) -> dict:
        subsections = [
            "Voraussichtliche Rolle für die Stadt Wuppertal",
            "Geschätzte Umsetzungsdauer und Startschuss",
            "Mehrwert der Idee für Wuppertal",
            "Eigene Rolle bei der Projektidee",
            "Kostenschätzung der Ideeneinreicher/in",
        ]
        return dict(zip(subsections, texts))

    @staticmethod
    def get_status(css_classes: [str]) -> dict:
        status_keys = [
            "Kriteriencheck bestanden",
            "Teil der TOP 100",
            "Gemeinwohl-Check bestanden: Teil der TOP 30",
            "Detailprüfung durch Verwaltung bestanden: Zur finalen Abstimmung freigegeben",
            "Bei der finalen Abstimmung gewonnen",
            "Umsetzung gestartet",
            "Umgesetzt!"
        ]
        status_values = [("not-checked-yet" not in css_classes[i]) and ("did-not-passed" not in css_classes[i])
                         for i in range(len(status_keys))]
        phase = Wuppertal2017Spider.get_last([i for i, passed in enumerate(status_values) if passed], -1) + 1
        status = dict(zip(status_keys, status_values))
        status["status"] = phase
        return status

    @staticmethod
    def get_last(lst: List, default: Any) -> Any:
        try:
            return lst[-1]
        except IndexError:
            return default
