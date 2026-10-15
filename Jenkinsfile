pipeline {
    agent any

    environment {
        PYTHON_VERSION = '3.11'
        MLFLOW_TRACKING_URI = 'sqlite:///mlflow.db'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python -m pip install --upgrade pip
                    pip install -r requirements-dev.txt
                '''
            }
        }

        stage('Code Linting') {
            steps {
                sh '''
                    flake8 src tests --count --select=E9,F63,F7,F82 --show-source --statistics
                    flake8 src tests --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
                '''
            }
        }

        stage('Unit Testing') {
            steps {
                sh 'pytest tests/ -v --junitxml=pytest-results.xml'
            }
            post {
                always {
                    junit 'pytest-results.xml'
                }
            }
        }

        stage('Model Training & Benchmark') {
            steps {
                sh '''
                    python -m src.data_loader
                    python -m src.preprocessing
                    python -m src.train
                '''
            }
            post {
                success {
                    archiveArtifacts artifacts: 'models/**, reports/figures/**, reports/model_comparison.csv', fingerprint: true
                }
            }
        }

        stage('Docker Build & Verify') {
            steps {
                sh '''
                    docker build -t heart-disease-api:${BUILD_NUMBER} .
                    docker run -d -p 8000:8000 --name heart-api-${BUILD_NUMBER} heart-disease-api:${BUILD_NUMBER}
                    sleep 5
                    curl -f http://localhost:8000/health || exit 1
                    curl -f http://localhost:8000/metrics || exit 1
                    docker rm -f heart-api-${BUILD_NUMBER}
                '''
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
