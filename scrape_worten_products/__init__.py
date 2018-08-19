from flask import Flask

def create_app():
	'''
	Function to create a new application (Flask instance).

	Parameters
	----------

	Returns
	-------
	flask.app.Flask
		The app instace.
	'''

	# Create the app
	app = Flask(__name__)

	# Define the Secret Key variable for the app configuration
	app.config['SECRET_KEY'] = 'not_using_one'
	# Check for modifications to templates so it uses their latest\
	# version
	app.config['TEMPLATES_AUTO_RELOAD'] = True

	# Import the "main" Blueprint
	from scrape_worten_products.main.routes import main
	# And register it in the app
	app.register_blueprint(main)

	return app