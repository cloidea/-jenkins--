pipeline {
    agent any

    // =============================================
    // 环境变量 — 请在 Jenkins 中配置对应的 Credentials
    // Dashboard → Manage Jenkins → Credentials → System → Global
    // 添加 Secret text 类型，ID 与下方 credentials() 中的名称一致
    // =============================================
    environment {
        BASE_URL      = 'http://host.docker.internal:8080'
        BROWSER       = 'headlesschrome'
        DB_HOST       = 'host.docker.internal'
        DB_PORT       = '3307'
        DB_DATABASE   = 'wordpress'
        DB_TABLE_PREFIX = 'wp_'
        DB_USER       = 'root'
        DB_PASSWORD   = 'root_password'
        // 敏感信息从 Jenkins Credentials 注入
        WOO_KEY       = credentials('WOO_KEY')
        WOO_SECRET    = credentials('WOO_SECRET')
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
                    // 启动 docker-compose（服务发布到宿主机端口）
                    sh 'docker compose up -d'

                    // 等待 WordPress 就绪
                    sh '''
                        echo "⏳ 等待 WordPress 启动..."
                        for i in $(seq 1 36); do
                            STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://host.docker.internal:8080 2>/dev/null || echo "000")
                            if [ "$STATUS" = "200" ] || [ "$STATUS" = "302" ]; then
                                echo "✅ WordPress 已就绪 (HTTP $STATUS)"
                                break
                            fi
                            echo "   等待中... ($i/36, 当前状态: $STATUS)"
                            sleep 5
                        done
                    '''
                }
            }
        }

        // ===========================================
        // Stage 3: 执行测试（在 python:3.11 容器中）
        // ===========================================
        stage('Run Tests') {
            agent {
                docker {
                    image 'python:3.11'
                    reuseNode true     // 复用同一节点的工作空间
                    args '''
                        --network jenkins-net
                        -e BASE_URL=http://host.docker.internal:8080
                        -e BROWSER=headlesschrome
                        -e DB_HOST=host.docker.internal
                        -e DB_PORT=3307
                        -e DB_DATABASE=wordpress
                        -e DB_TABLE_PREFIX=wp_
                        -e DB_USER=root
                        -e DB_PASSWORD=root_password
                    '''
                }
            }
            stages {

                // 安装 Python 依赖
                stage('Install Dependencies') {
                    steps {
                        sh 'pip install -r requirements.txt'
                    }
                }

                // 健康检查（快速失败）
                stage('Health Check') {
                    steps {
                        sh '''
                            cd demostore_automation
                            python -m pytest tests/test_healthcheck.py -v
                        '''
                    }
                }

                // 后端 API 测试
                stage('Backend Tests') {
                    steps {
                        sh '''
                            cd demostore_automation
                            python -m pytest tests/backend/ -v \
                                --tb=short \
                                --html=reports/report_backend.html \
                                --self-contained-html
                        '''
                    }
                }

                // 前端冒烟测试
                stage('Frontend Smoke Tests') {
                    steps {
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
        }
    }

    // =============================================
    // Post: 无论成功或失败都执行
    // =============================================
    post {
        always {
            // 清理测试基础设施
            sh 'docker compose down || true'
        }
        success {
            echo '🎉 所有测试通过！'
        }
        failure {
            echo '⚠️  测试未通过，请检查报告。'
        }
        // 归档报告和截图
        always {
            archiveArtifacts artifacts: 'demostore_automation/reports/**', allowEmptyArchive: true
        }
    }
}
