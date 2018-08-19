from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    '''
    Form used to create new posts.

    Attributes
    ----------
    query : wtforms.fields.core.UnboundField
    	A text field for the user to enter its
    	query.

    submit : wtforms.fields.core.UnboundField
    	A submission button for the user to submit
    	its query.

    Methods
    -------
    None
    '''

    # Create a (text) field with a "Query" label. It\
    # is a required field
    query = StringField('Query')
    # Create a submission field
    submit = SubmitField('Search')