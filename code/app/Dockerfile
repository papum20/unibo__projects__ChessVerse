FROM node:20.9.0-bullseye-slim
EXPOSE 3000

USER root

RUN apt-get update && apt-get install -y --no-install-recommends dumb-init
	
# only install production dependencies
ENV VITE_NODE_ENV production
ENV VITE_GAME_HOST https://game.chessverse.cloud
ENV VITE_API_HOST https://api.chessverse.cloud
ENV VITE_APP_HOST https://www.chessverse.cloud
WORKDIR /usr/src/app
# don't run as root #1
COPY --chown=node:node . .
# clean install
RUN npm ci --omit=dev

RUN npm run build

# don't run as root #2
USER node
# node isn't suitable to be run as pid 1, dumb-init is like a wrapper
RUN chmod +x /usr/src/app/entrypoint.sh
CMD ["/usr/src/app/entrypoint.sh"]

# https://snyk.io/blog/10-best-practices-to-containerize-nodejs-web-applications-with-docker/

