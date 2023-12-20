# Testing

Testing is automated with jenkins.  
Its configuration is in the `Jenkinsfile`, and that's all which manages the testing flow.  

## notes on Jenkins

Jenkins is a tool which automates testing and in general execution of scripts on specified triggers.  
The current configuration executes a diffent set of commands depending on the branch: when one of the specified branches is pushed, the relative congiguration is executed.  
Such configurations are called `pipeline`s: in fact, a pipeline is a sequence of `stage`s (as they are called), and a step isn't executed until the previous one has exited successfully (i.e. an error in one stage will block the **whole** pipeline, and no further stage will be executed).  
These stages and commands are executed in a specific environment on the server running Jenkins.  

### syntax

```config
// comment
pipeline{ // the main block for a pipeline  
	stages{ // main block containing stages  
		stage("NAME") { // a the stage mentioned above, contained in a `stages` block; NAME identifies it  
			when {	// inside a `stage`, tells when such stage is executed
				CONDITION
			}
			steps { // commands to exec
				dir("PATH") {	// execute commands in dir
					sh COMMAND	// shell command
				}
			}
		}
	}
}
```

`CONDITION` : 
*	`anyOf{CONDITION...}` : true if any of is 
*	`branch BRANCH` : true if we are on the git branch `BRANCH`  

## services

### app

Tests are found by jest in `code/app/__tests__` with extension `.test.js`.  
A test can be executed runnning `npm run coverage:dev` in development phase (or `npm run coverage:prod` for production).  

### api

(to define)  
Use `unittest` for python.  

### game 

Test are found by python in `code/game/test/unit`.    
The test can be executed from inside the folder above by 
running `python3.12 -m unittest test_*`.

### api

Test are located at `code/api/backend/test/unit`. 
They can be executed from the folder `code/api` by running 
`python3 manage.py test backend.test`. 


### end-to-end tests
Contenuti nel file e2etests.py in 'code/'.
Possono essere eseguiti da code/ lanciando 'python e2etests.py'.
Importante: i test ora usano Chrome e CromeDriver. Per eseguirli è necesssario scaricare chromedriver, se si vuole utilizzare
un browser diverso da Chrome si deve cambiare questo: 'self.driver = webdriver.Chrome()' e scaricare i webdriver appropriati per il
browser che si vuole utilizzare.

## branches

The following branches are automatically tested:
*	`main`
*	`testing`
*	`dev-*`
