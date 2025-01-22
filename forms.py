# In forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, HiddenField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Regexp, Email
import re  # Add this import at the top

class DateSelectionForm(FlaskForm):
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    submit = SubmitField('Proceed to Payment') #Submit button redirects to payment

class PaymentForm(FlaskForm):
    # Shipping/Billing Info
    full_name = StringField('Full Name', 
                          validators=[DataRequired(message="Please enter your full name")])
    email = StringField('Email', 
                       validators=[DataRequired(message="Please enter your email"),
                                 Email(message="Please enter a valid email address")])
    address = StringField('Address', 
                         validators=[DataRequired(message="Please enter your address")])
    city = StringField('City', 
                      validators=[DataRequired(message="Please enter your city")])
    postal_code = StringField('Postal Code', 
                            validators=[DataRequired(message="Please enter your postal code"),
                                      Regexp('^[0-9]{6}$', message="Postal code must be 6 digits")])
    
    # Payment Info
    def validate_card_number(form, field):
        # Remove any spaces from the card number
        number = field.data.replace(' ', '')
        if not number.isdigit():
            raise ValidationError("Card number must contain only digits")
        if len(number) != 16:
            raise ValidationError("Card number must be 16 digits")
    
    card_no = StringField('Card Number', 
                         validators=[DataRequired(message="Please enter your card number"),
                                   validate_card_number])
    
    cvv = StringField('CVV', 
                     validators=[DataRequired(message="Please enter the CVV"),
                               Regexp('^[0-9]{3,4}$', message="CVV must be 3 or 4 digits")])
    
    def validate_exp_date(form, field):
        if not field.data:
            raise ValidationError("Please enter the expiration date")
        # Remove any spaces from the expiration date
        exp = field.data.replace(' ', '')
        if not re.match('^(0[1-9]|1[0-2])/([0-9]{2})$', exp):
            raise ValidationError("Expiration date must be in MM/YY format")
    
    exp_date = StringField('Expiration Date', 
                          validators=[DataRequired(message="Please enter the expiration date"),
                                    validate_exp_date])
    
    submit = SubmitField('Place Order')
    latitude = HiddenField('Latitude')
    longitude = HiddenField('Longitude')
    
    
class LockUnlockForm(FlaskForm):
    bike_id = StringField('Bike ID', validators=[DataRequired()])
    submit = SubmitField('Submit')

class BikeIDManagementForm(FlaskForm):
    id_string = StringField('Bike ID', validators=[DataRequired()])
    bike_name = StringField('Bike Name', validators=[DataRequired()])
    submit = SubmitField('Add ID')