
pipeline {
    agent any

    stages {
        stage('SCM') {
            steps {
                checkout scm
            }
        }

        stage('Build and Test App') {
			when {
				anyOf {
					branch "main"
					branch "testing"
					branch "dev-app"
				}
			}
            steps {
                dir('code/app') {
                    nodejs(nodeJSInstallationName: 'NodeJS21_1_0') {
                        sh 'npm install'
                        sh 'npm run coverage:prod'
                    }
                }
            }
        }

        stage('Build and Test api backend') {
			when {
				anyOf {
					branch "main"
					branch "testing"
					branch "dev-api"
				}
			}
            steps {
                dir('code/api') {
                    // Add your Python testing commands here
                    sh 'pip install -r requirements.txt'
                    sh 'python -m unittest discover -s tests -p "*.py"'
                }
            }
        }

        stage('Build and Test async backend') {
			when {
				anyOf {
					branch "main"
					branch "testing"
					branch "dev-async"
				}
			}
            steps {
                dir('code/async') {
                    // Add your Python testing commands here
                    sh 'pip install -r requirements.txt'
                    sh 'python -m unittest discover -s tests -p "*.py"'
                }
            }
        }

        stage('SonarQube Analysis') {
			when {
				anyOf {
					branch "main"
					branch "testing"
				}
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
