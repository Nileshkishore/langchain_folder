pipeline {
    agent any

    stages {
        stage('Setup Virtual Environment') {
            steps {
                sh '''
                python -m venv venv
                source venv/bin/activate
                pip install --upgrade pip
                pip install -r requirenments.txt
                '''
            }
        }

        stage('Run Embedding Script') {
            steps {
                sh '''
                source venv/bin/activate
                python embedding.py
                '''
            }
        }

        stage('Cleanup') {
            steps {
                sh '''
                rm -rf venv
                '''
            }
        }
    }
}
