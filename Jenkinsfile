pipeline {
    agent any

    stages {
        stage('SCM') {
            steps {
                checkout scm
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
                    sh 'pip3 install -r requirements.txt'
                    sh 'python3.12 manage.py test"'
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

