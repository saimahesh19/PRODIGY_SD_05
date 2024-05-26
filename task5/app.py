# "http://books.toscrape.com/"
from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup
import csv

app = Flask(__name__)

def scrape_books(url):
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the product containers
        products = soup.find_all('article', class_='product_pod')

        # Store scraped data in a list of dictionaries
        scraped_data = []

        # Loop through each product container to extract information
        for product in products:
            # Extract the product name
            product_name = product.h3.a['title']

            # Extract the product price
            product_price = product.find('p', class_='price_color').text.strip()

            # Extract the product rating
            rating_classes = product.find('p', class_='star-rating')['class']
            product_rating = [r for r in rating_classes if r != 'star-rating'][0]

            # Add extracted information to the list
            scraped_data.append({
                'Product Name': product_name,
                'Price': product_price,
                'Rating': product_rating
            })

        return scraped_data
    else:
        return None

@app.route('/')
def index():
    # Read data from CSV file
    data = []
    with open('books.csv', 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return render_template('index.html', data=data)

@app.route('/scrape', methods=['POST'])
def scrape():
    # Get URL from request data
    url = request.json.get('url')

    if url:
        scraped_data = scrape_books(url)
        if scraped_data:
            # Write scraped data to CSV file
            with open('books.csv', 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=['Product Name', 'Price', 'Rating'])
                writer.writeheader()
                writer.writerows(scraped_data)

            return jsonify({'message': 'Scraping successful. Data saved to books.csv'}), 200
        else:
            return jsonify({'error': 'Failed to scrape data from the provided URL'}), 400
    else:
        return jsonify({'error': 'No URL provided in the request'}), 400

if __name__ == '__main__':
    app.run(debug=True)

