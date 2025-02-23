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
        stage('Create Virtual Environment') {
            steps {
                sh '''
                    python3 -m venv venv
                    source venv/bin/activate
                    which python3
                    python3 --version
                '''
            }
        }
        stage('Install Dependencies') {
            steps {
                sh '''
                    source venv/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }
        stage('Run Embedding Script') {
            steps {
                sh '''
                    source venv/bin/activate
                    python3 embedding.py
                '''
            }
        }
    }
    post {
        always {
            sh '''
                echo "Removing virtual environment..."
                rm -rf venv
                echo "Cleanup completed!"
            '''
        }
    }
}
