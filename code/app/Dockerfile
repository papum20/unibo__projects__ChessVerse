FROM node:20.9.0-bullseye-slim

EXPOSE 3000

USER root

RUN apt-get update && apt-get install -y --no-install-recommends dumb-init

# Directory per i node_modules
WORKDIR /usr/src/deps

# Installa le dipendenze Node.js
COPY package*.json ./
RUN npm install

# Directory per il codice dell'applicazione
WORKDIR /usr/src/app

# Copia il codice dell'applicazione
COPY . .

# Configurazione ambiente
ENV VITE_NODE_ENV production
ENV VITE_GAME_HOST https://game.chessverse.cloud
ENV VITE_API_HOST https://api.chessverse.cloud
ENV VITE_APP_HOST https://www.chessverse.cloud

# Costruisci l'applicazione
RUN npm run build

# Cambia utente
USER node

# Imposta script di avvio
RUN chmod +x /usr/src/app/entrypoint.sh
CMD ["/usr/src/app/entrypoint.sh"]
