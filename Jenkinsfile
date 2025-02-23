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
                script {
                    // Ensure we're operating in the current workspace
                    def workspaceDir = pwd()
                    echo "Current Workspace: ${workspaceDir}"

                    // Check if the virtual environment exists in the workspace
                    def venvExists = fileExists("${workspaceDir}/venv")
                    if (!venvExists) {
                        // If venv doesn't exist, create it
                        sh """
                            python3 -m venv ${workspaceDir}/venv
                            source ${workspaceDir}/venv/bin/activate
                            which python3
                            python3 --version
                        """
                    } else {
                        echo "Virtual environment already exists."
                    }
                }
            }
        }

        stage('Install Dependencies') {
            when {
                expression { return params.STAGE_TO_RUN == 'Create Virtual Environment' || params.STAGE_TO_RUN == 'Run Embedding Script' || params.STAGE_TO_RUN == 'Run Main Script' }
            }
            steps {
                script {
                    // Ensure we're operating in the current workspace
                    def workspaceDir = pwd()
                    echo "Current Workspace: ${workspaceDir}"

                    // Install dependencies in the current workspace's venv
                    sh """
                        source ${workspaceDir}/venv/bin/activate
                        pip install -r ${workspaceDir}/requirements.txt
                    """
                }
            }
        }

        stage('Run MLflow') {
            when {
                expression { return params.STAGE_TO_RUN == 'Run MLflow' }
            }
            steps {
                script {
                    def workspaceDir = pwd()
                    echo "Current Workspace: ${workspaceDir}"

                    // Run MLflow UI in the current workspace's venv
                    sh """
                        source ${workspaceDir}/venv/bin/activate
                        mlflow ui
                        echo "MLflow server running..."
                    """
                }
            }
        }

        stage('Run Embedding Script') {
            when {
                expression { return params.STAGE_TO_RUN == 'Run Embedding Script' }
            }
            steps {
                script {
                    def workspaceDir = pwd()
                    echo "Current Workspace: ${workspaceDir}"

                    // Run the embedding script in the current workspace's venv
                    sh """
                        source ${workspaceDir}/venv/bin/activate
                        python3 ${workspaceDir}/embedding.py
                    """
                }
            }
        }

        stage('Run Main Script') {
            when {
                expression { return params.STAGE_TO_RUN == 'Run Main Script' }
            }
            steps {
                script {
                    def workspaceDir = pwd()
                    echo "Current Workspace: ${workspaceDir}"

                    // Run the main script in the current workspace's venv
                    sh """
                        source ${workspaceDir}/venv/bin/activate
                        python3 ${workspaceDir}/main.py
                    """
                }
            }
        }

        stage('Cleanup') {
            when {
                expression { return params.STAGE_TO_RUN == 'Cleanup' }
            }
            steps {
                script {
                    def workspaceDir = pwd()
                    echo "Current Workspace: ${workspaceDir}"

                    // Remove virtual environment in the current workspace
                    echo "Removing virtual environment..."
                    sh "rm -rf ${workspaceDir}/venv"
                    echo "Cleanup completed!"
                }
            }
        }
    }
    post {
        always {
            echo "Pipeline execution completed"
        }
    }
}
