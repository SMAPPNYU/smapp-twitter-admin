from flask_wtf import Form
from wtforms import TextField, BooleanField, DateField, SelectField

class FilterCriterionForm(Form):
    # filter_type = TextField('Filter Type')
    filter_type = SelectField('Filter Type', choices=[('track', 'track'), ('follow', 'follow'), ('geo', 'geo')])
    value = TextField('Value')
    active = BooleanField('Active')
    date_added = DateField('Date Added')
    date_stopped = DateField('Date Stopped')

