pipeline {
    agent any
    stages {
        stage('Check Python Version') {
            steps {
                sh 'which python3'
                sh 'python3 --version'
            }
        }
    }
}
