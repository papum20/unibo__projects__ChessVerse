#!/bin/sh
envsubst < ./.env.example > ./.env
exec dumb-init npm run prod