@echo off
REM ============================================
REM  E-Commerce Test Framework - Windows Runner
REM  用法: runner.bat [frontend|backend|all]
REM  前置: 设置环境变量或修改下方占位符为实际值
REM ============================================

REM --- 环境变量（修改为你的测试环境实际值）---
set BASE_URL=<your_woocommerce_url>
set BROWSER=headlesschrome
set DB_HOST=<your_db_host>
set DB_PORT=<your_db_port>
set DB_DATABASE=<your_db_name>
set DB_TABLE_PREFIX=wp_
set DB_USER=<your_db_user>
set DB_PASSWORD=<your_db_password>
set WOO_KEY=<your_consumer_key>
set WOO_SECRET=<your_consumer_secret>

REM --- 进入测试目录 ---
cd /d %~dp0demostore_automation

REM --- 创建报告目录 ---
if not exist reports mkdir reports

REM --- 根据参数选择执行范围 ---
if "%1"=="frontend" (
    echo Running Frontend Tests...
    python -m pytest tests/frontend/ -v -m fesmoke --html=reports/report.html --self-contained-html
) else if "%1"=="backend" (
    echo Running Backend Tests...
    python -m pytest tests/backend/ -v --html=reports/report.html --self-contained-html
) else (
    echo Running All Tests...
    python -m pytest tests/ -v --html=reports/report.html --self-contained-html
)

echo.
echo Test execution completed.
