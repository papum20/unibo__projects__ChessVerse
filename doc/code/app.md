# APP

The frontend of our website.  

## env

We serve the built version.  
This uses environment variables, which, since we use react, need to be declared as `REACT_APP_<VARNAME>` and used as `proces.env.REACT_APP_<VARNAME`.  
They could be either defined in the environment or in the `.env`. We use the `.env`.
Since `.env` files are ignored in this repository, as always we use `.env.example` templates for convenience and automation.  
So the `.env` is automatically created in the building process with the `up.sh` command (which calls `envsubst` on the `.env.example` before using `docker compose`).  
