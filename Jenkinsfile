node {
	stages {
		stage('SCM') {
			steps {
				checkout scm
			}
		}
		stage('SonarQube Analysis') {
			steps {

				nodejs(nodeJSInstallationName: 'NodeJS21_1_0') {
					def scannerHome = tool 'SonarScanner4';
					withSonarQubeEnv() {
						sh 'node -v' // This should print the Node.js version.
						sh "${scannerHome}/bin/sonar-scanner"
					}
				}
			}
		}
	}
}
