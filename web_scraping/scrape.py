import requests
from bs4 import BeautifulSoup
import csv

def get_page_content(url):
    # Send a GET request to fetch the HTML content of the page
    response = requests.get(url)
    return response.text

def parse_results_page(results_page_url):
    # Get result from main page which contains snippets of all the items
    page_html = get_page_content(results_page_url)
    page_soup = BeautifulSoup(page_html, 'html.parser')
    
    # Extract links to individual item pages 
    items = []

    for product in page_soup.find_all('li', class_='product-item'):
        item = {}
        item["name"] = product.find('a', class_='product-item-link').get_text().strip().strip('"')
        item["link"] = product.find('a', class_='product-item-link')['href']
        item["price"] = product.find('span', class_='price-wrapper')['data-price-amount']



        items.append(item)



    
    return items

def save_links_to_csv(items, filename="item_links.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Item Name", "Item Price", "Item Link"])
        for item_details in items:
            writer.writerow([item_details["name"], item_details["price"], item_details["link"]])



page_content = get_page_content("https://wineconnection.com.sg/buy-wine-online/all-wines.html")
results = []
for i in range(1, 27):
    print("Scraping page", i)    
    if i == 1:
        pg_results = parse_results_page("https://wineconnection.com.sg/buy-wine-online/all-wines.html")
    pg_results = parse_results_page("https://wineconnection.com.sg/buy-wine-online/all-wines.html?p=" + str(i))
    results.extend(pg_results)



    

# save_links_to_csv(results)
