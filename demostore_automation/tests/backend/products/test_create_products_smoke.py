


import pytest
import logging as logger

from demostore_automation.src.utilities.genericUtilities import generate_random_string
from demostore_automation.src.api_helpers.ProductsAPIHelper import ProductsAPIHelper
from demostore_automation.src.dao.products_dao import ProductsDAO

@pytest.mark.smoke
@pytest.mark.des32
def test_create_1_simple_product():
    logger.info("Running test: test_create_1_simple_product")



    #build the payload for create product
    product_name = generate_random_string(length=20)
    logger.debug(f"Calling create api with product_name: {product_name}")
    product_type = 'simple'
    regular_price = '21.99'
    payload = {
    "name": product_name,
    "type": product_type,
    "regular_price": regular_price,

}

    #make the call to create product
    product_api_helper = ProductsAPIHelper()
    create_response = product_api_helper.call_create_product(payload=payload)

    #verify the response has correct data
    #verify the id in response is not empty
    assert create_response['id'], "Create product response, ID field is empty."

    assert create_response['type'] == product_type, f"Create product api, the 'type' in response is not as expected" \
                f"Expected: {product_type}, Actual: {create_response['type']}"
    
    assert create_response['name'] == product_name, f"Create product api, the 'name' in response is not as expected" \
                f"Expected: {product_name}, Actual: {create_response['name']}"
    
    assert create_response['status'] == 'publish', f"Create product api, the 'status' in response is not as expected. " \
                f"Expected: 'publish', Actual: {create_response['status']}"

    #verify the in database that the product is created 
    product_id = create_response['id']
    db_product = ProductsDAO().get_product_by_id(product_id)

    assert db_product, f"After creating product via api, the product not found in database. product_id = {product_id}"
    assert db_product[0]['post_name'] == product_name, f"After creating product via api, the product name in db does not match in API. Expected name: {product_name}, DB name: {db_product[0]['post_name']}. product_id = {product_id}"













