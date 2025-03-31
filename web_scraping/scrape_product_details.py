from bs4 import BeautifulSoup
import requests
import csv
import os
def get_page_content(url):
    response = requests.get(url)
    return response.text

def parse_product_page(url):
    item = {}
    page_html = get_page_content(url)
    page_soup = BeautifulSoup(page_html, 'html.parser')
    #get main container
    main_container = page_soup.find('div', class_='column main')
    info_container = main_container.find('div', class_='product-info-main')
    item["name"] = info_container.find('span', class_='base').get_text().strip().strip('"')

    # add price
    price = main_container.find('span', class_='price-wrapper')['data-price-amount']
    item["price"] = price

    # add product description
    description_container = main_container.find('div', class_='col-6 des_left_content')
    if description_container:
        for br in description_container.find_all('br'):
            br.extract()
        description = description_container.find_all('p')[1].get_text().strip().strip('"')
        item["description"] = description.replace('\n', ' ').replace('\r', '')

    # add pairings
    pairings_container = main_container.find('ul', class_='pair_list')
    if pairings_container:
        pairings = pairings_container.find_all('li')
        for pairing in pairings:
            pairing_spans = pairing.find_all('span')
            item[pairing_spans[0].get_text().strip().strip('"').lower() + "_pairing"] = pairing_spans[1].get_text().strip().strip('"')

        # item["meat_pairing"] =  pairings[0].find('span', class_=False).get_text().strip().strip('"')
        # item["seafood_pairing"] = pairings[1].find('span', class_=False).get_text().strip().strip('"')
        # item["legumes_pairing"] = pairings[2].find('span', class_=False).get_text().strip().strip('"')

    # add accolades list
    accolades_list = []
    accolades_container = main_container.find('div', id='accolades')
    if accolades_container:
        accolades = accolades_container.find_all('div', class_='accolades')        
        for accolade in accolades:
            h4_tag = accolade.find('h4')  # Find the 'h4' inside each 'accolade_info'
            if h4_tag:
                accolades_list.append(h4_tag.get_text(strip=True))
            else:
                print("No h4 tag found in this accolade_info")
    item["accolades"] = ', '.join(accolades_list)

        
    
    
    attributes_container = main_container.find('table', id='product-attribute-specs-table')
    for row in attributes_container.find_all('tr'):
        # Find the 'th' (key) and 'td' (value) elements
        th = row.find('th')
        td = row.find('td')
        
        if th and td:
            # Extract the text from the 'th' and 'td' and clean them up
            key = th.get_text(strip=True).lower().replace(" ", "_")
            value = td.get_text(strip=True).replace('\n', ' ').replace('\r', '')
            
            # Add the key-value pair to the dictionary
            item[key] = value
    return item


def write_to_csv(data, csv_file):
    """
    Writes a list of dictionaries to a CSV file with varying headers.

    Args:
    - data (list of dict): The data to write to the CSV.
    - csv_file (str): The path to the CSV file to write.
    """
    # Combine all headers (keys) from all dictionaries in the list
    all_headers = set()
    for record in data:
        all_headers.update(record.keys())

    
    headers = sorted(all_headers)

    # write to csv
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers, delimiter=';')

        # Write the header row
        writer.writeheader()

        # Write each dictionary as a row in the CSV
        for record in data:
            writer.writerow(record)

    print(f"Data successfully written to {csv_file}")



def scrape_wine_data(filename="item_links.csv"):
    # Open the item links CSV file to read URLs
    wines = []
    with open(filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        current_row = 1

        for row in reader:
            wine_url = row[2]
            
            if 'Masterclass' in row[0]:
                continue  
            
            print("Scraping wine:", row[0])
            print("Row:", current_row)
            current_row += 1
            
            # Get the wine data from the product page
            wine_data = parse_product_page(wine_url)
            
            wines.append(wine_data)

            print(f"Finished scraping wine: {row[0]}")
    return wines


# filename = "item_links.csv"
# with open(filename, mode='r', newline='', encoding='utf-8') as file:
#     reader = csv.reader(file)
#     next(reader)  # Skip the header row
#     wines = []
#     current_row = 1
#     for row in reader:
#         wine_url = row[2]
#         if 'Masterclass' in row[0]:
#             continue
#         print("Scraping wine:", row[0])
#         print("Row:", current_row)
#         current_row += 1
#         wine_data = parse_product_page(wine_url)
#         wines.append(wine_data)
#         # print(wine_data)

#     write_wines_to_csv(wines, "wine_data.csv")
#     print("Finished writing wine data to CSV file.")

wines = scrape_wine_data()
write_to_csv(wines, "wine_data.csv")