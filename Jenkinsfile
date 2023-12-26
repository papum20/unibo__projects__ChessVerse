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
stage('E2E Tests') {
    when {
        anyOf {
            branch "main"
            branch "testing"
            branch "dev-game"
        }
    }
    steps {
        script {
            sh '''
           # Check if Google Chrome is installed
            if ! command -v google-chrome-stable &> /dev/null
            then
                # Install Google Chrome
                wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
                echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list
                apt-get update
                apt-get install -y google-chrome-stable
            fi

            # Check if Chrome WebDriver is installed
            if ! command -v /usr/bin/chromedriver &> /dev/null
            then

                # Download and install Chrome WebDriver
                wget "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/120.0.6099.109/linux64/chromedriver-linux64.zip" -O chromedriver_linux64.zip
                unzip chromedriver_linux64.zip
                mv chromedriver-linux64/chromedriver /usr/bin/chromedriver
                chown root:root /usr/bin/chromedriver
                chmod +x /usr/bin/chromedriver
            fi

            # Navigate to the directory containing your E2E tests
            cd code/e2e

            # Run your E2E tests
            pip3 install -r requirements.txt
            python3.12 e2etests.py

            '''
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
            sh 'python3.12 -m coverage run manage.py test'
            sh 'python3.12 -m coverage xml -i'
            sh '''
                if [ -f "coverage.xml" ]; then
                    echo "coverage.xml file is created."
                    echo "Path: $(pwd)/coverage.xml"
                else
                    echo "coverage.xml file is not created."
                fi
            '''
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
                    sh 'python3.12 -m coverage run -m unittest '
                    sh 'python3.12 -m coverage xml -i'
                    sh '''
                        if [ -f "coverage.xml" ]; then
                            echo "coverage.xml file is created."
                            echo "Path: $(pwd)/coverage.xml"
                        else
                            echo "coverage.xml file is not created."
                        fi
                    '''
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

