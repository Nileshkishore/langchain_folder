pipeline {
    agent any
    parameters {
        choice(name: 'STAGE_TO_RUN', choices: ['Create Virtual Environment', 'Run MLflow', 'Run Embedding Script', 'Run Main Script', 'Cleanup'], description: 'Choose which stage to execute')
    }
    environment {
        PATH = "/Users/nileshkishore/anaconda3/bin:$PATH"
    }
    stages {
        stage('Create Virtual Environment') {
            when {
                expression { return params.STAGE_TO_RUN == 'Create Virtual Environment' }
            }
            steps {
                sh '''
                    python3 -m venv venv
                    source venv/bin/activate
                    which python3
                    python3 --version
                '''
            }
        }

        stage('Run MLflow') {
            when {
                expression { return params.STAGE_TO_RUN == 'Run MLflow' }
            }
            steps {
                sh '''
                    source venv/bin/activate
                    mlflow ui --host 0.0.0.0 --port 5000 &
                    echo "MLflow server running..."
                '''
            }
        }

        stage('Run Embedding Script') {
            when {
                expression { return params.STAGE_TO_RUN == 'Run Embedding Script' }
            }
            steps {
                sh '''
                    source venv/bin/activate
                    python3 embedding.py
                '''
            }
        }

        stage('Run Main Script') {
            when {
                expression { return params.STAGE_TO_RUN == 'Run Main Script' }
            }
            steps {
                sh '''
                    source venv/bin/activate
                    python3 main.py
                '''
            }
        }

        stage('Cleanup') {
            when {
                expression { return params.STAGE_TO_RUN == 'Cleanup' }
            }
            steps {
                sh '''
                    echo "Removing virtual environment..."
                    rm -rf venv
                    echo "Cleanup completed!"
                '''
            }
        }
    }
    post {
        always {
            echo "Pipeline execution completed"
        }
    }
}
