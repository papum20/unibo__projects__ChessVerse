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

Test are found by python in `code/async/tests/unit`.    
The test can be executed running `python3.12 -m unittest unit.TestChessSocketIO`.  

## branches

The following branches are automatically tested:
*	`main`
*	`testing`
*	`dev-*`


