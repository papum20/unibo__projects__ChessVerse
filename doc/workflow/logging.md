# LOGGING

Logging is automated thanks to prometheus and grafana.  
However this is only for tracking our work on the project/this repository, which means that it wont track the time we spend doing research on the internet, thinking, planning, designing or working with other apps (especially terminals).  

## vscode

This is the process that allows to collect our work on the project in vscode:
1.	`vscode-exporter` extension tracks our work and collects metrics.
2.	An instance of `prometheus` runs on the device of each of us developers. This is done through the command `prometheus.sh` in the `prometheus` folder, and what it does is executing a docker container running a prometheus instance in agent mode. Such instance collects metrics from `vscode-exporter` and sends to the global instance:
3.	A global instance of `prometheus` runs on the server, and aggregates all data received from the single developers. It can be accessed from `chessverse.mooo.com/prometheus`.
4.	Finally, `grafana` shows these metrics in a nicer way through its dashboard. It can be accessed at `chessverse.mooo.com/grafana`.

## other logging

As said, the method described above can't track all of our work, so here we will report our working time, divided by sprint.

### sprint 0
Daniele 40h  

### sprint 1
Daniele: 80h  

### sprint 2
Daniele: 54h  

### sprint 3
Daniele: 19h

### sprint 4
Daniele: 26h  
