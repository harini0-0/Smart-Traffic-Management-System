from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,SubmitField
from wtforms.validators import DataRequired,Length

class NeighbourhoodStat(FlaskForm):
	yourLocation = StringField('Location', validators = [DataRequired()])
	submit = SubmitField('Get Status')

class GetRoute(FlaskForm):
	userLocation = StringField('Location', validators = [DataRequired()])
	destination = StringField('Destination', validators = [DataRequired()])
	submit = SubmitField('Get Route')
