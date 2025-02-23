pipeline {
    agent any
    environment {
        PATH = "/usr/local/bin:$PATH"  // Adjust based on your system
    }
    stages {
        stage('Check Python Version') {
            steps {
                sh 'python3 --version'
            }
        }
    }
}
