import logging as logger 

from demostore_automation.src.selenium_extended.SeleniumExtended import SeleniumExtended
from demostore_automation.src.pages.locators.CartPageLocators import CartPageLocators
from demostore_automation.src.configs.MainConfigs import MainConfigs


class CartPage(CartPageLocators):

    endpoint = '/cart'

    def __init__(self, driver):
        self.driver = driver
        self.sl = SeleniumExtended(driver)

    def go_to_cart_page(self):
        base_url = MainConfigs.get_base_url()
        cart_url = base_url + self.endpoint
        self.driver.get(cart_url)

    def get_all_product_names_in_cart(self):  #gets a list of product names from the cart


        product_name_elements = self.sl.wait_and_get_elements(self.PRODUCT_NAMES_IN_CART)
        product_names = [i.text for i in product_name_elements]
        # product_names = []
        # for i in product_name_elements:
        #     product_names.append(i.text)
        return product_names

    def input_coupon(self, coupon_code):
        self.sl.wait_and_input_text(self.COUPON_FIELD, str(coupon_code))

    def click_apply_coupon(self):
        self.sl.wait_and_click(self.APPLY_COUPON_BTN)

    def click_add_coupon_field_hide_show(self):
        #clicks the button to show/hide the coupon input field
        self.sl.wait_and_click(self.ADD_COUPON_HIDE_SHOW)

    def get_displayed_message(self):
        """Retrieves the success message displayed after applying the coupon.

        Returns:
            str: the text of the success message.
        """
        txt = self.sl.wait_and_get_text(self.CART_PAGE_SUCCESS_MESSAGE)
        return txt


    def apply_coupon(self, coupon_code, expect_success=True):
        #applies a coupon code to the cart and verifies success message,
        #coupon_code (str): the coupon code to be applied - positional parameter
        #expect_success (bool, optional): Whether to expect a success message - defaults to true - keyword parameter
        #True = default value
    #raises: AssertionError: If expect_success is True and the success message doesn't match the expected format

        self.click_add_coupon_field_hide_show()
        self.input_coupon(coupon_code)
        self.click_apply_coupon()
        if expect_success:
            displayed_notice = self.get_displayed_message()
            logger.info(f'Displayed notice: {displayed_notice}')
            assert displayed_notice == f'Coupon code "{coupon_code}" has been applied to your cart.',\
                f"Applied coupon '{coupon_code}' but did not get successful messages."


    def click_on_proceed_to_checkout(self):
        self.sl.wait_and_click(self.PROCEED_TO_CHECKOUT_BTN)

    