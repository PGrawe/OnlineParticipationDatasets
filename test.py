from datetime import datetime, timedelta
import time
import os
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging


# regex patterns as keys -> factor as value
time_s_to_key = {
    'us': 'microseconds',
    'ms': 'milliseconds',
    's': 'seconds',
    'm': 'minutes',
    'h': 'hours',
    'd': 'days'
}


def call_scrapy(spider, seconds):
    runner = CrawlerRunner(get_project_settings())
    d = runner.crawl(spider)
    d.addCallback(callLater_wrapper, seconds, call_scrapy, spider, seconds)
    # d.addBoth(lambda _: reactor.stop())
    # # print('Run spider {} at {}'.format(spider, datetime.now()))
    # reactor.run(installSignalHandlers=0) # the script will block here until the crawling is finished
    # # print('{} finished at {}'.format(spider, datetime.now()))
    return d

def callLater_wrapper(result, *args, **kwargs):
    # here add returned value to thread-safe obj
    return reactor.callLater(*args,*kwargs)

def parse_timestr(s):
    time_count, time_s = s.split()
    return {time_s_to_key[time_s]: int(time_count)}

def get_envs():
    return_dict = {}
    return_dict['onstartup'] = parse_timestr(os.environ.get('ONSTARTUP'))
    return_dict['spider'] = os.environ.get('SPIDER')
    return return_dict

def main():
    configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})
    # scheduler = BlockingScheduler()
    # scheduler.add_job(call_scrapy, 'interval', kwargs={'spider': 'bonn2017'}, seconds=60, start_date=on_startup(), id='crawler')
    # scheduler.start() # for backgroundscheduler
    print('Press Ctrl+{0} to exit -- {1}'.format('Break' if os.name == 'nt' else 'C', datetime.now()))
    call_scrapy('bonn2017', 120)
    reactor.run()

    # try:
    #     # This is here to simulate application activity (which keeps the main thread alive).
    #     # while True:
    #     #     time.sleep(10)
    #     scheduler.start()
    # except (KeyboardInterrupt, SystemExit):
    #     # Not strictly necessary if daemonic mode is enabled but should be done if possible
    #     scheduler.shutdown()

if __name__ == '__main__':
    main()
    
