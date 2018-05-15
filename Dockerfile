FROM python:3

RUN apt-get clean && apt-get update
# configure use of locales
RUN echo "Europe/Berlin " > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata
RUN apt-get install -y locales locales-all

RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /home/appuser

COPY ./OnlineParticipationDatasets OnlineParticipationDatasets
COPY ./requirements.txt ./scrapy.cfg ./setup.py ./scrapyd.conf ./docker-entrypoint.sh ./
RUN chown -R appuser:appuser ./ && chmod +x docker-entrypoint.sh

USER appuser
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt

ENTRYPOINT [ "./docker-entrypoint.sh" ]
CMD ["run"]

EXPOSE 6800
