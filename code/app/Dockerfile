
FROM node:20.9.0-bullseye-slim

RUN apt-get update && apt-get install -y --no-install-recommends dumb-init \
	# envsubst
	gettext-base
# only install production dependencies
ENV NODE_ENV production
WORKDIR /usr/src/app
# don't run as root #1
COPY --chown=node:node . .
# clean install
RUN npm ci --mit=dev

RUN npm run build

# don't run as root #2
USER node
# node isn't suitable to be run as pid 1, dumb-init is like a wrapper
RUN chmod +x /usr/src/app/entrypoint.sh
CMD ["/usr/src/app/entrypoint.sh"]

# https://snyk.io/blog/10-best-practices-to-containerize-nodejs-web-applications-with-docker/
