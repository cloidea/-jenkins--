pipeline {
    agent any

    // =============================================
    // 环境变量 — 测试容器走 Docker 内网服务名
    // =============================================
    environment {
        BASE_URL       = 'http://wc_site'
        BROWSER        = 'headlesschrome'
        DB_HOST        = 'wc_db'
        DB_PORT        = '3306'
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
            steps { checkout scm }
        }

        // ============================================
        // Stage 2: 基础设施 + WordPress 安装 + WooCommerce 激活
        // ============================================
        stage('Setup Test Infrastructure') {
            steps {
                script {
                    // Docker Hub 登录
                    withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials',
                                                      usernameVariable: 'DH_USER',
                                                      passwordVariable: 'DH_PASS')]) {
                        sh 'echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin'
                    }

                    // 启动 MySQL + WordPress
                    sh 'docker rm -f wc_db wc_site 2>/dev/null || true'
                    sh 'docker compose up -d'

                    // ---- MySQL 权限：root@% 和 root@localhost 双通道授权 ----
                    sh '''
                        echo "=== 等待 MySQL 就绪 ==="
                        until docker exec wc_db mysqladmin ping -h localhost --silent 2>/dev/null; do
                            sleep 2
                        done
                        docker exec wc_db mysql -u root -proot_password -e "
                            ALTER USER 'root'@'%'       IDENTIFIED WITH mysql_native_password BY 'root_password';
                            ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root_password';
                            GRANT ALL PRIVILEGES ON *.* TO 'root'@'%'       WITH GRANT OPTION;
                            GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
                            FLUSH PRIVILEGES;
                        "
                        echo "MySQL root 权限已配置 (% + localhost)"
                    '''

                    // ---- 等待 WordPress 容器响应 ----
                    sh '''
                        echo "=== 等待 WordPress 容器响应 ==="
                        max=36; s=""
                        for i in $(seq 1 $max); do
                            s=$(curl -s -o /dev/null -w "%{http_code}" http://host.docker.internal:8080 2>/dev/null || echo "000")
                            case "$s" in 200|302|301) echo "容器已响应 (HTTP $s)"; break ;; esac
                            echo "  等待... ($i/$max)"; sleep 5
                        done
                        case "$s" in 200|302|301) ;; *) echo "ERROR: 3分钟无响应"; exit 1 ;; esac
                    '''

                    // ---- 安装 wp-cli（始终安装，后续步骤依赖） ----
                    sh '''
                        echo "=== 安装 wp-cli ==="
                        if [ ! -f wp-cli.phar ]; then
                            curl -sSfLo wp-cli.phar https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar
                        fi
                        docker cp wp-cli.phar wc_site:/usr/local/bin/wp
                        docker exec wc_site chmod +x /usr/local/bin/wp
                        echo "wp-cli 就绪"
                    '''

                    // ---- WordPress core install（如未安装） ----
                    sh '''
                        echo "=== 检查 WordPress 安装 ==="
                        if docker exec wc_site wp core is-installed --allow-root --path=/var/www/html 2>/dev/null; then
                            echo "WordPress 已安装"
                        else
                            echo "执行 WordPress 安装..."
                            docker exec wc_site wp core install \
                                --url="http://wc_site" \
                                --title="Test Store" \
                                --admin_user="admin" \
                                --admin_password="admin_password" \
                                --admin_email="admin@test.com" \
                                --path="/var/www/html" \
                                --skip-email \
                                --allow-root
                            if [ $? -ne 0 ]; then
                                echo "ERROR: WordPress 安装失败"; exit 1
                            fi
                            echo "WordPress 安装完成"
                        fi
                    '''

                    // ---- WooCommerce 离线安装（在线仓库国内不通） ----
                    sh '''
                        echo "=== 检查 WooCommerce ==="
                        if docker exec wc_site wp plugin is-active woocommerce --allow-root --path=/var/www/html 2>/dev/null; then
                            echo "WooCommerce 已激活，跳过"
                        else
                            # 安装方式：优先用项目内预置 zip，次选在线下载
                            WOO_ZIP="woocommerce.zip"
                            if [ -f "$WOO_ZIP" ]; then
                                echo "使用本地 $WOO_ZIP 安装..."
                                docker cp "$WOO_ZIP" wc_site:/tmp/woocommerce.zip
                                docker exec wc_site wp plugin install /tmp/woocommerce.zip --activate --allow-root --path=/var/www/html
                            else
                                echo "本地无 $WOO_ZIP，尝试在线安装..."
                                docker exec wc_site wp plugin install woocommerce --activate --allow-root --path=/var/www/html
                            fi
                            if [ $? -ne 0 ]; then
                                echo "ERROR: WooCommerce 安装失败"; exit 1
                            fi
                            docker exec wc_site wp rewrite flush --allow-root --path=/var/www/html
                            sleep 3
                            if docker exec wc_site wp plugin is-active woocommerce --allow-root --path=/var/www/html; then
                                echo "WooCommerce 激活确认 OK"
                            else
                                echo "ERROR: WooCommerce 未成功激活"; exit 1
                            fi
                        fi
                    '''

                    // ---- 最终校验 REST API ----
                    sh '''
                        echo "=== 校验 REST API ==="
                        resp=$(curl -s http://host.docker.internal:8080/wp-json/wc/v3/ 2>/dev/null | head -c 200)
                        if echo "$resp" | grep -q '"namespace":"wc/v3"'; then
                            echo "WC API v3 路由已生效，开始测试"
                        else
                            echo "ERROR: WC API 不可用"
                            echo "响应: $resp"
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

        // ============================================
        // Stage 4: 前端冒烟测试
        // ============================================
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
        success { echo '所有测试通过！' }
        failure { echo '测试未通过，请检查报告。' }
    }
}
