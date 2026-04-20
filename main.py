import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from Product import Product
from csv_generator import generate_csv

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
})

url_links = {
    "LT": "https://www.glossier.com/en-lt/collections/all",
    "US": "https://www.glossier.com/collections/all",
    }


def get_description(product_url):
    product_page = session.get(product_url).text
    product_soup = BeautifulSoup(product_page, 'html.parser')
    try:
        product_description = product_soup.find("p", class_="pv-details__info-item", id="description-item").text
    except Exception as e:
        print("GET DESCRIPTION ERROR:", e)
        product_description = ""
    print(product_description) # printing here since it's not included in the csv file, but to also make the wait more entertaining

    return product_description


def are_options(product_options):
    options = product_options.find("div", class_="config__group config__group--size js-option-group")
    if options is not None:
        return True
    else:
        return False


def scrape_with_options(product_with_options, all_products_list):
    pwo_url = product_with_options.article.find(itemprop="url").get("content")
    pwo_description = get_description(pwo_url)
    pwo_scraped_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    pwo_name = product_with_options.article.find(itemprop="name").get("content")
    pwo = product_with_options.find("div", class_="config__group config__group--size js-option-group")
    all_options = pwo.find_all("li")
    for option in all_options:
        option_id = option.get("data-variant-id")
        option_image = option.get("data-img-imgix")
        option_price = option.get("data-variant-price")
        option_url = "https://www.glossier.com" + option.get("data-url")
        (all_products_list
         .append(Product(pwo_name, option_id, option_url, option_image, option_price, pwo_scraped_at, pwo_description)))


def main():
    base_url = url_links["LT"]
    page_num = 1
    products_final = []

    while True:
        url = f"{base_url}?page={page_num}"
        print(f"Scraping page {page_num}: {url}")

        response = session.get(url, timeout=10)
        print("status:", response.status_code)

        if response.status_code == 429:
            print("Rate limited. Stopping.")
            break

        page = response.text
        soup = BeautifulSoup(page, 'html.parser')

        all_products = soup.find_all('li', class_='collection__item js-collection-item')

        if not all_products:
            print("No more products found. Stopping.")
            break

        for product in all_products:
            if are_options(product):
                scrape_with_options(product, products_final)
            else:
                product_id = product.article.get("data-product-id")
                name = product.article.find(itemprop="name").get("content")
                image = "https:" + product.article.find(itemprop="image").get("title")
                url = product.article.find(itemprop="url").get("content")
                description = get_description(url)
                price = product.find("span", class_="pi__price--current").contents[-1].strip()
                scraped_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                products_final.append(
                    Product(name, product_id, url, image, price, scraped_at, description)
                )

        page_num += 1
        time.sleep(3)

    generate_csv(products_final)


if __name__ == "__main__":
    main()
