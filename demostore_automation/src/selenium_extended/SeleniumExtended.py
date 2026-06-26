
import time

from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select

class SeleniumExtended:

    def __init__(self, driver):
        """
        Initializes the class with a WebDriver instance and sets the default timeout.

        This constructor initializes the WebDriver used for browser automation and
        sets a default timeout value that can be used across various actions in the class.

        Args:
            driver (WebDriver): The WebDriver instance to interact with the browser.

        Returns:
            None: This method does not return any value. It only initializes the object.

        Example:
            driver = webdriver.Chrome()  # or any other WebDriver instance
            my_class_instance = MyClass(driver)
            # This creates an instance of MyClass with the WebDriver 'driver' and a default timeout of 5 seconds.
        """
        self.driver = driver
        self.default_timeout = 5

        
    def go_to(self, url):
        """
        Navigate the browser to the specified URL.

        This method uses the web driver to open the given URL in the browser.

        Args:
            url (str): The URL to navigate to. This should be a valid URL (e.g., 'https://example.com').

        Returns:
            None: The method does not return any value; it simply performs the navigation action.

        Example:
            go_to('https://example.com')
            # This will navigate the browser to the 'https://example.com' webpage.
        """
        self.driver.get(url)
        
        
    def wait_and_input_text(self, locator, text, timeout=None):
        """
        Waits for an element to be visible and then inputs the specified text.

        This method waits for the element, identified by the given locator, to become
        visible within the specified timeout period. Once the element is visible, it
        inputs the provided text into the element.

        Args:
            locator (str or tuple): The locator for the element to interact with (e.g., ID, XPath, CSS selector).
            text (str): The text to be input into the located element.
            timeout (int, optional): The maximum time (in seconds) to wait for the element to become visible. 
                                    If not provided, the default timeout value will be used.

        Returns:
            None: The method does not return any value; it performs the action of waiting and inputting the text.

        Example:
            wait_and_input_text('input#search', 'OpenAI', timeout=10)
            # This will wait up to 10 seconds for the element with the locator 'input#search' to appear and then input 'OpenAI'.
        """
        timeout = timeout if timeout else self.default_timeout
       
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        ).send_keys(text)



    def wait_and_click(self, locator, timeout=None):
        """
        Waits for an element to become clickable and then clicks on it.

        This method waits for the element, identified by the given locator, to become
        clickable within the specified timeout period. If the element is stale (i.e., no longer attached to the DOM),
        it will wait for it to become visible and then attempt to click again.

        Args:
            locator (str or tuple): The locator used to find the element to click (e.g., ID, XPath, CSS selector).
            timeout (int, optional): The maximum time (in seconds) to wait for the element to become clickable. 
                                    If not provided, the default timeout value will be used.

        Returns:
            None: The method does not return any value; it performs the action of waiting for the element and clicking it.

        Raises:
            TimeoutException: If the element is not clickable within the provided timeout period.

        Example:
            wait_and_click('button#submit', timeout=10)
            # This will wait up to 10 seconds for the 'button#submit' element to become clickable and click it.
        """

        timeout = timeout if timeout else self.default_timeout
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator),
                message=f'Element with locator {locator} not found after {timeout} seconds.'
            ).click()
        except StaleElementReferenceException:
            time.sleep(2)
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator),
                message=f"Element with locator {locator}, is not clickable."
            ).click()


    def wait_until_element_contains_text(self, locator, text, timeout=None):
        """
        Waits for an element to contain the specified text within a given timeout.

        This method waits until the element, identified by the provided locator, contains
        the specified text. If the element doesn't contain the text within the specified
        timeout, a TimeoutException is raised. If no timeout is provided, the default timeout is used.

        Args:
            locator (str or tuple): The locator used to find the element (e.g., ID, XPath, CSS selector).
            text (str): The text that the element should contain.
            timeout (int, optional): The maximum time (in seconds) to wait for the element to contain the text. 
                                    If not provided, the default timeout value will be used.

        Returns:
            None: The method does not return any value; it only waits for the element to contain the specified text.

        Raises:
            TimeoutException: If the element does not contain the text within the given timeout period.
        """
        timeout = timeout if timeout else self.default_timeout

        WebDriverWait(self.driver, timeout).until(
            EC.text_to_be_present_in_element(locator, text),
            message=f'Element with locator = {locator}, does not contain text: "{text}", after waiting {timeout} seconds.'
        )
      
    def wait_until_element_is_visible(self, locator_or_element, timeout=None):
        """
        Waits until the specified element is visible within a given timeout.

        This method waits for the element, identified by the provided locator or element object,
        to become visible on the page within the specified timeout period. If the element does not 
        become visible within the timeout, a TimeoutException is raised. If no timeout is provided, 
        the default timeout value is used.

        Args:
            locator_or_element (str, tuple, or WebElement): The locator (such as ID, XPath, or CSS selector) 
                                                            or a WebElement object to find the element.
            timeout (int, optional): The maximum time (in seconds) to wait for the element to become visible.
                                    If not provided, the default timeout value will be used.

        Returns:
            None: The method does not return any value; it waits for the element to become visible.

        Raises:
            TimeoutException: If the element is not visible within the specified timeout period.

        Example:
            wait_until_element_is_visible('div#alert', timeout=10)
            # This will wait up to 10 seconds for the element with the locator 'div#alert' to become visible.
        """
        timeout = timeout if timeout else self.default_timeout

        if isinstance(locator_or_element, tuple):
            elem = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator_or_element),
                message=f"Element with locator {locator_or_element} not found after timeout of {timeout}"
            )
        else:
            import selenium.webdriver.remote.webelement
            if isinstance(locator_or_element, selenium.webdriver.remote.webelement.WebElement):
                elem = WebDriverWait(self.driver, timeout).until(
                    EC.visibility_of(locator_or_element),
                    message=f"Element {locator_or_element} not found after timeout of {timeout}"
                )
            else:
                raise TypeError(f"The locator to check visibility must be a 'tuple' or a 'WebElement'. It was {type(locator_or_element)}")

        return elem

    def wait_and_get_elements(self, locator, timeout=None, err=None):
        """
        Waits for the elements to be visible and returns them once they are located.

        This method waits for the elements, identified by the given locator, to be present and visible 
        within the specified timeout period. If the elements are not found or visible within the timeout, 
        a TimeoutException will be raised. If no timeout is provided, the default timeout is used. 
        Additionally, a custom error message can be passed via the `err` parameter.

        Args:
            locator (str or tuple): The locator used to find the elements (e.g., ID, XPath, CSS selector).
            timeout (int, optional): The maximum time (in seconds) to wait for the elements to be visible. 
                                    If not provided, the default timeout value will be used.
            err (str, optional): A custom error message to be used if the element is not found or visible 
                                within the timeout period. If not provided, a default error message is used.

        Returns:
            list: A list of WebElements matching the given locator.

        Raises:
            TimeoutException: If the elements are not visible within the specified timeout period.
        """
        timeout = timeout if timeout else self.default_timeout
        err = err if err else f"Unable to find elements located by '{locator}'," \
                                f"after timeout of {timeout}"
    
        try:
            elements = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_all_elements_located(locator),
                )
        except TimeoutException:
                raise TimeoutException(err)

        return elements



    def wait_and_select_dropdown(self, locator, to_select, select_by='visible_text'):
        """

        :param locator:
        :param to_select:
        :param select_by: Options are 'visible_text', 'index', or value 'value'
        :return:
        
        Waits for a dropdown element to become visible and selects an option from it.

        This method waits for the dropdown element, identified by the given locator, to become visible 
        within the specified timeout period. Once the element is visible, it selects an option from the 
        dropdown based on the provided selection strategy (`select_by`). By default, the method selects 
        the option by its visible text. Other strategies such as `value` or `index` can also be used.

        Args:
            locator (str or tuple): The locator used to find the dropdown element (e.g., ID, XPath, CSS selector).
            to_select (str): The option to select from the dropdown. This can be either the visible text,
                            the value attribute, or the index of the option depending on the `select_by` parameter.
            select_by (str, optional): The strategy to locate the dropdown option. 
                                        Options are:
                                        - 'visible_text' (default): Selects the option by its visible text.
                                        - 'value': Selects the option by its value attribute.
                                        - 'index': Selects the option by its index (0-based).
        
        Returns:
            None: The method does not return any value; it performs the action of selecting an option.

        Raises:
            TimeoutException: If the dropdown element is not visible within the specified timeout period.
            NoSuchElementException: If the option to be selected is not found in the dropdown.

        Example:
            wait_and_select_dropdown('select#category', 'Electronics', select_by='visible_text')
            # This will wait for the 'select#category' dropdown to be visible and select the 'Electronics' option by visible text.
        """
        select_element = self.wait_until_element_is_visible(locator)
        select = Select(select_element)
        if select_by.lower() == 'visible_text':
            select.select_by_visible_text(to_select)
        elif select_by.lower() == 'index':
            select.select_by_index(to_select)
        elif select_by.lower() == 'value':
            select.select_by_value(to_select)
        else:
            raise Exception(f"Invalid option for 'to_select' parameter. Valid values are 'visible_text', 'index', or value 'value'.")

   
   
    def wait_and_get_text(self, locator, timeout=None):
        """
        Waits for the element to become visible and returns its text content.

        This method waits for the element, identified by the given locator, to be visible within the specified
        timeout period. Once the element becomes visible, it retrieves and returns the text content of the element.
        If the element does not become visible within the timeout, a TimeoutException is raised. If no timeout is 
        provided, the default timeout value is used.

        Args:
            locator (str or tuple): The locator used to find the element (e.g., ID, XPath, CSS selector).
            timeout (int, optional): The maximum time (in seconds) to wait for the element to become visible. 
                                    If not provided, the default timeout value will be used.

        Returns:
            str: The text content of the element once it is visible.

        Raises:
            TimeoutException: If the element is not visible within the given timeout period.

        Example:
            wait_and_get_text('div#message', timeout=10)
            # This will wait up to 10 seconds for the 'div#message' element to become visible and then return its text.
        """
        timeout = timeout if timeout else self.default_timeout
        elm = self.wait_until_element_is_visible(locator, timeout)
        element_text = elm.text               
       
        return element_text

