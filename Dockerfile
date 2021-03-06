FROM python:3.6

RUN apt-get clean && apt-get update
# configure use of locales
RUN echo "Europe/Berlin " > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata
RUN apt-get install -y locales locales-all netcat

RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /home/appuser

COPY ./OnlineParticipationDatasets OnlineParticipationDatasets
COPY ./requirements.txt ./scrapy.cfg ./setup.py ./scrapyd.conf \
    ./docker-entrypoint.sh crawl_scheduler.py ./
RUN mkdir logs
RUN chown -R appuser:appuser ./ && \
    chmod +x docker-entrypoint.sh

USER appuser
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt

ENTRYPOINT [ "./docker-entrypoint.sh" ]
CMD ["run"]

EXPOSE 6800
