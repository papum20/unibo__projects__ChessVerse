node {
	stage('SCM') {
		checkout scm
	}
	stage('SonarQube Analysis') {
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
