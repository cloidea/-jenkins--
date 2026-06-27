pipeline {
    agent any

    // =============================================
    // 环境变量
    // =============================================
    environment {
        // 所有容器同处 ecom-testing-net 网络，用服务名互访，无端口歧义
        BASE_URL       = 'http://wc_site'
        BROWSER        = 'headlesschrome'
        DB_HOST        = 'wc_db'
        DB_PORT        = '3306'
        DB_DATABASE    = 'wordpress'
        DB_TABLE_PREFIX = 'wp_'
        DB_USER        = 'root'
        DB_PASSWORD    = 'root_password'
        PYTHONPATH     = "${WORKSPACE}"
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
                    // Docker Hub 登录，避免未认证拉取速率限制
                    withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials',
                                                      usernameVariable: 'DH_USER',
                                                      passwordVariable: 'DH_PASS')]) {
                        sh 'echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin'
                    }
                    // 强制删除同名旧容器
                    sh 'docker rm -f wc_db wc_site 2>/dev/null || true'
                    sh 'docker compose up -d'

                    sh '''
                        echo "============================================="
                        echo "阶段 1: 等待 WordPress 容器启动..."
                        echo "============================================="
                        max_times=36
                        wp_responding=""
                        for i in $(seq 1 $max_times); do
                            wp_responding=$(curl -s -o /dev/null -w "%{http_code}" http://wc_site 2>/dev/null || echo "000")
                            if [ "$wp_responding" = "200" ] || [ "$wp_responding" = "302" ] || [ "$wp_responding" = "301" ]; then
                                echo "WordPress 容器已响应 (HTTP $wp_responding) — 第 ${i} 次检查"
                                break
                            fi
                            echo "   等待容器启动... ($i/$max_times)"
                            sleep 5
                        done
                        if [ "$wp_responding" != "200" ] && [ "$wp_responding" != "302" ] && [ "$wp_responding" != "301" ]; then
                            echo "ERROR: 等待 3 分钟后 WordPress 容器仍无响应，构建终止"
                            exit 1
                        fi

                        echo ""
                        echo "============================================="
                        echo "阶段 2: 检查 WordPress 是否已安装..."
                        echo "============================================="
                        # /wp-json/ 返回 200 → REST API 就绪（真就绪）
                        # /wp-json/ 返回 404/302 → 站点未安装（假就绪，仅容器在跑）
                        install_check=$(curl -s -o /dev/null -w "%{http_code}" http://wc_site/wp-json/ 2>/dev/null || echo "000")
                        if [ "$install_check" = "200" ]; then
                            echo "WordPress 已安装，REST API 可用"
                        else
                            echo "WordPress 未安装 (HTTP $install_check)，执行自动安装..."
                            # wp-cli 不在 WordPress 镜像内，用独立 wordpress:cli 容器执行
                            # --volumes-from wc_site 复用 WordPress 文件，同网络直连数据库
                            docker run --rm \\
                                --network ecom-testing-net \\
                                --volumes-from wc_site \\
                                wordpress:cli wp core install \\
                                --url="http://wc_site" \\
                                --title="Test Store" \\
                                --admin_user="admin" \\
                                --admin_password="admin_password" \\
                                --admin_email="admin@test.com" \\
                                --path="/var/www/html" \\
                                --skip-email
                            if [ $? -eq 0 ]; then
                                echo "WordPress 安装成功"
                            else
                                echo "ERROR: WordPress 安装失败，构建终止"
                                exit 1
                            fi
                        fi

                        echo ""
                        echo "============================================="
                        echo "阶段 3: 确认 REST API 可用..."
                        echo "============================================="
                        api_verify=$(curl -s -o /dev/null -w "%{http_code}" http://wc_site/wp-json/ 2>/dev/null || echo "000")
                        if [ "$api_verify" = "200" ]; then
                            echo "REST API 就绪 (HTTP 200)，开始执行测试"
                        else
                            echo "ERROR: REST API 不可用 (HTTP $api_verify)，构建终止"
                            exit 1
                        fi
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
                    args "-u root --network ecom-testing-net -e BASE_URL=${BASE_URL} -e BROWSER=${BROWSER} -e DB_HOST=${DB_HOST} -e DB_PORT=${DB_PORT} -e DB_DATABASE=${DB_DATABASE} -e DB_TABLE_PREFIX=${DB_TABLE_PREFIX} -e DB_USER=${DB_USER} -e DB_PASSWORD=${DB_PASSWORD} -e WOO_KEY=${WOO_KEY} -e WOO_SECRET=${WOO_SECRET}"
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
                    args "-u root --network ecom-testing-net -e BASE_URL=${BASE_URL} -e BROWSER=${BROWSER} -e DB_HOST=${DB_HOST} -e DB_PORT=${DB_PORT} -e DB_DATABASE=${DB_DATABASE} -e DB_TABLE_PREFIX=${DB_TABLE_PREFIX} -e DB_USER=${DB_USER} -e DB_PASSWORD=${DB_PASSWORD} -e WOO_KEY=${WOO_KEY} -e WOO_SECRET=${WOO_SECRET}"
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
