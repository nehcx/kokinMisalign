FROM python:3.8-buster as builder

LABEL maintainer="xchen@shs.ens.titech.ac.jp"

WORKDIR /opt/app

# Environment
RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get install --no-install-recommends -yq ssh git curl apt-utils && \
    apt-get install -y python-igraph 

# Code
RUN git clone -b master --depth=1 --recursive https://github.com/nehcx/misalignVis

# Python dependencies
RUN pip install --upgrade pip && \
    pip install -r misalignVis/requirements.txt
