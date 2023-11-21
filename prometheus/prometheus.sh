#!/bin/bash

PORT_TO_EXPOSE=9090
PORT_EXPOSED=
LOCAL_DOCKER_GID="$(echo \"$(id $(whoami) )\" | sed -n -e 's/^.*,\(.*\)(docker).*$/\1/p')"
echo $LOCAL_DOCKER_GID

set -a && source ./prometheus.env
if [ -z ${INSTANCE_NAME} ]; then
	INSTANCE_NAME="$(whoami)"
fi
envsubst < prometheus.yaml.template > prometheus.yaml

mkdir ${WAL_DATA_DIR} 2>/dev/null
chmod ug=rwx ${WAL_DATA_DIR}
chown -R :docker ${WAL_DATA_DIR}

if [ "$1" = "-p" ]; then
    echo "Binding to localhost port ${PORT_TO_EXPOSE}"
	PORT_EXPOSED="${PORT_TO_EXPOSE}:"
fi

if [ "$(docker ps -q -f name=${PROMETHEUS_AGENT_CONTAINER_NAME})" ]; then
    echo "Container is running, stopping and removing..."
    docker stop ${PROMETHEUS_AGENT_CONTAINER_NAME} && \
		docker container rm ${PROMETHEUS_AGENT_CONTAINER_NAME}
elif [ "$(docker ps -aq -f name=${PROMETHEUS_AGENT_CONTAINER_NAME})" ]; then
    echo "Container exists but is not running, removing..."
    docker container rm ${PROMETHEUS_AGENT_CONTAINER_NAME}
fi

if docker image inspect ${PROMETHEUS_AGENT_IMAGE_NAME} >/dev/null 2>&1; then
    echo "Image exists, removing..."
    docker image rm ${PROMETHEUS_AGENT_IMAGE_NAME}
fi

docker build -t ${PROMETHEUS_AGENT_IMAGE_NAME} \
	--build-arg LOCAL_DOCKER_GID=${LOCAL_DOCKER_GID} \
	. \
	

docker run -d -t \
	--name ${PROMETHEUS_AGENT_CONTAINER_NAME} \
	-p ${PORT_EXPOSED}9090 \
	-v ${WAL_DATA_DIR}:/prometheus \
	-v ${PWD}/prometheus.yaml:/etc/prometheus/prometheus.yml \
	--restart ${RESTART_POLICY} \
	${PROMETHEUS_AGENT_IMAGE_NAME}
	