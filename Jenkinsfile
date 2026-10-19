pipeline {
    agent any
    environment { PYTHON_VERSION = '3.12' }
    stages {
        stage('Install') {
            steps { sh 'python3.12 -m venv .venv && . .venv/bin/activate && pip install --upgrade pip && pip install -r requirements-dev.txt' }
        }
        stage('Lint and test') {
            steps { sh '. .venv/bin/activate && mkdir -p ci-logs && flake8 src test --max-complexity=10 --max-line-length=127 2>&1 | tee ci-logs/flake8.log && pytest test/ -v --junitxml=pytest-results.xml --cov=src --cov-report=xml 2>&1 | tee ci-logs/pytest.log' }
            post { always { junit 'pytest-results.xml'; archiveArtifacts artifacts: 'ci-logs/**,coverage.xml', allowEmptyArchive: true } }
        }
        stage('Train') {
            steps { sh '. .venv/bin/activate && python -m src.data_loader && python -m src.preprocessing && python -m src.eda && python -m src.train' }
        }
        stage('Docker verify') {
            steps { sh '''
                set -e
                docker build -t heart-disease-api:${BUILD_NUMBER} .
                docker run -d -p 8000:8000 --name heart-api-${BUILD_NUMBER} heart-disease-api:${BUILD_NUMBER}
                for i in $(seq 1 30); do curl -fsS http://localhost:8000/health && break || [ "$i" = 30 ] && exit 1; sleep 1; done
                . .venv/bin/activate && python scripts/test_serving.py
            ''' }
        }
    }
    post {
        always {
            sh 'docker logs heart-api-${BUILD_NUMBER} > ci-logs/docker.log 2>&1 || true; docker rm -f heart-api-${BUILD_NUMBER} || true'
            archiveArtifacts artifacts: 'models/**,reports/figures/**,reports/*.csv,reports/*.md,mlflow.db,ci-logs/**', allowEmptyArchive: true
        }
    }
}
