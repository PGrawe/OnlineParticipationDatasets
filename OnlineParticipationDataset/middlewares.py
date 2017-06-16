# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import logging
import time

class JSMiddleware(object):
    '''
    Middleware that deals with javascript loading on braunkohle-sites
    '''
    def click_button_repeat(self, driver, button_css, delay):
        '''
        Clicks a button as long as it can be found on the site. Results can be found in driver.
        :param driver: Webdriver
        :param button_css: CSS-selector of the button
        :param delay: Delay between each click
        :return: None
        '''
        while True:
            try:
                logging.info("Has tried to find button")
                next = driver.find_element_by_css_selector(button_css)
                logging.info("Has found button")
                next.click()
                logging.info("Has clicked")
                time.sleep(delay)
                logging.info("Has slept")

            except:
                break

    def process_request(self, request, spider):
        logging.info('JS Middleware started!')
        #Create webdriver
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
            "(KHTML, like Gecko) Chrome/15.0.87")
        driver = webdriver.PhantomJS(executable_path='/usr/local/bin/phantomjs-2.1.1-linux-x86_64/bin/phantomjs',desired_capabilities=dcap)
        driver.get(request.url)
        #Click button to show more comments
        self.click_button_repeat(driver, '.ecm_showMoreLink', 7)
        #Click button to expand comments
        self.click_button_repeat(driver,'.ecm_commentShowMore',7)
        body = driver.page_source
        current_url = driver.current_url
        driver.close()
        return HtmlResponse(current_url, body=body, encoding='utf-8', request=request)

class OnlineparticipationdatasetSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
