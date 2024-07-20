import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin

url = 'https://www.mouser.com/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def fetch_page(url):
    print(f"Fetching URL: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        return None

def extract_categories(page_content):
    soup = BeautifulSoup(page_content, 'html.parser')
    categories = []
    category_buttons = soup.find_all('button', class_='main-category')

    for button in category_buttons:
        category_name = button.text.strip()
        category_url = urljoin(url, button['data-value'])
        categories.append({
            'Category': category_name,
            'URL': category_url
        })

    print("Categories extracted successfully:")
    for category in categories:
        print(category)

    return categories

def extract_products_from_category(category_url):
    products = []
    current_page = 1
    proceed = True

    while proceed:
        page_content = fetch_page(f"{category_url}?page={current_page}")
        if page_content:
            soup = BeautifulSoup(page_content, 'html.parser')
            product_list = soup.find_all('div', class_='col-sm-2 col-xs-4 vcenter')

            print(f"Products found on page {current_page} of {category_url}:")

            for product in product_list:
                product_name_tag = product.find('span', class_='hidden', itemprop='name')
                if product_name_tag:
                    product_name = product_name_tag.text.strip()
                    product_url = urljoin(url, product.find('a').get('href'))
                    products.append({
                        'Product Name': product_name,
                        'URL': product_url,
                        'Category URL': category_url
                    })
                    print(f"Product Name: {product_name}, URL: {product_url}")

            if not product_list:
                print("No products found on this page.")
                proceed = False

            current_page += 1
        else:
            proceed = False

    return products

# Fetch the main page
main_page_content = fetch_page(url)
if main_page_content:
    categories = extract_categories(main_page_content)

    all_categories = []
    all_products = []

    for category in categories:
        category_url = category['URL']
        products = extract_products_from_category(category_url)
        if products:
            all_categories.append(category['Category'])
            all_products.extend(products)

    if all_categories and all_products:
        df_categories = pd.DataFrame(all_categories, columns=['Category'])
        df_products = pd.DataFrame(all_products)

        # Save to CSV
        df_categories.to_csv('categories.csv', index=False)
        df_products.to_csv('products.csv', index=False)

        print("Data saved to 'categories.csv' and 'products.csv'.")
    else:
        print("No data to save.")
else:
    print("Failed to fetch the main page.")
