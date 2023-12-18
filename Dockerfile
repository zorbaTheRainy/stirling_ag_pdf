# syntax=docker/dockerfile:1

ARG IMAGE_TAG=zzzz
FROM frooodle/s-pdf:${IMAGE_TAG}

# ---------------------------------
# ENVs supported by this Image
# ---------------------------------
# ENV CHECK_EVERY_X_MINUTES=
ENV AM_I_IN_A_DOCKER_CONTAINER=1
ENV API_SERVER_URL="http://localhost:8080"

# ---------------------------------
# COPY needed files
# ---------------------------------
WORKDIR /app
COPY requirements.txt requirements.txt
COPY keep_alive.py keep_alive.py
COPY monitorfolder.py monitorfolder.py
COPY start.sh start.sh

# ---------------------------------
# What RUN does
# ---------------------------------
# 1. make the needed directories 
# 2. install requirements.txt

RUN mkdir /inputDir /outputDir /logDir  && \
    pip install -r requirements.txt


# ENTRYPOINT ["/scripts/init.sh"]
ENTRYPOINT ["/app/start.sh"]
