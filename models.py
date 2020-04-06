from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField, TextAreaField
from wtforms.fields.html5 import DateField
from wtforms.validators import Length, Email, Required

class StockForm(FlaskForm):
    stock_ticker=TextField('Stock Symbol',validators=[Required()])
    month = DateField('Month',render_kw={'data-provide':'datepicker'})
    submit = SubmitField('Submit')
