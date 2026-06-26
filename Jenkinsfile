pipeline {
    agent any

    // =============================================
    // 环境变量
    // =============================================
    environment {
        BASE_URL       = 'http://host.docker.internal:8080'
        BROWSER        = 'headlesschrome'
        DB_HOST        = 'host.docker.internal'
        DB_PORT        = '3307'
        DB_DATABASE    = 'wordpress'
        DB_TABLE_PREFIX = 'wp_'
        DB_USER        = 'root'
        DB_PASSWORD    = 'root_password'
        // 从 Jenkins Credentials 注入（敏感信息）
        WOO_KEY        = credentials('WOO_KEY')
        WOO_SECRET     = credentials('WOO_SECRET')
    }

    stages {

        // ===========================================
        // Stage 1: 拉取代码
        // ===========================================
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        // ===========================================
        // Stage 2: 启动测试基础设施 (WordPress + MySQL)
        // ===========================================
        stage('Setup Test Infrastructure') {
            steps {
                script {
                    // 先停掉可能残留的旧容器，避免名称冲突
                    sh 'docker compose down --remove-orphans 2>/dev/null || true'
                    sh 'docker compose up -d'

                    sh '''
                        echo "等待 WordPress 启动..."
                        for i in $(seq 1 36); do
                            STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://host.docker.internal:8080 2>/dev/null || echo "000")
                            if [ "$STATUS" = "200" ] || [ "$STATUS" = "302" ]; then
                                echo "WordPress 已就绪 (HTTP $STATUS)"
                                break
                            fi
                            echo "   等待中... ($i/36)"
                            sleep 5
                        done
                    '''
                }
            }
        }

        // ===========================================
        // Stage 3: 后端 API 测试
        // ===========================================
        stage('Backend Tests') {
            agent {
                docker {
                    image 'python:3.11'
                    reuseNode true
                    args "-e BASE_URL=${BASE_URL} -e BROWSER=${BROWSER} -e DB_HOST=${DB_HOST} -e DB_PORT=${DB_PORT} -e DB_DATABASE=${DB_DATABASE} -e DB_TABLE_PREFIX=${DB_TABLE_PREFIX} -e DB_USER=${DB_USER} -e DB_PASSWORD=${DB_PASSWORD} -e WOO_KEY=${WOO_KEY} -e WOO_SECRET=${WOO_SECRET}"
                }
            }
            steps {
                sh 'pip install -r requirements.txt'
                sh '''
                    cd demostore_automation
                    python -m pytest tests/test_healthcheck.py tests/backend/ -v \
                        --tb=short \
                        --html=reports/report_backend.html \
                        --self-contained-html
                '''
            }
        }

        // ===========================================
        // Stage 4: 前端冒烟测试（需要 Chrome）
        // ===========================================
        stage('Frontend Smoke Tests') {
            agent {
                docker {
                    image 'python:3.11'
                    reuseNode true
                    args "-u root -e BASE_URL=${BASE_URL} -e BROWSER=${BROWSER} -e DB_HOST=${DB_HOST} -e DB_PORT=${DB_PORT} -e DB_DATABASE=${DB_DATABASE} -e DB_TABLE_PREFIX=${DB_TABLE_PREFIX} -e DB_USER=${DB_USER} -e DB_PASSWORD=${DB_PASSWORD} -e WOO_KEY=${WOO_KEY} -e WOO_SECRET=${WOO_SECRET}"
                }
            }
            steps {
                sh 'pip install -r requirements.txt'
                // 安装 Chrome（前端 Selenium 测试需要）
                sh '''
                    apt-get update -qq && apt-get install -y -qq wget gnupg
                    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg
                    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
                    apt-get update -qq && apt-get install -y -qq google-chrome-stable
                '''
                sh '''
                    cd demostore_automation
                    python -m pytest tests/frontend/ -v \
                        -m "fesmoke" \
                        --tb=short \
                        --html=reports/report_frontend.html \
                        --self-contained-html
                '''
            }
        }
    }

    // =============================================
    // Post: 无论成功或失败都执行
    // =============================================
    post {
        always {
            sh 'docker compose down || true'
            // 修复 root 用户产生的文件权限，确保 Jenkins 可归档
            sh 'chmod -R 755 demostore_automation/reports/ || true'
            archiveArtifacts artifacts: 'demostore_automation/reports/**', allowEmptyArchive: true
        }
        success {
            echo '所有测试通过！'
        }
        failure {
            echo '测试未通过，请检查报告。'
        }
    }
}
