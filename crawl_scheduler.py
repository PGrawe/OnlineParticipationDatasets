from datetime import datetime
import os
import re
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging

SECS_PER_MINUTE = 60
SECS_PER_HOUR = SECS_PER_MINUTE * 60
SECS_PER_DAY = SECS_PER_HOUR * 24


MULTIPLIERS = {
    'days': SECS_PER_DAY,
    'day': SECS_PER_DAY,
    'd': SECS_PER_DAY,
    'hours': SECS_PER_HOUR,
    'hour': SECS_PER_HOUR,
    'hr': SECS_PER_HOUR,
    'h': SECS_PER_HOUR,
    'minutes': SECS_PER_MINUTE,
    'minute': SECS_PER_MINUTE,
    'min': SECS_PER_MINUTE,
    'm': SECS_PER_MINUTE,
    'seconds': 1,
    'second': 1,
    'sec': 1,
    's': 1
    }


def call_scrapy(spider, seconds):
    settings = get_settings_with_logfile()
    runner = CrawlerRunner(settings)
    deferred = runner.crawl(spider)
    if seconds:
        deferred.addCallback(scrapy_callback, seconds, call_scrapy, spider)
    else:
        deferred.addBoth(lambda _: reactor.stop())
    return deferred


def scrapy_callback(result, seconds, func, spider):
    return reactor.callLater(seconds, func, spider, seconds)


def callLater_wrapper(result, *args, **kwargs):
    # here add returned value to thread-safe obj
    return reactor.callLater(*args, **kwargs)


def extract_multiplier(s):

    global MULTIPLIERS

    for suffix, multiplier in MULTIPLIERS.items():
        if s == suffix:
            return multiplier
    raise NotImplementedError('Only days, hours, minutes and seconds are supported')


def parse_timestr(s=None):
    # strings are immutable
    if not s:
        return None
    pattern = r'[a-z]+|[^a-z\s]+'
    groups = re.findall(pattern, s)
    seconds = 0
    for i in range(0, len(groups), 2):
        seconds += float(groups[i]) * extract_multiplier(groups[i+1])
    return seconds


def get_settings_with_logfile():
    settings = get_project_settings()
    log_path = os.environ.get('LOG_ROOT', './log')
    current_day = datetime.date(datetime.now())
    settings.set('LOG_FILE', get_logfile_name(log_path, current_day))
    configure_logging({'LOG_ENABLED': False})
    return settings


def get_logfile_name(log_path, current_day):
    return os.path.abspath(
            os.path.normpath(
                log_path + '/crawler_log-{}.log'.format(str(current_day))))


def main():
    call_scrapy(os.environ['SPIDER'], parse_timestr(os.environ.get('RUNEVERY', None))
    reactor.run()


if __name__ == '__main__':
    main()
