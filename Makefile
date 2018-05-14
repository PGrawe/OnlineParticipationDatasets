name = crawler

build:
	docker build -t $(name) .

stop:
	docker rm -f $(name) || true

shell:
	docker run -it --rm=true -v $(shell pwd):/src \
	--name=$(name) $(name) bash -l

start: stop
	docker run -d -v $(shell pwd):/src --name=$(name) $(name)
