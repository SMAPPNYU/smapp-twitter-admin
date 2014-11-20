from flask_wtf import Form
from wtforms import TextField, BooleanField, DateField, SelectField, HiddenField, TextAreaField
from wtforms.validators import Optional, Required

from smapp_twitter_admin.post_filters import filter_choices

class FilterCriterionForm(Form):
    filter_type = SelectField('Filter Type', choices=[('track', 'track'), ('follow', 'follow'), ('geo', 'geo')])
    value = TextField('Value')
    active = BooleanField('Active')
    date_added = DateField('Date Added')
    date_removed = DateField('Date Removed', validators=[Optional()])

class FilterCriteriaManyForm(Form):
    keywords = TextAreaField('Keywords', validators=[Required()])

class PostFilterForm(Form):
    filter_type = SelectField('Filter Type', choices=filter_choices())
    arguments = TextField('Arguments')
    active = BooleanField('Active')
    date_added = DateField('Date Added')
    date_removed = DateField('Date Removed', validators=[Optional()])