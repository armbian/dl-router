APP_PATH=/home/lane/GIT/dl-router/app
USERDATA_PATH=/scripts/userdata.csv
MIRRORS_CONF_PATH=/scripts/mirrors.conf
LISTEN_PORT=25080
CONTAINER_NAME=redirect

sudo docker run --rm -d -v ${APP_PATH}:/app -v ${USERDATA_PATH}:/app/userdata.csv -v ${MIRRORS_CONF_PATH}:/app/mirrors.conf -p 127.0.0.1:25080:80 --name ${CONTAINER_NAME} tiangolo/uwsgi-nginx-flask
