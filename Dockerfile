#FROM vimagick/scrapyd
FROM python:3

RUN echo "Europe/Berlin " > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata

WORKDIR /src
ADD . .
RUN pip install -r requirements.txt
RUN pip install -e .
