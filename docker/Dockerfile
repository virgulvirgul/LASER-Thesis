    FROM continuumio/miniconda3

MAINTAINER Gilles Bodart <gillesbodart@users.noreply.github.com>

RUN conda create -n env python=3.6
RUN echo "source activate env" > ~/.bashrc
ENV PATH /opt/conda/envs/env/bin:$PATH

RUN apt-get -qq -y update --fix-missing
RUN apt-get -qq -y upgrade
RUN apt-get -qq -y install \
        gcc \
        g++ \
        wget \
        curl \
        git \
        make \
        unzip \
        sudo \
        vim \
        libpq-dev \
        python3-tk

# Use C.UTF-8 locale to avoid issues with ASCII encoding
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Set the working directory to /app
WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org Cython
RUN pip install --trusted-host pypi.python.org -r requirements.txt --verbose

ARG CACHEBUST=1

# Download LASER from FB
RUN git clone https://github.com/jrfilocao/LASER-Thesis.git

ENV LASER /app/LASER-Thesis
ENV NEWS_TASK /app/LASER-Thesis/tasks/news_uni_leipzig
WORKDIR $LASER

RUN bash ./install_models.sh


# Installing FAISS

RUN conda install --name env -c pytorch faiss-cpu -y

# Spacy
RUN python3 -m spacy download de_core_news_sm
RUN python3 -m spacy download pt_core_news_sm
RUN python3 -m spacy download en_core_web_sm

RUN bash ./install_external_tools.sh

COPY ./decode.py $LASER/tasks/embed/decode.py

RUN alias ll="ls -la"

# Make port 80 available to the world outside this container
WORKDIR /app

RUN echo "Hello World" > test.txt

RUN $LASER/tasks/embed/embed.sh test.txt en test_embed.raw
RUN python3 $LASER/tasks/embed/decode.py test_embed.raw

#Open the port 80
EXPOSE 80

COPY ./app.py /app/app.py

CMD ["/bin/bash"]
