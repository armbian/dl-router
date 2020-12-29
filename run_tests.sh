#!/bin/bash

APP_PATH=$(pwd)/app
USERDATA_PATH=$(pwd)/examples/userdata.csv
MIRRORS_CONF_PATH=$(pwd)/examples/mirrors-apt.yaml
LISTEN_PORT=5000
CONTAINER_NAME=redirect_test
DETACH=false

##FIXME CHANGE CONFIG MAP TO YAML WHEN DONE

if [ ! -d "${APP_PATH}" ]; then
    echo "Unable to find App path: ${APP_PATH}"
    exit 1
fi

if [ ! -f "${USERDATA_PATH}" ]; then
    echo "Unable to find userdata.csv at ${USERDATA_PATH}"
    exit 1
fi

if [ ! -f "${MIRRORS_CONF_PATH}" ]; then
    echo "Unable to find mirrors.yaml at ${MIRRORS_CONF_PATH}"
    exit 1
fi

sudo docker run --rm $([[ ${DETACH} == "true" ]] && echo "-d") \
    -v ${APP_PATH}:/app \
    -v ${USERDATA_PATH}:/app/userdata.csv \
    -v ${MIRRORS_CONF_PATH}:/app/mirrors.yaml \
    -p ${LISTEN_PORT}:80 \
    --name ${CONTAINER_NAME} \
    quay.io/lanefu/nginx-uwsgi-flask:arm64 bash -c "pip install --upgrade pip && pip install -r requirements.txt && pip install pytest && pytest -s "

