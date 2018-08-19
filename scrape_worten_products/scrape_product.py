# -*- coding: iso-8859-15 -*-

# http://docs.python-requests.org/en/master/
from requests import post, get
# https://beautiful-soup-4.readthedocs.io/en/latest/
from bs4 import BeautifulSoup
from random import randint
import urllib
from datetime import datetime

def scrape(args):
    '''
    Make a query to worten.pt. Then open the page of the
    result and scrape information about it. The function will
    return a string with xml about that page (product).

    Parameters
    ----------
    args : str
        The user query.

    Returns
    -------
    scraped_info : dict
        A dictionary with the scraped information.
    '''

    # Holds the scraped information
    scraped_info = {}

    # Use a try/except clause in case something goes wrong with\
    # the GET requests or the creation of the BeautifulSoup\
    # objects
    try:
        # Target website
        target = 'https://www.worten.pt'
        # Make a GET request to get a text version of the query results
        # Use urllib.parse.urlenconde() to properly encode the arguments for the GET request URL
        query = get('https://www.worten.pt/search?sortBy=relevance&hitsPerPage=24&page=1&'+ urllib.parse.urlencode({'query': args})) 
        # Create a BeautifulSoup object to hold the scraped html, encoding the raw data from\
        # the Response object with iso-8859-15
        soup = BeautifulSoup(query.content, 'lxml', from_encoding="iso-8859-15")
        # Product page for the first result of the query
        prod_link = target + soup.find('div', class_='w-product__wrapper').a["href"]
        # Text version of the product's page source code
        product_page = get(prod_link)
        # Create a new BeautifulSoup object for the product's page, encoding the raw data from\
        # the Response object with iso-8859-15
        soup = BeautifulSoup(product_page.content, 'lxml', from_encoding="iso-8859-15")
    
    # If something does go wrong, the function ends here by returning None
    except:
        return None

    # Product detailed info (this section of the source code will be worked on ahead)
    more_info = soup.find('div', class_='w-product-details__wrapper').div


    # Product availability
    # If there's a <div> for available products, it means the product is available
    if soup.find('div', class_='w-product__availability-title'):
        scraped_info['prod_avail'] = 'Available'
    # If there's a <div> for unavailable products, it means the product is not available
    elif soup.find('div', class_='w-product__unavailability-title'):
        scraped_info['prod_avail'] = 'Not Available'            
    # If neither of the two <div>s exist, the product is available only by pre-order
    else:
        scraped_info['prod_avail'] = 'Pre-Order'

    
    # Product name
    prod_name = more_info.header.h2.find('span', class_='w-section__product').text.strip()
    scraped_info['prod_name'] = prod_name

    # Product category (a single <ul> contains one or more <li> tags, each containing <a> tags\
    # that contain the text we want, the categories)
    prod_cat = soup.find('ul', class_='w-breadcrumbs breadcrumbs').find_all('li')[-1].a.text.strip()
    scraped_info['prod_cat'] = prod_cat

    # Product current price (if it's on sale, scrapes the discounted price)
    prod_price = soup.find('span', class_='w-product__price__current')['content']
    scraped_info['prod_price'] = prod_price

    # Product pictures' links
    # The try clause is for cases where the product has 5 pictures or less
    try:
        pics = soup.find('div', class_='swiper-container w-product-gallery__thumbnails swiper__off').find_all('div', class_='swiper-slide')
        pictures = [target+pic.a.img["src"] for pic in pics]
    # The except clause is run when a product has 6 or more pictures
    # We need to use a different line of code for products with more\
    # than 5 pictures because the source HTML is different for these cases
    except:
        pics = soup.find('div', class_='swiper-wrapper').find_all('div')
        pictures = [target+pic.a.img["src"] for pic in pics]

    scraped_info['prod_pic'] = pictures[0]

    # Product description
    try:
        prod_desc = soup.find('div', class_='w-section__wrapper__content').find_all('p')[1].text.strip()
    # If there's a problem scraping the product's description (such as it being nonexistent), just\
    # create a string telling the information is not available
    except:
        prod_desc = 'Product description not available'
    scraped_info['prod_desc'] = prod_desc

    # Left column info (Usually "Referências", "Características Físicas" and "Mais Informações")
    left_col = more_info.find('div', class_='w-product-details__column w-product-details__moreinfo show-for-medium')
    # Scrapes the titles of each list of aspects in the left column
    l_col_titles = [col.text.strip() for col in left_col.find_all('p')]
    # Scrapes the <ul> tags from the previous section, that is, just the lines\
    # of the list without the title
    l_info_ULs = [col for col in left_col.find_all('ul')]
    # Scrapes <li> tags nested in the previous <ul> tags, that is, each <li>\
    # corresponds to a line of the list of information
    l_info_LIs = [col.find_all('li') for col in l_info_ULs]

    # Product internal reference
    # We scrape this one "directly" because it is always the first value of\
    # the first list in the left column
    prod_ref = l_info_ULs[0].li.find('span', class_='details-value').text.strip()
    scraped_info['prod_ref'] = prod_ref
    
    # Initialize strings to hold information about these aspects of the product
    # They begin as empty strings, so that if they are still empty after trying\
    # to scrape that information, it is assumed the information is not available
    prod_brand = ''
    prod_weight = ''
    prod_dimensions = ''
    prod_color = ''
    # Loop through the <li> elements of the left column, looking for the desired\
    # aspects
    # Note we need a nested for loop, since in the outer loop we loop through the\
    # an iterable of <li> tags stored in the 'l_info_LIs' list, that is,\
    # we are simply looping through that list in the outer loop. In the nested\
    # loop, we loop through each <li> of each of those iterables (which are\
    # the lists of information from the left column of the product specifications)
    for lst in l_info_LIs:
        for li in lst:
            if 'Referência Worten' in li.find('span', class_='details-label').text:
                prod_ref = li.find('span', class_='details-value').text.strip()

            if 'Marca' in li.find('span', class_='details-label').text:
                prod_brand = li.find('span', class_='details-value').text.strip()
            
            if 'Peso' in li.find('span', class_='details-label').text:
                prod_weight = li.find('span', class_='details-value').text.strip()

            # Even though 'Altura', 'Largura' and 'Profundidade' (Height, Width, Depth) will\
            # all make a up a single Dimensions values, they need to be scraped separately
            if 'Altura' in li.find('span', class_='details-label').text:
                prod_dimensions += li.find('span', class_='details-value').text.strip() + '*'

            if 'Largura' in li.find('span', class_='details-label').text:
                prod_dimensions += li.find('span', class_='details-value').text.strip() + '*'

            if 'Profundidade' in li.find('span', class_='details-label').text:
                prod_dimensions += li.find('span', class_='details-value').text.strip()

            if 'Cor' in li.find('span', class_='details-label').text:
                prod_color = li.find('span', class_='details-value').text.strip()

    # After trying to scrape information about these aspects, if the strings are\
    # still empty then just assume the information about said aspects is not\
    # available
    else:
        if not prod_brand:
            prod_brand = 'Information not available'
        if not prod_weight:
            prod_weight = 'Information not available'
        if not prod_dimensions:
            prod_dimensions = 'Information not available'
        if not prod_color:
            prod_color = 'Information not available'

    scraped_info['prod_brand'] = prod_brand
    scraped_info['prod_weight'] = prod_weight
    scraped_info['prod_dimensions'] = prod_dimensions
    scraped_info['prod_color'] = prod_color


    return scraped_info




def gen_html(scraped_data):
    '''
    Creates the HTML page given the scraped data dictionary.
    At the end of the script, after having a single string
    with all the HTML, it creates a new .html file and writes
    the string to it.

    Parameters
    ---------
    scraped_data : dict
        The dictionary with scraped data.

    Returns
    -------
    None
    '''

    # Create the string with HTML
    # Since we are creating an HTML page to be used in a Flask application\
    # the HTML structure is a bit different from the usual
    html_string = '''{% extends "layout.html" %}
<!-- The HTML structure is inherited from layout.html -->
<!-- The following block contains all the content unique to this file -->
{% block content %}'''
    html_string += '\n<article class="prod">' +\
    f'\n\t<section class="prod-info">' +\
    f'\n\t\t<h1 class="prod-name">{scraped_data["prod_name"]}</h1>'
    
    if scraped_data["prod_avail"] == 'Available':
        html_string += f'\n\t\t<h3 class="avail">Availability: <i>{scraped_data["prod_avail"]}</i></h3>'
    elif scraped_data["prod_avail"] == 'Pre-Order':
        html_string += f'\n\t\t<h3 class="pre-avail">Availability: <i>{scraped_data["prod_avail"]}</i></h3>'
    else:
        html_string += f'\n\t\t<h3 class="not-avail">Availability: <i>{scraped_data["prod_avail"]}</i></h3>'
    
    html_string += f'\n\t\t<p class="prod-id">{scraped_data["prod_ref"]}<p>' +\
    f'\n\t\t<img src="{scraped_data["prod_pic"]}" alt="Product Picture"/>' +\
    f'\n\t\t<p class="prod-desc">{scraped_data["prod_desc"]}</p>' +\
    f'\n\t</section>' +\
    f'\n\t<section class="extra-info">' +\
    f'\n\t\t<table class="extra">' +\
    f'\n\t\t\t<tr>\n\t\t\t\t<td>Price</td>\n\t\t\t\t<td>€{scraped_data["prod_price"]}</td>\n\t\t\t</tr>' +\
    f'\n\t\t\t<tr>\n\t\t\t\t<td>Category</td>\n\t\t\t\t<td>{scraped_data["prod_cat"]}</td>\n\t\t\t</tr>' +\
    f'\n\t\t\t<tr>\n\t\t\t\t<td>Brand</td>\n\t\t\t\t<td>{scraped_data["prod_brand"]}</td>\n\t\t\t</tr>' +\
    f'\n\t\t\t<tr>\n\t\t\t\t<td>Weight</td>\n\t\t\t\t<td>{scraped_data["prod_weight"]}</td>\n\t\t\t</tr>' +\
    f'\n\t\t\t<tr>\n\t\t\t\t<td>Dimensions</td>\n\t\t\t\t<td>{scraped_data["prod_dimensions"]}</td>\n\t\t\t</tr>' +\
    f'\n\t\t\t<tr>\n\t\t\t\t<td>Color</td>\n\t\t\t\t<td>{scraped_data["prod_color"]}</td>\n\t\t\t</tr>' +\
    f'\n\t\t\t</table>\n\t\t</section>' +\
    f'\n</article>'

    html_string += '{% endblock content %}'

    # Now that the HTML is finished, we can create a new .html file and write\
    # the string to it (note we write using the ISO-8859-15 encoding)
    with open('scrape_worten_products\\templates\\query_result.html', 'w', encoding='iso-8859-15') as f:
        f.write(html_string)
    
    return None