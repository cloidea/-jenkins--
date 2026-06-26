
from selenium.webdriver.common.by import By

class ProductPageLocators:

    PRODUCT_TITLE = (By.CSS_SELECTOR, 'h1.product_title.entry-title')
    PRODUCT_IMAGE_MAIN = (By.CSS_SELECTOR, 'div.woocommerce-product-gallery__image.flex-active-slide img.wp-post-image')
    PRODUCT_ALTERNATE_IMAGES = (By.CSS_SELECTOR, 'ol.flex-control-nav.flex-control-thumbs li img')
    PRODUCT_TYPE_TEXT = (By.CSS_SELECTOR, 'p.price')
    PRODUCT_PRICE = (By.CSS_SELECTOR, 'p.price')

