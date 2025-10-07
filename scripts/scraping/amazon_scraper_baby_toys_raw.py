from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException
import pandas as pd
import time
import re
from datetime import datetime

# Selenium configuration
chrome_driver_path = r"C:\Users\lsapa\OneDrive\Desktop\chromedriver-win64\chromedriver-win64\chromedriver.exe"
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

# Baby toys store page URL
url = "https://www.amazon.de/stores/page/8448A972-580C-4CD3-8C64-2C7E3AE14D1F?ingress=2&lp_context_asin=B0CXTQWQWM&visitId=62b5c0bd-9304-4d7d-ad4b-4e2fef7d984b&ref_=ast_bln"

def extract_asin(url):
    if not url:
        return ""
    match = re.search(r"/dp/([A-Z0-9]{10})", url)
    if match:
        return match.group(1)
    return ""

def get_old_price(driver):
    try:
        old_price_element = driver.find_element(By.CSS_SELECTOR, "span.a-price.a-text-price")
        return old_price_element.text.strip()
    except NoSuchElementException:
        try:
            old_price_element = driver.find_element(By.CSS_SELECTOR, "span.a-price.aok-align-center.reinventPricePriceToPayMargin.priceToPay")
            return old_price_element.text.strip()
        except NoSuchElementException:
            return ""

def scrape_baby_toys():
    try:
        service = Service(chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        time.sleep(15)

        products = []
        current_date = datetime.now().strftime("%Y-%m-%d")
        filename = f'baby_toys_raw_{current_date}.csv'

        items = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/dp/"]')
        print(f"Found {len(items)} product links.")

        for index, item in enumerate(items[4:], start=1):
            try:
                product_link = item.get_attribute('href')
                if not product_link:
                    print(f"Product {index}: link missing")
                    continue

                title = item.get_attribute('title') or item.get_attribute('aria-label') or item.text
                if not title:
                    print(f"Product {index}: title missing")
                    continue

                print(f"Processing product {index}: {title[:50]}...")

                driver.execute_script(f"window.open('{product_link}', '_blank');")
                driver.switch_to.window(driver.window_handles[1])
                time.sleep(5)

                asin = extract_asin(product_link)

                # Product title
                try:
                    title = driver.find_element(By.ID, "productTitle").text.strip()
                except NoSuchElementException:
                    title = ""

                # Current price
                try:
                    price_currency = driver.find_element(By.CSS_SELECTOR, "span.a-price-symbol").text.strip()
                    price_whole = driver.find_element(By.CSS_SELECTOR, "span.a-price-whole").text.strip()
                    price_fraction = driver.find_element(By.CSS_SELECTOR, "span.a-price-fraction").text.strip()
                    price = f"{price_currency}{price_whole}.{price_fraction}"
                except NoSuchElementException:
                    price = ""

                # Old price
                old_price = get_old_price(driver)

                # Discount
                try:
                    discount = driver.find_element(By.CSS_SELECTOR, "span.savingsPercentage").text.strip()
                except NoSuchElementException:
                    discount = ""

                # Stock status
                try:
                    stock = driver.find_element(By.CSS_SELECTOR, "div#availability").text.strip()
                except NoSuchElementException:
                    stock = ""

                # Number of reviews
                try:
                    reviews_count = driver.find_element(By.CSS_SELECTOR, "span[data-hook='total-review-count']").text.strip()
                except NoSuchElementException:
                    reviews_count = ""

                # Age range
                try:
                    age_range = driver.find_element(By.XPATH, '//td[contains(@class, "prodDetAttrValue") and (contains(text(), "Monate") or contains(text(), "Jahre") or contains(text(), "months") or contains(text(), "years"))]').text.strip()
                except NoSuchElementException:
                    age_range = ""

                # Weight
                try:
                    weight = driver.find_element(By.XPATH, '//td[contains(@class, "prodDetAttrValue") and (contains(text(), "g") or contains(text(), "kg"))]').text.strip()
                except NoSuchElementException:
                    weight = ""

                # Short description
                try:
                    short_description_elements = driver.find_elements(By.CSS_SELECTOR, "ul.a-unordered-list.a-vertical.a-spacing-mini li.a-spacing-mini span.a-list-item")
                    short_description = "\n".join([item.text.strip() for item in short_description_elements])
                except NoSuchElementException:
                    short_description = ""

                products.append({
                    'asin': asin,
                    'url': product_link,
                    'title': title,
                    'price': price,
                    'old_price': old_price,
                    'discount': discount,
                    'stock': stock,
                    'reviews_count': reviews_count,
                    'age_range': age_range,
                    'weight': weight,
                    'short_description': short_description
                })

                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(2)

            except Exception as e:
                print(f"Error while processing product {index}: {e}")
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                continue

        if products:
            df = pd.DataFrame(products)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"Data successfully saved to {filename}")
        else:
            print("No product data could be collected.")

        driver.quit()
        return True

    except WebDriverException as e:
        print(f"WebDriver error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("Starting data collection for baby toys...")
    success = scrape_baby_toys()
    if success:
        print("Done!")
    else:
        print("An error occurred. Please try again later.")

