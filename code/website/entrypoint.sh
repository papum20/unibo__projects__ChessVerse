#!/bin/sh
envsubst < public/index.html.template > public/index.html
exec dumb-init npm start