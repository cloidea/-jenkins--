pipeline {
    agent any

    environment {
        BASE_URL       = 'http://host.docker.internal:8080'
        BROWSER        = 'headlesschrome'
        DB_HOST        = 'host.docker.internal'
        DB_PORT        = '3307'
        DB_DATABASE    = 'wordpress'
        DB_TABLE_PREFIX = 'wp_'
        DB_USER        = 'root'
        DB_PASSWORD    = 'root_password'
        PYTHONPATH     = "${WORKSPACE}"
        WOO_KEY        = credentials('WOO_KEY')
        WOO_SECRET     = credentials('WOO_SECRET')
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Test Infrastructure') {
            steps {
                script {
                    // Docker Hub 登录
                    withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials',
                                                      usernameVariable: 'DH_USER',
                                                      passwordVariable: 'DH_PASS')]) {
                        sh 'echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin'
                    }

                    // 清理旧容器，启动新容器
                    sh 'docker rm -f wc_db wc_site 2>/dev/null || true'
                    sh 'docker compose up -d'

                    // MySQL 权限修复：允许 root 从任意主机（含 host.docker.internal）密码登录
                    sh '''
                        echo "=== 等待 MySQL 就绪 ==="
                        until docker exec wc_db mysqladmin ping -h localhost --silent 2>/dev/null; do
                            sleep 2
                        done
                        docker exec wc_db mysql -u root -proot_password -e "
                            ALTER USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'root_password';
                            GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
                            FLUSH PRIVILEGES;
                        " 2>/dev/null
                        echo "MySQL 权限已配置"
                    '''

                    // ========================================
                    // 阶段 1: 等待容器响应
                    // ========================================
                    sh '''
                        echo "=== 阶段 1: 等待 WordPress 容器响应 ==="
                        max=36
                        status=""
                        for i in $(seq 1 $max); do
                            status=$(curl -s -o /dev/null -w "%{http_code}" http://host.docker.internal:8080 2>/dev/null || echo "000")
                            if [ "$status" = "200" ] || [ "$status" = "302" ] || [ "$status" = "301" ]; then
                                echo "容器已响应 (HTTP $status) — 第 $i 次"
                                break
                            fi
                            echo "  等待... ($i/$max)"
                            sleep 5
                        done
                        if [ "$status" != "200" ] && [ "$status" != "302" ] && [ "$status" != "301" ]; then
                            echo "ERROR: 3 分钟无响应，终止"
                            exit 1
                        fi
                    '''

                    // ========================================
                    // 阶段 2: 检查是否已安装，未安装则自动安装
                    // ========================================
                    sh '''
                        echo "=== 阶段 2: 检查 WordPress 安装状态 ==="
                        check=$(curl -s -o /dev/null -w "%{http_code}" http://host.docker.internal:8080/wp-json/ 2>/dev/null || echo "000")
                        if [ "$check" = "200" ]; then
                            echo "WordPress 已安装，跳过安装步骤"
                        else
                            echo "未安装 (HTTP $check)，开始安装..."

                            # 下载 wp-cli.phar 到宿主机，再 cp 进容器
                            if [ ! -f wp-cli.phar ]; then
                                curl -sO https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar
                            fi
                            docker cp wp-cli.phar wc_site:/usr/local/bin/wp
                            docker exec wc_site chmod +x /usr/local/bin/wp

                            docker exec wc_site wp core install \\
                                --url="http://host.docker.internal:8080" \\
                                --title="Test Store" \\
                                --admin_user="admin" \\
                                --admin_password="admin_password" \\
                                --admin_email="admin@test.com" \\
                                --path="/var/www/html" \\
                                --skip-email \\
                                --allow-root

                            if [ $? -ne 0 ]; then
                                echo "ERROR: WordPress 安装失败"
                                exit 1
                            fi
                            echo "WordPress 安装完成"

                            # 安装并激活 WooCommerce 插件（API 路由 wc/v3 依赖此插件）
                            echo "安装 WooCommerce 插件..."
                            docker exec wc_site wp plugin install woocommerce --activate --allow-root --path="/var/www/html"
                            if [ $? -ne 0 ]; then
                                echo "ERROR: WooCommerce 安装失败"
                                exit 1
                            fi
                            echo "WooCommerce 安装并激活完成"
                        fi
                    '''

                    // ========================================
                    // 阶段 3: 确认 REST API 可用
                    // ========================================
                    sh '''
                        echo "=== 阶段 3: 确认 REST API ==="
                        verify=$(curl -s http://host.docker.internal:8080/wp-json/ 2>/dev/null | head -c 100)
                        if echo "$verify" | grep -q '"name"'; then
                            echo "REST API 就绪，开始测试"
                        else
                            echo "ERROR: REST API 不可用"
                            echo "响应: $verify"
                            exit 1
                        fi
                    '''
                }
            }
        }

        // ============================================
        // Stage 3: 后端 API 测试
        // ============================================
        stage('Backend Tests') {
            agent {
                docker {
                    image 'python:3.11'
                    reuseNode true
                    args "-u root --add-host=host.docker.internal:host-gateway -e BASE_URL=${BASE_URL} -e BROWSER=${BROWSER} -e DB_HOST=${DB_HOST} -e DB_PORT=${DB_PORT} -e DB_DATABASE=${DB_DATABASE} -e DB_TABLE_PREFIX=${DB_TABLE_PREFIX} -e DB_USER=${DB_USER} -e DB_PASSWORD=${DB_PASSWORD} -e WOO_KEY=${WOO_KEY} -e WOO_SECRET=${WOO_SECRET}"
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

        // ============================================
        // Stage 4: 前端冒烟测试
        // ============================================
        stage('Frontend Smoke Tests') {
            agent {
                docker {
                    image 'python:3.11'
                    reuseNode true
                    args "-u root --add-host=host.docker.internal:host-gateway -e BASE_URL=${BASE_URL} -e BROWSER=${BROWSER} -e DB_HOST=${DB_HOST} -e DB_PORT=${DB_PORT} -e DB_DATABASE=${DB_DATABASE} -e DB_TABLE_PREFIX=${DB_TABLE_PREFIX} -e DB_USER=${DB_USER} -e DB_PASSWORD=${DB_PASSWORD} -e WOO_KEY=${WOO_KEY} -e WOO_SECRET=${WOO_SECRET}"
                }
            }
            steps {
                sh 'pip install -r requirements.txt'
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

    post {
        always {
            sh 'docker compose down || true'
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
