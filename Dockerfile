#FROM vimagick/scrapyd
FROM python:3

RUN echo "Europe/Berlin " > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata
#RUN apt-get update
#RUN apt-get install -y firefox
#RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.16.1/geckodriver-v0.16.1-linux64.tar.gz && \
#    tar -xvzf geckodriver* && \
#    chmod +x geckodriver && \
#    mv geckodriver /usr/local/bin/geckodriver

RUN wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2 && \
    tar -xvjf phantomjs-2.1.1-linux-x86_64.tar.bz2 && \
    mv phantomjs-2.1.1-linux-x86_64 /usr/local/bin/phantomjs-2.1.1-linux-x86_64


WORKDIR /src
ADD . .
RUN pip install -r requirements.txt
RUN pip install -e .
