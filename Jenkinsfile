pipeline {
    agent any

    stages {
        stage('SCM') {
            steps {
                checkout scm
            }
        }
        stage('Cleanup previous DB') {
        steps {
            script {
                sh '''
                if [ $(docker ps -a -q -f name=mysql) ]; then
                    docker stop mysql
                    docker rm mysql
                fi
                '''
            }
        }
    }
        stage('Setup DB') {
            steps {
                script {
                    dir('code/database') {
                        sh '''
                            docker build -t my-mysql dockerfile
                        '''
                    }
                    sh 'sleep 30'
                    sh '''
                    docker exec -i mysql mysql -uroot -proot -e "CREATE DATABASE IF NOT EXISTS users_db; USE users_db;"
                    '''
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

        // stage('Build and Test App') {
		// 	when {
		// 		anyOf {
		// 			branch "main"
		// 			branch "testing"
		// 			branch "dev-app"
		// 		}
		// 	}
        //     steps {
        //         dir('code/app') {
        //             nodejs(nodeJSInstallationName: 'NodeJS21_1_0') {
        //                 sh 'npm install'
        //                 sh 'npm run coverage:prod'
        //             }
        //         }
        //     }
        // }

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
                    // to fix
                    sh 'python3.12 -m unittest unit_test.TestChessSocketIO'
                }
            }
        }
        stage('Cleanup DB') {
            steps {
                script {
                    sh '''
                    docker stop mysql
                    docker rm mysql
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

