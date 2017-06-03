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



WORKDIR /src
ADD . .
RUN pip install -r requirements.txt
RUN pip install -e .
