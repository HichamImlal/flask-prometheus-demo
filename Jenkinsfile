pipeline {
    agent any
    environment {
        SONAR_HOST_URL = "http://192.168.214.136:9000"
        SONAR_TOKEN = credentials('sonar')
        NVD_API_KEY = credentials('nvd')
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
                mkdir -p tests
                
                if [ ! -f "tests/test_app.py" ]; then
                    cat > tests/test_app.py <<EOL
from app import app
import pytest

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200

def test_metrics_endpoint(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert b'flask_http_request_total' in response.data
EOL
                fi

                python3 -m pytest tests/ --junitxml=test-results.xml --cov=app --cov-report=xml:coverage.xml || echo "Pytest completed"
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                    archiveArtifacts artifacts: 'test-results.xml,coverage.xml', allowEmptyArchive: true
                }
            }
        }
        
        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('sonar-docker') {
                    sh '''
                    /opt/sonar-scanner/bin/sonar-scanner \
                    -Dsonar.projectKey=SonarDemo \
                    -Dsonar.projectName=SonarDemo \
                    -Dsonar.sources=. \
                    -Dsonar.python.version=3 \
                    -Dsonar.host.url=${SONAR_HOST_URL} \
                    -Dsonar.login=${SONAR_TOKEN} \
                    -Dsonar.python.coverage.reportPaths=coverage.xml
                    '''
                }
            }
        }
        stage('Dependency-Check') {
    steps {
        timeout(time: 30, unit: 'MINUTES') {
            script {
                withEnv(["JAVA_OPTS=-Xmx4g -XX:MaxRAMPercentage=75.0"]) {
                    // Secure way to pass arguments
                    def additionalArgs = [
                        '--scan', './',
                        '--format', 'XML',
                        '--format', 'HTML',
                        '--out', './dependency-check-report',
                        '--enableExperimental',
                        '--disableArchive',
                        '--data', '/var/lib/jenkins/dependency-check-data',
                        '--project', 'Flask-demo-token'
                    ]
                    
                    // Only add NVD API key if it exists
                    if (NVD_API_KEY) {
                        additionalArgs.addAll(['--nvdApiKey', NVD_API_KEY])
                    }
                    
                    dependencyCheck(
                        additionalArguments: additionalArgs.join(' '),
                        odcInstallation: 'dc'
                    )
                }
            }
        }

        // Publish results
        dependencyCheckPublisher pattern: '**/dependency-check-report/dependency-check-report.xml'
        archiveArtifacts artifacts: 'dependency-check-report/*.*', fingerprint: true
        publishHTML(target: [
            allowMissing: false,
            alwaysLinkToLastBuild: true,
            keepAll: true,
            reportDir: 'dependency-check-report',
            reportFiles: 'dependency-check-report.html',
            reportName: 'OWASP Dependency-Check Report'
        ])
    }
}
        stage('Generate SBOM') { 
steps { 
sh ''' 
syft scan dir:. --output cyclonedx-json=sbom.json 
''' 
archiveArtifacts allowEmptyArchive: true, 
artifacts: 'sbom*', fingerprint: true, 
followSymlinks: false, onlyIfSuccessful: true 
sh ' rm -rf sbom*' 
} 
} 
        stage('Secret Detection') {
            steps {
                sh '/var/lib/jenkins/detect-secrets-venv/bin/detect-secrets scan --all-files > secrets.txt'
            }
        }
    }
}