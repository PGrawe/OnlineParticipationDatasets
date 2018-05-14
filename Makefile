name = crawler
home = /home/appuser

build:
	docker build -t $(name) .

stop:
	docker stop $(name) || true
	docker rm -f $(name) || true

shell:
	docker run -it -p 6800:6800 --rm -v $(shell pwd)/downloads:$(home)/downloads \
	--name=$(name) $(name) bash -l

start: stop
	docker run -d --restart=unless-stopped -p 6800:6800 -v $(shell pwd)/downloads:$(home)/downloads:z --name=$(name) $(name)
