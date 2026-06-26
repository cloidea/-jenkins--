import logging as logger

from demostore_automation.src.selenium_extended.SeleniumExtended import SeleniumExtended #importing the folder.thefile
from demostore_automation.src.configs.MainConfigs import MainConfigs #getting the base URL
from demostore_automation.src.pages.locators.ProductPageLocators import ProductPageLocators


class ProductPage(ProductPageLocators):

    def __init__(self, driver):
        self.driver = driver
        self.sl = SeleniumExtended(driver) #self makes it available on every function within the class


    def go_to_product_page(self, product_slug):
        """
    Navigates to the product page based on the provided product slug.

    Args:
        product_slug (str): The unique identifier (slug) for the product. 
                             This is typically part of the URL to navigate to the specific product page.

    Returns:
        None: This function does not return any value; it performs the navigation action.
    
    Example:
        go_to_product_page('my-awesome-product')
        # This will navigate the browser to the product page for 'my-awesome-product'.
    """

        base_url = MainConfigs.get_base_url()
        product_url = f"{base_url}/{product_slug}" #is the same as product_url = base_url + "/" + product_slug
        self.sl.go_to(product_url)

    def get_displayed_product_name(self):
       return self.sl.wait_and_get_text(self.PRODUCT_TITLE)
    """
    Retrieves the name of the product displayed on the current page.

    This method extracts the name of the product from the currently displayed product page
    and returns it as a string. It assumes that the product name is available in a specific 
    element, typically identified by a predefined locator or structure on the page.

    Returns:
        str: The name of the product currently displayed on the page.

    Example:
        product_name = get_displayed_product_name()
        # This will retrieve and return the name of the product displayed on the page.
    """

    def get_url_of_displayed_main_image(self):
       

       image_element = self.sl.wait_until_element_is_visible(self.PRODUCT_IMAGE_MAIN)
       image_url = image_element.get_attribute('src')
       return image_url


    def get_url_of_displayed_alternate_images(self):
        image_elements = self.sl.wait_and_get_elements(self.PRODUCT_ALTERNATE_IMAGES, err="Unable to find alternate images for a product.")
        all_urls = [element.get_attribute('src') for element in image_elements]
        logger.debug(f"All alternate image urls: {all_urls}")
        return all_urls

    def get_product_type_text(self):
        """Retrieves the product type text displayed on the product page."""
        return self.sl.wait_and_get_text(self.PRODUCT_TYPE_TEXT)

    def get_displayed_product_price(self):
        """Retrieves the displayed product price HTML."""
        return self.sl.wait_and_get_text(self.PRODUCT_PRICE)





