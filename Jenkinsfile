pipeline {
    agent any

    environment {
        DOCKERHUB_USER = 'allfridhosaragi'
        IMAGE = 'allfridhosaragi/ruangkita'
        TAG = "${env.BUILD_NUMBER}"
    }

    stages {
        // Stage 1: Checkout dari GitHub Repository
        stage('Checkout') {
            steps {
                echo '=== [Stage 1/6: Checkout] Mengambil source code dari SCM GitHub ==='
                checkout scm
            }
        }

        // Stage 2: Automated Testing (Quality Gate di dalam container)
        stage('Test') {
            steps {
                echo '=== [Stage 2/6: Test] Menjalankan automated test di dalam container ==='
                script {
                    if (isUnix()) {
                        sh "docker build --target test -t ${IMAGE}:test ."
                    } else {
                        bat "docker build --target test -t ${IMAGE}:test ."
                    }
                }
            }
        }

        // Stage 3: Build Image Docker (Multi-stage Production)
        stage('Build Image') {
            steps {
                echo "=== [Stage 3/6: Build Image] Membangun image tag: ${TAG} & latest ==="
                script {
                    if (isUnix()) {
                        sh "docker build -t ${IMAGE}:${TAG} -t ${IMAGE}:latest ."
                    } else {
                        bat "docker build -t ${IMAGE}:${TAG} -t ${IMAGE}:latest ."
                    }
                }
            }
        }

        // Stage 4: Push Image ke Docker Hub dengan Jenkins Credentials
        stage('Push Image') {
            steps {
                echo '=== [Stage 4/6: Push Image] Mengunggah image ke Docker Hub ==='
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials',
                                                 usernameVariable: 'DOCKER_USER',
                                                 passwordVariable: 'DOCKER_PASS')]) {
                    script {
                        if (isUnix()) {
                            sh 'echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin'
                            sh "docker push ${IMAGE}:${TAG}"
                            sh "docker push ${IMAGE}:latest"
                        } else {
                            bat "echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin"
                            bat "docker push ${IMAGE}:${TAG}"
                            bat "docker push ${IMAGE}:latest"
                        }
                    }
                }
            }
        }

        // Stage 5: Deploy dengan Docker Compose (Mencatat tag untuk Auto-Rollback K10)
        stage('Deploy') {
            steps {
                echo '=== [Stage 5/6: Deploy] Deployment kontainer via Docker Compose ==='
                script {
                    if (isUnix()) {
                        sh '''
                            CURRENT_TAG=$(docker inspect --format='{{.Config.Image}}' ruangkita_app 2>/dev/null | awk -F: '{print $2}')
                            if [ -z "$CURRENT_TAG" ]; then
                                CURRENT_TAG="latest"
                            fi
                            echo "$CURRENT_TAG" > .previous_deployed_tag
                            echo "[Deploy] Tag aktif sebelumnya: $CURRENT_TAG (disimpan untuk auto-rollback K10)"
                            APP_TAG=${TAG} docker compose pull app || true
                            APP_TAG=${TAG} docker compose up -d
                        '''
                    } else {
                        bat """
                            for /f "tokens=2 delims=:" %%a in ('docker inspect --format="{{.Config.Image}}" ruangkita_app 2^>nul') do echo %%a > .previous_deployed_tag
                            if not exist .previous_deployed_tag (echo latest > .previous_deployed_tag)
                            set APP_TAG=${TAG}
                            docker compose pull app || ver > nul
                            docker compose up -d
                        """
                    }
                }
            }
        }

        // Stage 6: Smoke Test (Menguji Endpoint /health)
        stage('Smoke Test') {
            steps {
                echo '=== [Stage 6/6: Smoke Test] Memvalidasi kesehatan endpoint /health ==='
                script {
                    if (isUnix()) {
                        sh '''
                            sleep 10
                            RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health || echo "000")
                            echo "[Smoke Test] HTTP Status: $RESPONSE"
                            if [ "$RESPONSE" != "200" ]; then
                                echo "[Smoke Test] GAGAL: Respons bukan 200 (didapat: $RESPONSE)!"
                                exit 1
                            fi
                            echo "[Smoke Test] SUKSES: Aplikasi beroperasi sehat (200 OK)."
                        '''
                    } else {
                        bat '''
                            timeout /t 10 /nobreak > nul
                            powershell -Command "$res = try { (Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing).StatusCode } catch { 500 }; Write-Output ('[Smoke Test] HTTP Status: ' + $res); if ($res -ne 200) { exit 1 }"
                        '''
                    }
                }
            }
        }
    }

    // Blok Post: Success & Auto-Rollback K10 pada Failure
    post {
        success {
            echo '========================================================================'
            echo "✅ [PIPELINE SUKSES] Build #${env.BUILD_NUMBER} berhasil melewati 6 stage!"
            echo '🚀 Status aplikasi: Sehat, kontainer berjalan, dan endpoint /health merespons 200'
            echo '========================================================================'
        }
        failure {
            echo '========================================================================'
            echo "🚨 [PIPELINE GAGAL] Build #${env.BUILD_NUMBER} mengalami kegagalan pada pipeline!"
            echo '⚡ [TANTANGAN K10: AUTO-ROLLBACK TRIGGERED] Mengembalikan versi ke tag sebelumnya...'
            script {
                if (isUnix()) {
                    sh '''
                        if [ -f .previous_deployed_tag ]; then
                            ROLLBACK_TAG=$(cat .previous_deployed_tag)
                            echo "[Auto-Rollback] Men-deploy ulang tag sebelumnya yang stabil: $ROLLBACK_TAG"
                            APP_TAG=$ROLLBACK_TAG docker compose up -d
                            sleep 5
                            echo "[Auto-Rollback] Status kontainer setelah rollback:"
                            docker compose ps
                        fi
                    '''
                } else {
                    bat '''
                        if exist .previous_deployed_tag (
                            set /p ROLLBACK_TAG=<.previous_deployed_tag
                            echo [Auto-Rollback] Men-deploy ulang tag stabil: %ROLLBACK_TAG%
                            set APP_TAG=%ROLLBACK_TAG%
                            docker compose up -d
                        )
                    '''
                }
            }
            echo '========================================================================'
        }
    }
}
