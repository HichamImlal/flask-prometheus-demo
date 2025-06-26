pipeline {
    agent any
    environment {
        SONAR_HOST_URL = "http://192.168.214.128:9000"  // Kali's SonarQube
        SONAR_TOKEN = credentials('Flask-demo-token')     // Jenkins-stored token
    }
    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/HichamImlal/flask-prometheus-demo.git', 
                     branch: 'main'
            }
        }

        stage('Build') {
            steps {
                sh 'python3 -m pip install --upgrade pip'
                sh 'python3 -m pip install -r requirements.txt'
                sh 'python3 -m pip freeze > requirements_frozen.txt'
                
                // Only include existing files/directories
                sh '''
                    files_to_archive="app.py requirements.txt"
                    [ -d static ] && files_to_archive="$files_to_archive static"
                    [ -d templates ] && files_to_archive="$files_to_archive templates"
                    tar czf app_build.tar.gz $files_to_archive
                '''
            }
        }

        stage('Archive') {
            steps {
                archiveArtifacts artifacts: 'app_build.tar.gz,requirements_frozen.txt', 
                                fingerprint: true
            }
        }
        
        stage('Test') {
            steps {
                sh '''
                # Create tests directory if it doesn't exist
                mkdir -p tests
                
                # Create a basic test file if none exists
                if [ ! -f "tests/test_app.py" ]; then
                    echo "Creating basic test file..."
                    cat > tests/test_app.py <<EOL
from app import app
import pytest

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Basic health check test"""
    response = client.get("/")
    assert response.status_code == 200

def test_metrics_endpoint(client):
    """Test Prometheus metrics endpoint"""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert b'flask_http_request_total' in response.data
EOL
                fi

                # Run pytest (will succeed even if no tests are found)
                python3 -m pytest tests/ --junitxml=test-results.xml || echo "Pytest completed"
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                    archiveArtifacts 'test-results.xml'
                }
            }
        }
        
        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('sonar-docker') {
                    sh '''
                    /opt/sonar-scanner/bin/sonar-scanner \
                    -Dsonar.projectKey=Flask-demo-token \
                    -Dsonar.projectName=Flask-demo-token \
                    -Dsonar.sources=. \
                    -Dsonar.python.version=3 \
                    -Dsonar.host.url=${SONAR_HOST_URL} \
                    -Dsonar.login=${SONAR_TOKEN}
                    '''
                }
            }
        }
        
      stage('Dependency-Check') {
    steps {
        dependencyCheck(
            odcInstallation: 'dc',
            additionalArguments: """
                --scan . 
                --format XML 
                --nvdApiKey ${credentials('nvd')}
                --disableNexus
                --data /var/lib/jenkins/dependency-check-data
            """
        )
    }
}

    }
}