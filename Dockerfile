FROM liebeck/miniconder3

RUN apt-get update && \
	apt-get install -y build-essential libxml2-dev libxslt-dev python-matplotlib libsm6 libxrender1 libfontconfig1 libicu-dev python-dev python-qt4 && \
	apt-get clean

# install packages with conda
RUN conda install -y \
  pip

RUN sudo echo "Europe/Berlin " > /etc/timezone
RUN sudo dpkg-reconfigure -f noninteractive tzdata


WORKDIR /var/www
ADD . .
RUN pip install -r requirements.txt
RUN pip install -e .