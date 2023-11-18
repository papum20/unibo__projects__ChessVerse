# Repository structure
...and where to find the right files.  

**Notes**:
1.	We try to keep the project as generical as possible; consider that most referred values and variables (e.g. websites, subpaths) are only the defaults and can be edited.  
2.	for each service you will (could) see specified some details
	*	service name
	*	workdir: the working directory inside the container (ttypically where it's launched, and where the main code is stored)
	*	volumes: both local and container's path, and content
3.	files:
	*	`.template` : are to be replaced with environment variables, using `envsubst` (removing the `.template` extension)
	*	`.example` : environment/configuration files, to use as templates to create the actual file (without `.example`)

## /
`.env` : environemnt used to build the `docker-compose`

###
scripts

## /code
Source code.  
Each `/code/SUBDIR` represents a (docker) service or a (web) app.  

### app

Frontend.  

`app/__tests__/` : tests for jest, with `.test.js` extension  

### app-ia
This is a simple web-app to play chess, made by copilot.  
It's accessed at `DOMAIN/webapp`.  

### api
The backend providing chessverse api.  

### async
Another backend, used for real-time necessities (e.g. games): async is more efficient for such purpose and avoids polling from client-side.  
It works by establishing a websockets connection with each client requiring it.  

### website
Everything you see at `DOMAIN`.  
Features:
*	download the app, choose your version and os
*	access to copilot's wonderful webapp

The folder contains both frontend and backend.  
It is thus a single service:
*	service name: `chessverse-website`
*	workdir: `/usr/src/app`
*	volumes: `./database/dist:/usr/src/dist` (bind mount)

#### frontend
Path: `website/public`.  
It's included in the same folder, being a very simple js+html app.  

### database
Code to start the database.  
It's a mysql database run with the standard docker image.  
Service:
*	volumes: `${VOLUME_MYSQL_DATA}:/var/lib/mysql`


## /database
Contains app data, tipically bind mounts.  

### dist
App distributions, downloadable from the `website` (it's a bind mount).  

### releases
Official releases.  
Their names must follow the structure `chessverse{MAJOR}_{MINOR}_{FIX}{SYSTEM}{EXTENSION}`, where `SYSTEM` is one of 
*	`macos`
*	`windows11`
*	`debian`

## /doc
All documentation, both for project and for university teachers requests.  

*	`infrastructure.drawio`: an infrastructure schema
*	`code/`: project-related documentation  
*	other: was reqested by teachers

## /env
Environment files used by docker-compose for each service.  

## /server-nginx
Suggested files to configure your proxy with nginx.  
*	`chessverse_params` : params for the `.conf` (to put in `/etc/nginx/`)
*	`chessverse.conf.template` : conf file (to put in `/etc/nginx/conf.d/`)
*	`chessverse.env.example` : env used for the replacement of the template conf (different from the env for docker compose)

## /test
Test files
