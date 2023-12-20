pipeline {
    agent any

    stages {
         stage('Install Docker Compose') {
            steps {
                script {
                    sh '''
                    sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                    sudo chmod +x /usr/local/bin/docker-compose
                    '''
                }
            }
        }
        stage('SCM') {
            steps {
                checkout scm
            }
        }
        stage('Cleanup previous DB') {
            steps {
               script {
                   sh '''
                   docker-compose -f ./docker-compose.yml down
                   '''
                }
           }
       }
        stage('Setup DB') {
            steps {
                script {
                    sh '''
                    docker-compose -f ./docker-compose.yml up -d
                    '''
                    sh 'sleep 30'
                }
            }
        }

        stage('Migrate DB') {
            steps {
                dir('code/api'){
                    sh 'pip3 install -r requirements.txt'
                    sh 'python3.12 manage.py makemigrations'
                    sh 'python3.12 manage.py migrate'
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
                    sh 'python3.12 manage.py test'
                }
            }
        }

        stage('Build and Test game backend') {
			when {
				anyOf {
					branch "main"
					branch "testing"
					branch "dev-game"
				}
			}
            steps {
                dir('code/game/') {
                    sh 'pip3 install -r requirements.txt'
                }
                dir('code/game/test/unit') {
                    sh 'python3.12 -m unittest unit_test.TestChessSocketIO'
                }
            }
        }
        stage('Cleanup DB') {
            steps {
                script {
                    sh '''
                    docker-compose -f ./code/database/docker-compose.yml down
                    '''
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
