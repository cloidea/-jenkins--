"""
Module for random unitilies. Helpful functions go here.
Example:
    generating random email

"""


import random
import string
import logging as logger
from html.parser import HTMLParser



def generate_random_email_and_password(domain='supersqa.com', email_prefix='testuser', elength=10):
    """
    Generates a random email and password combination.
    :param domain:
    :param email_prefix:
    :return: dictionary. A dictionary with keys 'email' & 'password'
    """

    random_string = ''.join(random.choices(string.ascii_lowercase, k=elength))
    # email = email_prefix + '_' + random_string + '@' + domain
    email = f'{email_prefix}_{random_string}@{domain}'

    password_length = 20
    password_string = ''.join(random.choices(string.ascii_letters, k=password_length))

    random_info = {'email': email, 'password': password_string}
    logger.debug(f"Randomly generated email and password: {random_info}")

    return random_info


def generate_random_coupon_code(suffix=None, length=10):
    code = ''.join(random.choices(string.ascii_lowercase, k=length))
    if suffix:
        code += suffix

    return code    


def generate_random_string(length=10, prefix=None, suffix=None):

    random_string = ''.join(random.choices(string.ascii_lowercase, k=length))

    if prefix:
        random_string = prefix + random_string
    if suffix:
        random_string = random_string + suffix    

    return random_string

def convert_html_to_text(html_string):
    """Convert HTML string to plain text by stripping all tags.

    Args:
        html_string (str): The HTML content to convert.

    Returns:
        str: Plain text extracted from the HTML.
    """
    class HTMLStripper(HTMLParser):
        def __init__(self):
            super().__init__()
            self.text = ""
        def handle_data(self, data):
            self.text += data
    stripper = HTMLStripper()
    stripper.feed(html_string)
    return stripper.text.strip()

if __name__ == '__main__':
    print(generate_random_email_and_password())
