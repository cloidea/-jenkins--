"""
全局 Pytest Fixtures 配置文件

提供浏览器驱动管理、失败自动截图、测试报告增强等功能。
"""

import pytest
import os
import logging as logger
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChOptions
from selenium.webdriver.firefox.options import Options as FFOptions

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent


def pytest_configure(config):
    """pytest 启动时的全局配置"""
    config.option.htmlpath = str(PROJECT_ROOT / "demostore_automation/reports/report.html")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """为失败用例自动截图并嵌入 HTML 报告"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)

    if rep.when == "call" and rep.failed:
        driver = getattr(item.instance, "driver", None) if hasattr(item, "instance") else None
        if driver:
            try:
                screenshot_dir = PROJECT_ROOT / "demostore_automation/reports/screenshots"
                screenshot_dir.mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{item.name}_{timestamp}.png"
                filepath = screenshot_dir / filename
                driver.save_screenshot(str(filepath))
                logger.info(f"失败截图已保存: {filepath}")
            except Exception as e:
                logger.error(f"截图失败: {e}")


@pytest.fixture(scope="class")
def init_driver(request):
    """
    浏览器驱动 Fixture（class 级别）

    支持浏览器类型：
    - chrome / ch：本地 Chrome
    - headlesschrome：无头 Chrome（CI 环境推荐）
    - firefox / ff：本地 Firefox
    - headlessfirefox：无头 Firefox
    - remote_chrome / remote_firefox：Selenium Grid 远程执行

    环境变量：
    - BROWSER：浏览器类型（必填）
    - REMOTE_WEBDRIVER：远程 WebDriver URL（remote 模式必填）
    """
    supported_browsers = [
        "chrome", "ch", "headlesschrome",
        "remote_chrome", "firefox", "ff",
        "headlessfirefox", "remote_firefox",
    ]

    browser = os.environ.get("BROWSER")
    if not browser:
        raise Exception("环境变量 'BROWSER' 必须设置。示例: BROWSER=headlesschrome")

    browser = browser.lower()
    if browser not in supported_browsers:
        raise Exception(
            f"不支持的浏览器类型 '{browser}'。可选值: {supported_browsers}"
        )

    # --- Chrome 系列 ---
    if browser in ("chrome", "ch"):
        driver = webdriver.Chrome()

    elif browser == "headlesschrome":
        logger.info("启动 Headless Chrome（无头模式）")
        chrome_options = ChOptions()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(options=chrome_options)

    elif browser == "remote_chrome":
        chrome_remote_url = os.environ.get("REMOTE_WEBDRIVER")
        if not chrome_remote_url:
            raise Exception("remote_chrome 模式需要设置 'REMOTE_WEBDRIVER' 环境变量")
        logger.info(f"连接远程 Chrome: {chrome_remote_url}")
        chrome_options = ChOptions()
        chrome_options.add_argument("--ignore-ssl-errors=yes")
        chrome_options.add_argument("--ignore-certificate-errors")
        driver = webdriver.Remote(command_executor=chrome_remote_url, options=chrome_options)

    # --- Firefox 系列 ---
    elif browser in ("firefox", "ff"):
        driver = webdriver.Firefox()

    elif browser == "headlessfirefox":
        ff_options = FFOptions()
        ff_options.add_argument("--headless")
        ff_options.add_argument("--disable-gpu")
        ff_options.add_argument("--no-sandbox")
        ff_options.add_argument("--window-size=1920,1080")
        driver = webdriver.Firefox(options=ff_options)

    elif browser == "remote_firefox":
        remote_url = os.environ.get("REMOTE_WEBDRIVER")
        if not remote_url:
            raise Exception("remote_firefox 模式需要设置 'REMOTE_WEBDRIVER' 环境变量")
        capabilities = {
            "browserName": "firefox",
            "marionette": True,
            "acceptInsecureCerts": True,
        }
        driver = webdriver.Remote(command_executor=remote_url, desired_capabilities=capabilities)

    # 输出浏览器信息（调试用）
    logger.debug("=" * 50)
    logger.debug("浏览器信息:")
    for k, v in driver.capabilities.items():
        logger.debug(f"  {k}: {v}")
    logger.debug("=" * 50)

    request.cls.driver = driver
    yield
    driver.quit()
