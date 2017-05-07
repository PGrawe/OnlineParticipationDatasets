# OnlineParticipationDatasets
[![license](https://img.shields.io/github/license/mashape/apistatus.svg?maxAge=2592000)](https://github.com/Liebeck/OnlineParticipationDatasets/blob/master/LICENSE)

This projects aims to share text content from online participation processes by sharing crawlers instead of the text contents themselves which might not be possible due to legal reasons.

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
scrapy runspider onlineparticipation/crawlers/bonn2011.py -o downloads/bonn2011.json
```
