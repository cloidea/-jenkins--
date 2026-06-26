"""优惠券 API 测试模块 — 已修复语法问题。"""

import pytest
import logging as logger

from demostore_automation.src.utilities.genericUtilities import generate_random_coupon_code
from demostore_automation.src.api_helpers.CouponAPIHelper import CouponAPIHelper


pytestmark = [pytest.mark.coupon_api]


@pytest.fixture(scope="module")
def my_setup():
    coupon_api_helper = CouponAPIHelper()
    info = {"coupon_api_helper": coupon_api_helper}
    return info


@pytest.mark.des30
def test_create_coupon_invalid_discount_type(my_setup):
    logger.info("Running test: test_create_coupon_invalid_discount_type")

    coupon_api_helper = my_setup["coupon_api_helper"]

    coupon_code = generate_random_coupon_code()
    amount = "50.00"
    discount_type = "free_cart"
    payload = {
        "code": coupon_code,
        "discount_type": discount_type,
        "amount": amount,
    }

    logger.debug(f"Creating coupon with payload: {payload}")

    response = coupon_api_helper.call_create_coupon(payload, expected_status_code=400)

    # Verify the error response contains expected fields
    assert response["code"] == "rest_invalid_param", (
        f"Expected error code 'rest_invalid_param', got: {response.get('code')}"
    )
    assert "Invalid parameter(s): discount_type" in response["message"], (
        f"Expected message about invalid discount_type, got: {response.get('message')}"
    )
    assert response["data"]["status"] == 400, (
        f"Expected status 400, got: {response['data'].get('status')}"
    )
    assert "discount_type is not one of" in response["data"]["params"]["discount_type"], (
        f"Unexpected params error: {response['data']['params'].get('discount_type')}"
    )


@pytest.mark.parametrize(
    "discount_type",
    [
        pytest.param("percent", marks=[pytest.mark.des27]),
        pytest.param("fixed_cart", marks=[pytest.mark.des28]),
        pytest.param("fixed_product", marks=[pytest.mark.des29]),
        pytest.param(None, marks=[pytest.mark.des31]),
    ],
)
def test_create_coupon_discount_type(my_setup, discount_type):
    logger.info(f"Running test: test_create_coupon_discount_type {discount_type}")
    coupon_api_helper = my_setup["coupon_api_helper"]

    coupon_code = generate_random_coupon_code()
    amount = "100.00"

    payload = {"code": coupon_code, "amount": amount}
    if discount_type:
        payload["discount_type"] = discount_type

    logger.debug(f"Creating coupon with payload: {payload}")

    response = coupon_api_helper.call_create_coupon(payload)

    # verify the id is not null
    assert response["id"], "After making create coupon api call, response does not have valid ID."

    # verify the coupon code matches
    assert response["code"] == coupon_code.lower(), (
        f"Create coupon api call mismatched 'code'. "
        f"Request: {coupon_code.lower()}, Response: {response['code']}"
    )

    # verify the amount
    assert response["amount"] == amount, (
        f"Create coupon api, amount does not match. "
        f"Expected: {amount}, Actual: {response['amount']}"
    )

    # verify discount type
    actual_discount = response.get("discount_type", "")
    expected_discount = discount_type if discount_type else "fixed_cart"  # WooCommerce 9.x defaults to fixed_cart
    assert actual_discount == expected_discount, (
        f"Create coupon api, discount_type does not match. "
        f"Expected: {expected_discount}, Actual: {actual_discount}"
    )

    # verify data persistence via GET call
    coupon_id = response["id"]
    get_response = coupon_api_helper.call_retrieve_coupon(coupon_id)

    get_discount = get_response.get("discount_type", "")
    assert get_discount == expected_discount, (
        f"GET coupon api, discount_type does not match. "
        f"Expected: {discount_type}, Actual: {get_discount}"
    )
