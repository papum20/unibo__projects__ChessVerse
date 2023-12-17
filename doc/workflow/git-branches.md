# Workflow and git branches

Our development is made of (design,) scripting and testing.  
Testing is automated thanks to Jenkins and SonarQube, which run our tests when a push is made to the appropriate branch on gitlab.  
Here we explain the purpose of each branch.  

## main

What is served in production. It must work at all times.  
Here tests are repeated on all services to be sure.  

## dev-*

For developing a service (or sometimes a feature).  
Names should be consistent between
*	service name
*	folder name (`code/SERVICE`)
*	git branch name (`dev-SERVICE`)

List:
-	`dev-app` : app, frontend  
-	`dev-api` : backend providing api    
-	`dev-game` : asynchronous backend, for asynchronous stuff with websockets    

Here tests are made only on the specific service.  

## testing

Here come together all services, before being pushed to `main`.  
These services must work on their own in the first place, so in `testing` they will only be tested to work well together, before serving them.  
