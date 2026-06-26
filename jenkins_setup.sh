#!/bin/sh
# ============================================================
# Jenkins 容器环境初始化脚本
# 用途：给 Jenkins 容器安装 Docker CLI（使其能操作宿主机 Docker）
# 运行：bash jenkins_setup.sh
# ============================================================

set -e

echo ">>> 在 Jenkins 容器中安装 wget..."
docker exec -u root jenkins apt-get update -qq
docker exec -u root jenkins apt-get install -y -qq wget ca-certificates

echo ""
echo ">>> 下载 Docker CLI 静态二进制..."
docker exec -u root jenkins sh -c '
  wget -q -O /tmp/docker.tgz https://download.docker.com/linux/static/stable/x86_64/docker-28.0.4.tgz && \
  tar -xzf /tmp/docker.tgz -C /usr/local/bin --strip-components=1 && \
  chmod +x /usr/local/bin/docker && \
  rm /tmp/docker.tgz
'

echo ""
echo ">>> 验证安装..."
docker exec -u root jenkins docker --version

echo ""
echo "✅ Jenkins 容器已具备 Docker CLI"
echo "   下一步：在 Jenkins Web UI 中配置凭据和 Pipeline 任务"
