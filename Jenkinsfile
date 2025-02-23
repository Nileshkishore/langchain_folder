pipeline {
    agent any
    environment {
        PATH = "/Users/nileshkishore/anaconda3/bin:$PATH"
    }
    stages {
        stage('Check Python Version') {
            steps {
                sh 'which python3'
                sh 'python3 --version'
            }
        }
    }
}
