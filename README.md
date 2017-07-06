# OnlineParticipationDatasets
[![license](https://img.shields.io/github/license/mashape/apistatus.svg?maxAge=2592000)](https://github.com/Liebeck/OnlineParticipationDatasets/blob/master/LICENSE)

This projects aims to share text content from online participation processes by sharing crawlers instead of the text contents themselves which might not be possible due to legal reasons. The text contets of the individual online participation plattforms will be downloaded via [Scrapy](https://scrapy.org/) into a JSON file.

## Dependencies
* [docker](https://www.docker.com/)

## How to setup the project:
This will install all required dependencies.
``` bash
make build
```

## How to start the project:
``` bash
make run
scrapy crawl bonn2011
```

## Supported datasets:


| Dataset name | Link                                                                                                                                  | # Suggestions | # Comments | # Total | Crawl time | Command               |
|--------------|---------------------------------------------------------------------------------------------------------------------------------------|---------------|------------|---------|------------|-----------------------|
| Bonn 2011    | [bonn-packts-an-2011.de](http://bonn-packts-an-2011.de/www.bonn-packts-an.de/dito/forumc0d2.html)                                     |    1015       |    8903    |   9918   | 50 seconds | scrapy crawl bonn2011 |
| Braunkohle   | [leitentscheidung-braunkohle.nrw](https://www.leitentscheidung-braunkohle.nrw/perspektiven/de/home/beteiligen/draftbill/47589/chap/5#chapter) |       7       |     1296  |   1296      | 32 minutes | scrapy crawl braunkohle|

###Note:
Braunkohle-spider uses javascript to load content and needs to wait for server responses. This results in long crawltimes.
Braunkohle-site only provides 7 suggestions.