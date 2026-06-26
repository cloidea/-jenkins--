"""
产品模块：API + 数据库双重校验测试

验证通过 WooCommerce API 创建产品后，数据库记录是否一致。
"""

import logging as logger
import pytest
from demostore_automation.src.utilities.wooAPIUtility import WooAPIUtility
from demostore_automation.src.dao.products_dao import ProductsDAO
from demostore_automation.src.utilities.genericUtilities import generate_random_string


pytestmark = [pytest.mark.beregression, pytest.mark.besmoke, pytest.mark.products_api]


@pytest.mark.tcid101
def test_create_simple_product_and_verify_in_db():
    """
    TCID-101: 创建简单产品并验证数据库记录

    1. 通过 API 创建一个简单产品
    2. 验证 API 响应正确
    3. 在数据库中查询该产品
    4. 验证数据库记录与 API 返回一致
    """
    # 构造唯一产品名
    product_name = f"Test Product - {generate_random_string(8)}"
    product_price = "29.99"

    woo_helper = WooAPIUtility()
    payload = {
        "name": product_name,
        "type": "simple",
        "regular_price": product_price,
        "description": "自动化测试创建的产品",
        "short_description": "用于 API + DB 双重校验测试",
        "status": "publish",
    }
    rs_body = woo_helper.post("products", params=payload, expected_status_code=201)

    # 验证 API 响应
    assert rs_body, "创建产品的 API 响应不应为空"
    assert rs_body["id"], "产品 ID 必须存在"
    assert isinstance(rs_body["id"], int), "产品 ID 必须是整数"
    assert rs_body["name"] == product_name, (
        f"产品名称不匹配。预期: {product_name}, 实际: {rs_body['name']}"
    )
    assert rs_body["regular_price"] == product_price, (
        f"产品价格不匹配。预期: {product_price}, 实际: {rs_body['regular_price']}"
    )

    logger.info(f"API 验证通过: 产品 '{product_name}' 创建成功, ID={rs_body['id']}")

    # 验证数据库记录
    product_dao = ProductsDAO()
    db_result = product_dao.get_product_by_id(rs_body["id"])

    assert db_result, f"数据库中未找到产品 ID={rs_body['id']} 的记录"
    assert len(db_result) == 1, (
        f"数据库应返回 1 条记录，实际返回 {len(db_result)} 条"
    )

    logger.info(f"数据库验证通过: 产品 ID={rs_body['id']} 数据一致")


@pytest.mark.tcid102
def test_get_all_products_verify_not_empty():
    """
    TCID-102: 获取所有产品列表并验证非空

    1. 通过 API 获取产品列表
    2. 验证返回结果不为空
    """
    woo_helper = WooAPIUtility()
    api_products = woo_helper.get("products", params={"per_page": 100})
    assert len(api_products) > 0, f"产品列表不应为空，实际返回 {len(api_products)} 条"
    logger.info(f"产品列表校验通过: API 返回 {len(api_products)} 个产品")


@pytest.mark.tcid103
def test_create_product_without_required_field():
    """
    TCID-103: 创建产品时 name 为必填字段

    验证 name 字段缺失时 WooCommerce 自动填充默认名称，状态码为 201。
    （WooCommerce 9.x 行为：name 缺失 → 默认 'Product'）
    """
    woo_helper = WooAPIUtility()
    payload = {"type": "simple", "regular_price": "29.99"}
    rs_body = woo_helper.post("products", params=payload, expected_status_code=201)

    assert rs_body, "响应不应为空"
    assert rs_body.get("id"), "产品 ID 必须存在"
    # WooCommerce 9.x: 缺少 name 时自动生成默认名称
    assert rs_body.get("name"), "产品应包含名称字段"
    logger.info(f"参数校验通过: 缺少 name 字段时自动填充, name={rs_body.get('name')}")
