import os

# api domain
class Domain:
	PORT = os.getenv('PORT')
	DOMAIN = os.getenv('DOMAIN')
	SUBPATH_API = os.getenv('SUBPATH_API')
	API_ADDR = f"{DOMAIN}:{PORT}/{SUBPATH_API}"

# api paths
class Api:
	API_ADD_GUEST = f"{Domain.API_ADDR}/add_guest/"
	API_GET_GUEST_NAME = f"{Domain.API_ADDR}/get_guest_name/"