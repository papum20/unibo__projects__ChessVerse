pipeline {
    agent any

    stages {
        stage('SCM') {
            steps {
                checkout scm
            }
        }
     stage('Setup') {
    steps {
        script {
            sh '''
            if ! command -v docker-compose &> /dev/null
            then
                echo "docker-compose could not be found"
                echo "Installing docker-compose"
                curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                chmod +x /usr/local/bin/docker-compose
            fi
            '''
           
        }
    }
}
stage('Setup DB') {
    steps {
        dir('db/'){
             sh '''
            if [ $(docker ps -a -q -f name=mysql) ]; then
                docker stop mysql
                docker rm mysql
            fi
            '''
            sh '''
            docker-compose up -d
            '''
        }
    }
}
stage('Install MySQL Client') {
    steps {
        script {
            // Run the installation command for default-mysql-client
            sh 'apt-get update && apt-get install -y default-mysql-client'
        }
    }
}
    stage('Check MySQL') {
    steps {
        script {
            sh '''
            mysqladmin --verbose --wait=30 -hmysql -uroot -proot ping || exit 1
            '''
        }
    }
}
stage('Create DB') {
    steps {
        script {
            sh '''
            mysql -hmysql -uroot -proot -e "CREATE DATABASE IF NOT EXISTS users_db;"
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
            sh 'rm -rf Python-3.12.0'
            sh 'python3.12 -m coverage run manage.py test'
            sh 'python3.12 -m coverage xml -i'
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
                    sh 'python3.12 -m coverage run -m unittest '
                    sh 'python3.12 -m coverage xml -i'
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
            nodejs(nodeJSInstallationName: 'NodeJS21_1_0') {
                script {
                    def scannerHome = tool 'SonarScanner4'
                    withSonarQubeEnv("sonarqube") {
                        sh "${scannerHome}/bin/sonar-scanner -Dsonar.verbose=true"
                    }
                }
            }
        }
        }

    }
}

