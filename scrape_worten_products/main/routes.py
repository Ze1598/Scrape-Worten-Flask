# render_template: render HTML templates
# request: used to get query parameter values from URLs
# Blueprint: used to make this module into a flask blueprint
# redirect: redirect the user to a given route
# url_for: the url for a given route
from flask import render_template, request, Blueprint, redirect, url_for
from scrape_worten_products.main.forms import SearchForm
# Import the module I've written to scrape a product given\
# the user's query to then create the HTML page to show it
from scrape_worten_products.scrape_product import scrape, gen_html

# Create a Blueprint for this module, so that it can then be imported\
# from the main app script
main = Blueprint('main', __name__)

# Route to the Home (root) page
@main.route("/", methods=['GET', 'POST'])
@main.route("/home", methods=['GET', 'POST'])
def home():

	# This route always shows the search form
	form = SearchForm()

	# If the user made a POST request, that is, entered information\
	# (made a query)
	if request.method == 'POST':
		# Get the user's query
		user_query = form.query.data
		# Scrape using the user's query
		scraped_info = scrape(user_query)
		# Create the HTML page
		scraped_info = gen_html(scraped_info)
		# Return and render the created page
		return redirect(url_for("main.query_result"))

	return render_template("home.html", title="Home", form=form)


# Route to the About page
@main.route("/about")
def about():
	return render_template("about.html", title="About")


# Route to the page of query results
@main.route("/query_result", methods=['GET', 'POST'])
def query_result():

	# This route always shows the search form
	form = SearchForm()

	# If the user made a POST request, that is, entered information\
	# (made a query)
	if request.method == 'POST':
		# Get the user's query
		user_query = form.query.data
		# Scrape a product using the user's query
		scraped_info = scrape(user_query)
		# Create the HTML page
		scraped_info = gen_html(scraped_info)
		# Return and render the created page
		return redirect(url_for("main.query_result"))

	return render_template("query_result.html", title="Query Result", form=form)


# Just a test route
'''
@main.route("/test_route")
def test_route():
	form = SearchForm()
	return render_template("test_route.html", title="Test Route", form=form)
'''