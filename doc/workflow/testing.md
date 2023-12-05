# Testing

Testing is automated with jenkins.  
Its configuration is in the `Jenkinsfile`.  

## services

### app

Tests are found by jest in `code/app/__tests__` with extension `.test.js`.  
A test can be executed runnning `npm run coverage:dev` in development phase (or `npm run coverage:prod` for production).  

### api

(to define)  
Use `unittest` for python.  

### async

Test are found by python in `code/async/test/unit`.    
The test can be executed from inside the folder above by 
running `python3.12 -m unittest test_*`.

### django

Test are located at `code/django/backend/test/unit`. 
They can be executed from the folder `code/django` by running 
`python3 manage.py test backend.test`. 

## branches

The following branches are automatically tested:
*	`main`
*	`testing`
*	`dev-*`
