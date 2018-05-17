CRAWLER_NAME = crawler
HOME = /home/appuser

build:
	docker build -t $(CRAWLER_NAME) .

stop:
	- docker stop $(CRAWLER_NAME)
	- docker rm -f $(CRAWLER_NAME)

shell:
	docker run -it -p 6800:6800 --rm -v $(shell pwd)/downloads:$(HOME)/downloads \
	--name=$(CRAWLER_NAME) $(CRAWLER_NAME) bash -l

start: stop
	docker run -d --restart=unless-stopped -p 6800:6800 -v $(shell pwd)/downloads:$(HOME)/downloads:z --name=$(CRAWLER_NAME) $(CRAWLER_NAME)

dev: stop
	docker run -d --rm -p 6800:6800 -v $(shell pwd)/downloads:$(HOME)/downloads:z --name=$(CRAWLER_NAME) $(CRAWLER_NAME)
