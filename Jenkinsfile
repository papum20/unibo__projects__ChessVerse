
pipeline {
    agent any

    stages {
        stage('SCM') {
            steps {
                checkout scm
            }
        }

        stage('Build and Test Frontend') {
            steps {
                dir('code/app') {
                    nodejs(nodeJSInstallationName: 'NodeJS21_1_0') {
                        sh 'npm install'
                        sh 'npm run coverage:prod'
                    }
                }
            }
        }

        //stage('Build and Test Backend') {
        //    agent {
        //        label 'python'
        //    }
        //    steps {
        //        dir('code/backend') {
        //            // Add your Python testing commands here
        //            sh 'pip install -r requirements.txt'
        //            sh 'python -m unittest discover -s tests -p "*.py"'
        //        }
        //    }
        //}

        stage('SonarQube Analysis') {
            agent {
                label 'node'
            }
            steps {
                dir('code/app') {
                    nodejs(nodeJSInstallationName: 'NodeJS21_1_0') {
						script {
							def scannerHome = tool 'SonarScanner4'
							withSonarQubeEnv("sonarqube") {
								sh "${scannerHome}/bin/sonar-scanner"
							}
						}
                    }
                }
            }
        }
    }
}
