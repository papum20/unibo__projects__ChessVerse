# FROM prom/prometheus
FROM prom/prometheus:v2.48.0-rc.2

ARG LOCAL_DOCKER_GID

USER root
# groupadd and usermod: commands not found
RUN addgroup -g ${LOCAL_DOCKER_GID} docker
RUN addgroup nobody docker

USER nobody
ENTRYPOINT [ "/bin/prometheus" ]

CMD [ "--config.file=/etc/prometheus/prometheus.yml", \
 	"--storage.tsdb.path=/prometheus", \
	"--web.console.libraries=/usr/share/prometheus/console_libraries", \
	"--web.console.templates=/usr/share/prometheus/consoles", \
	"--log.level=info" ]