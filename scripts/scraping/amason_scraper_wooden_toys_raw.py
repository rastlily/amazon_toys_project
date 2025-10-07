from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import re
from datetime import datetime

# Selenium setup
chrome_driver_path = r"C:\Users\lsapa\OneDrive\Desktop\chromedriver-win64\chromedriver-win64\chromedriver.exe"
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

# Wooden toys store page URL
url = "https://www.amazon.de/stores/page/3A28CD28-6DD2-4410-8F3C-0F08322C380E?ingress=2&lp_context_asin=B07N1JP56L&visitId=1e29af81-06fc-420f-a509-c85bd9c3d5f1&ref_=ast_bln"

def extract_asin(url):
    if not url:
        return ""
    match = re.search(r"/dp/([A-Z0-9]{10})", url)
    if match:
        return match.group(1)
    return ""

def clean_title(title):
    if not title:
        return ""
    return title.strip()

def get_old_price(driver):
    try:
        # Try to find the old price by default selector
        old_price_element = driver.find_element(By.CSS_SELECTOR, "span.a-price.a-text-price")
        return old_price_element.text.strip()
    except NoSuchElementException:
        try:
            # Alternative selector for old price
            old_price_element = driver.find_element(By.CSS_SELECTOR, "span.a-price.aok-align-center.reinventPricePriceToPayMargin.priceToPay")
            return old_price_element.text.strip()
        except NoSuchElementException:
            return ""

def scrape_wooden_toys():
    try:
        service = Service(chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        time.sleep(15)

        products = []
        current_date = datetime.now().strftime("%Y-%m-%d")  
        filename = f'wooden_toys_raw_{current_date}.csv'

        items = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/dp/"]')
        print(f"Found {len(items)} product links.")

        for index, item in enumerate(items[4:], start=1):
            try:
                product_link = item.get_attribute('href')
                if not product_link:
                    print(f"Product {index}: link missing")
                    continue

                title = item.get_attribute('title') or item.get_attribute('aria-label') or item.text
                if not title or ("Wooden" not in title and "Holz" not in title):
                    print(f"Product {index}: does not match criteria")
                    continue

                print(f"Processing product {index}: {title[:50]}...")

                driver.execute_script(f"window.open('{product_link}', '_blank');")
                driver.switch_to.window(driver.window_handles[1])
                time.sleep(5)

                # Extract ASIN
                asin = extract_asin(product_link)

                # Extract product title
                try:
                    title = clean_title(driver.find_element(By.ID, "productTitle").text.strip())
                except NoSuchElementException:
                    title = ""

                # Extract price
                try:
                    price_currency = driver.find_element(By.CSS_SELECTOR, "span.a-price-symbol").text.strip()
                    price_whole = driver.find_element(By.CSS_SELECTOR, "span.a-price-whole").text.strip()
                    price_fraction = driver.find_element(By.CSS_SELECTOR, "span.a-price-fraction").text.strip()
                    price = f"{price_currency}{price_whole}.{price_fraction}"
                except NoSuchElementException:
                    price = ""

                # Extract old price
                old_price = get_old_price(driver)

                # Extract discount
                try:
                    discount = driver.find_element(By.CSS_SELECTOR, "span.savingsPercentage").text.strip()
                except NoSuchElementException:
                    discount = ""

                # Extract stock status
                try:
                    stock = driver.find_element(By.CSS_SELECTOR, "div#availability").text.strip()
                except NoSuchElementException:
                    stock = ""

                # Extract number of reviews
                try:
                    reviews_count = driver.find_element(By.CSS_SELECTOR, "span[data-hook='total-review-count']").text.strip()
                except NoSuchElementException:
                    reviews_count = ""

                # Extract age range
                try:
                    age_range = driver.find_element(By.XPATH, '//td[contains(@class, "prodDetAttrValue") and (contains(text(), "Monate") or contains(text(), "Jahre") or contains(text(), "months") or contains(text(), "years"))]').text.strip()
                except NoSuchElementException:
                    age_range = ""

                # Extract weight
                try:
                    weight = driver.find_element(By.XPATH, '//td[contains(@class, "prodDetAttrValue") and (contains(text(), "g") or contains(text(), "kg"))]').text.strip()
                except NoSuchElementException:
                    weight = ""

                # Extract short description
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
                print(f"Error processing product {index}: {e}")
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                continue

        if products:
            df = pd.DataFrame(products)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"Data successfully saved to {filename}")
        else:
            print("No products were scraped.")

        driver.quit()
        return True

    except WebDriverException as e:
        print(f"WebDriver error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("Starting scrape of wooden toys...")
    success = scrape_wooden_toys()
    if success:
        print("Done!")
    else:
        print("An error occurred. Try again later.")





