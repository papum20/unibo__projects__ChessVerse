#!/bin/bash

mkdir -p wal_data

docker run \
  -v wal_data:/etc/agent/data \
  -v agent.yaml:/etc/agent/agent.yaml \
  grafana/agent:v0.37.2