name = onlineparticipationdatasets
registry = hub.docker.com
bonn2011 = http://bonn-packts-an-2011.de/www.bonn-packts-an.de/dito/forumc0d2.html

build:
	docker build -t $(registry)/$(name) $(BUILD_OPTS) .

stop:
	docker rm -f $(name) || true

run: stop
	docker run -it --rm=true -v $(shell pwd):/src \
	--name=$(name) $(registry)/$(name) bash -l

start: stop
	docker run -d -v $(shell pwd):/src --name=$(name) $(registry)/$(name)

shell-bonn2011: stop
	docker run -it --rm=true -v $(shell pwd):/src \
	--name=$(name) $(registry)/$(name) scrapy shell $(bonn)
