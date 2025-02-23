pipeline {
    agent any

    stages {
        stage('Setup Virtual Environment') {
            steps {
                sh '''
                python3 -m venv venv
                source venv/bin/activate
                pip install --upgrade pip setuptools wheel
                pip install -r requirenments.txt --no-cache-dir
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
