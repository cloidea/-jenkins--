"""一键运行后端测试 — 环境变量内嵌，避免命令行泄露。"""
import os
import sys
import subprocess

# 本地 Docker 测试环境变量（仅本机有效）
os.environ["BASE_URL"] = "http://localhost:8080"
os.environ["WOO_KEY"] = "ck_f618a638c6fd7b21fcfd12bba04c9cd3"
os.environ["WOO_SECRET"] = "cs_5da2cc5bd3b8dabacb2abf3f13507c24"
os.environ["DB_HOST"] = "127.0.0.1"
os.environ["DB_PORT"] = "3307"
os.environ["DB_DATABASE"] = "wordpress"
os.environ["DB_TABLE_PREFIX"] = "wp_"
os.environ["DB_USER"] = "root"
os.environ["DB_PASSWORD"] = "root_password"
os.environ["BROWSER"] = "headlesschrome"
os.environ["PYTHONPATH"] = os.path.dirname(os.path.abspath(__file__))

# 运行 pytest
args = [
    sys.executable, "-m", "pytest",
    "demostore_automation/tests/backend/",
    "-v", "--tb=short",
]

print("=" * 50)
print("运行后端测试...")
print("=" * 50)

result = subprocess.run(args, cwd=os.path.dirname(os.path.abspath(__file__)))
sys.exit(result.returncode)
