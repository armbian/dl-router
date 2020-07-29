APP_PATH=/home/lane/GIT/apt-router/app
LISTEN_PORT=25090
CONTAINER_NAME=apt-redirect

sudo docker run --rm -d -v ${APP_PATH}:/app -p 127.0.0.1:${LISTEN_PORT}:80 --name ${CONTAINER_NAME} tiangolo/uwsgi-nginx-flask
