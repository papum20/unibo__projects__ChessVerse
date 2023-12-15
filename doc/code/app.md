# APP

The frontend of our website.  

## env

This uses environment variables, which, since we use vite, need to be declared as `VITE_<VARNAME>` and used as `proces.env.VITE_APP_<VARNAME>`.  
Since `.env` files are ignored in this repository, as always we use `.env.example` templates for convenience and automation.  
The `.env.example` can be easily converted using `envsubst`.  

Also, you could have to set something in the `index.html`.  

## run

*	`npm run dev` : dev??  
*	`npm run dev-local` : dev in local (enables local https)
	*	note that for local https you need your own files (`cert.pem`, `key.pem`), stored in the  `code/app/cert` folder (as set in the vite config).

## structure

`/code/app/` :
*	`src/` : source code
	*	`assets/` : assets, e.g. images
	*	`components/` : react components
	*	`const/` : files of configs and consts
	*	`errors/` : own defined error classes
	*	`models/` : models and utilities for objects formats
	*	`network/` : network/api/server call functions
	*	`styles/` : `.css` files
	*	`utils/` : utility functions and other useful and generical stuff

## constants

### api

These files reflect tha api requests formats:
*	`models/credentials`
*	`models/api_responses`
*	`models/const_api`

Thus should be updated in case of changes in the api.  

## features and libraries

### auth

#### facebook

`index.html` includes the fb jdk, as suggested by `https://developers.facebook.com/quickstarts` guide - it just gets the sdk and initializes params. The sdk is downloaded locally.  
Also, you should set appropriately the `appId` to your facebook app id from the `index.html` (you can get it from facebook developers).  