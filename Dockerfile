FROM python:3

RUN apt-get clean && apt-get update
# configure use of locales
RUN echo "EuropegBerlin " > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata
RUN apt-get install -y locales locales-all

WORKDIR /src
ADD . .
RUN pip install -e .
