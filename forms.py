from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, HiddenField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Regexp, NumberRange
from wtforms import Form, StringField, RadioField, SelectField, TextAreaField, validators, DecimalField, FileField, IntegerField
from wtforms.fields import EmailField, DateField
from datetime import datetime
import email_validator
import re
import requests
import shelve
from flask import current_app

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(message="email is required"), Email(message="Please enter a valid email")])
    password = PasswordField('Password', validators=[DataRequired(message="password is required")])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message="email is required"),
        Email(message="Please enter a valid email")
    ])
    username = StringField('Username', validators=[
        DataRequired(message="username is required"),
        Length(min=3, max=20, message="Username must be between 3 and 20 characters")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="password is required")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message="password is required"),
        EqualTo('password', message="Passwords must match")
    ])
    submit = SubmitField('Register')

    def validate_username(self, username):
        if not username.data.isalnum():
            raise ValidationError("Username can only contain letters and numbers")

class EditUsernameForm(FlaskForm):
    username = StringField('New Username', validators=[
        DataRequired(),
        Length(min=3, max=20, message="Username must be between 3 and 20 characters")
    ])
    submit = SubmitField('Update Username')

    def validate_username(self, username):
        if not username.data.isalnum():
            raise ValidationError("Username can only contain letters and numbers")


class NumberOnlyValidator(object):
    def __init__(self, message=None):
        if not message:
            message = 'Please enter numbers only'
        self.message = message

    def __call__(self, form, field):
        if not field.data.isdigit():
            raise validators.ValidationError(self.message)

class FutureDateValidator:
    def __init__(self, message=None):
        if not message:
            message = 'Date cannot be in the future'
        self.message = message

    def __call__(self, form, field):
        if field.data and field.data > datetime.now().date():
            raise validators.ValidationError(self.message)

class CreateDefectForm(Form):
    bike_id = StringField('Bike ID', [
        validators.DataRequired(),
        validators.Length(min=1, max=20)
    ])

    defect_type = SelectField('Defect type',
                              [validators.DataRequired()],
                              choices=[('', 'Select'), ('New', 'New Defect'), ('Old', 'Old Defect')],
                              default='')

    date_found = DateField('Date Found',
                           format='%Y-%m-%d',
                           validators=[
                               validators.DataRequired(message="Date is required"),
                               FutureDateValidator()
                           ])

    bike_location = TextAreaField('Location of Bike', [
        validators.Length(max=200),
        validators.DataRequired(message="Please enter a location."),
    ])

    severity = RadioField('Severity',
                          choices=[('V', 'Very Serious'),
                                   ('S', 'Serious'),
                                   ('N', 'Normal'),
                                   ('L', 'Less Serious'),
                                   ('X', 'Not so serious')],
                          default='N')

    description = TextAreaField('Description',
                                [validators.DataRequired()])

    def validate_bike_location(self, field):
        address = field.data
        api_key = current_app.config.get('GOOGLE_MAPS_API_KEY')  # Ensure the API key is configured

        # List of known Singapore locations (can be expanded)
        valid_general_locations = [
            "Choa Chu Kang", "Ang Mo Kio", "Pasir Ris", "Jurong East", "Jurong West",
            "Bukit Batok", "Tampines", "Punggol", "Sengkang", "Yishun", "Woodlands",
            "Bedok", "Clementi", "Queenstown", "Toa Payoh", "Serangoon", "Changi",
            "Bukit Gombak", "Abingdon Road", "Adam Drive", "Adam Park", "Adam Road", "Adis Road",
            "Admiralty Drive", "Admiralty Lane", "Admiralty Link", "Admiralty Road East", "Admiralty Road West",
            "Admiralty Road", "Admiralty Street", "Ah Hood Road", "Ah Soo Garden", "Ah Soo Walk", "Aida Street", "Airline Road",
            "Airport Boulevard", "Airport Cargo Road", "Akyab Road", "Albert Street", "Alexandra Lane", "Alexandra Road",
            "Alexandra Terrace", "Aliwal Street", "Aljunied Avenue 1", "Aljunied Avenue 2", "Aljunied Avenue 3",
            "Aljunied Avenue 4", "Aljunied Avenue 5", "Aljunied Crescent", "Aljunied Road", "Alkaff Avenue",
            "Allamanda Grove", "Allanbrooke Road", "Allenby Road", "Almond Avenue", "Almond Crescent",
            "Almond Street", "Alnwick Road", "Ama Keng Road", "Amber Close", "Amber Gardens", "Amber Road",
            "Amberwood Close 1", "Amberwood Close 2", "Amberwood Close 3", "Amberwood Close 4", "Amberwood Close 5",
            "Amoy Street", "Anamalai Avenue", "Anchorvale Crescent", "Anchorvale Drive", "Anchorvale Lane",
            "Anchorvale Link", "Anchorvale Street", "Anderson Road", "Andover Road", "Andrew Avenue", "Andrew Road",
            "Ang Mo Kio Avenue 1", "Ang Mo Kio Avenue 10", "Ang Mo Kio Avenue 12", "Ang Mo Kio Avenue 2",
            "Ang Mo Kio Avenue 3", "Ang Mo Kio Avenue 4", "Ang Mo Kio Avenue 5", "Ang Mo Kio Avenue 6",
            "Ang Mo Kio Avenue 7", "Ang Mo Kio Avenue 8", "Ang Mo Kio Avenue 9", "Ang Mo Kio Central 1",
            "Ang Mo Kio Central 2", "Ang Mo Kio Central 2A", "Ang Mo Kio Central 3", "Ang Mo Kio Industrial Park 1",
            "Ang Mo Kio Industrial Park 2", "Ang Mo Kio Industrial Park 2A", "Ang Mo Kio Industrial Park 3",
            "Ang Mo Kio Street 11", "Ang Mo Kio Street 12", "Ang Mo Kio Street 13", "Ang Mo Kio Street 21",
            "Ang Mo Kio Street 22", "Ang Mo Kio Street 23", "Ang Mo Kio Street 24", "Ang Mo Kio Street 31", "Ang Mo Kio Street 32", "Ang Mo Kio Street 41", "Ang Mo Kio Street 42", "Ang Mo Kio Street 43", "Ang Mo Kio Street 4451", "Ang Mo Kio Street 52", "Ang Mo Kio Street 53", "Ang Mo Kio Street 54", "Ang Mo Kio Street 61", "Ang Mo Kio Street 62", "Ang Mo Kio Street 63", "Ang Mo Kio Street 64", "Ang Mo Kio Street 65", "Angklong Lane", "Angora Close", "Angsana Avenue", "Angullia Park", "Angus Street", "Ann Siang Hill", "Ann Siang Road", "Anson Road", "Anthony Road", "Arab Street", "Arcadia Road", "Architecture Drive", "Ardmore Park", "Armenian Street", "Arnasalam Chetty Road", "Aroozoo Avenue", "Aroozoo Lane", "Arthur Road", "Artillery Avenue", "Artillery Close", "Artillery Link", "Arts Link", "Arumugam Road", "Ascot Rise", "Ash Grove", "Ashwood Grove", "Asimont Lane", "Astrid Hill", "Attap Valley Road", "Auckland Road East", "Auckland Road West", "Ava Road", "Aviation Drive", "Avon Road", "Ayer Rajah Avenue", "Ayer Rajah Crescent",

        ]

        # First, check if the address matches a known general location
        if address in valid_general_locations:
            return  # Address is valid

        # Otherwise, validate using Google Maps Geocoding API
        response = requests.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={"address": address, "key": api_key}
        )
        data = response.json()
        if response.status_code != 200 or data.get('status') != 'OK':
            raise ValidationError("Invalid address. Please enter a valid location in Singapore.")

        # Ensure the address is in Singapore
        if not any("Singapore" in comp.get('long_name', '') for result in data['results'] for comp in result.get('address_components', [])):
            raise ValidationError("Location must be in Singapore. Please enter a valid Singapore address.")



    def validate_bike_id(self, field):
        bike_id = field.data
        try:
            with shelve.open('bike_ids.db', 'r') as db:
                bike_ids = db.get('bike_ids', {})
                if bike_id not in bike_ids:
                    raise ValidationError("Bike ID does not exist. Please enter a valid Bike ID.")
        except Exception as e:
            raise ValidationError("Bike ID does not exist. Please enter a valid Bike ID.")


class UpdateDefectForm(Form):
    status = SelectField('Status',
                         [validators.DataRequired()],
                         choices=[('Pending', 'Pending'),
                                  ('Repaired', 'Repaired'),
                                  ('Closed', 'Closed')],
                         default='Pending')
    
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
    id_string = StringField(
        'Bike ID',
        validators=[DataRequired(message="Bike ID is required.")],
    )
    bike_name = StringField(
        'Bike Name',
        validators=[DataRequired(message="Bike Name is required.")],
    )
    stock_quantity = IntegerField(
        'Stock Quantity',
        validators=[
            DataRequired(message="Stock Quantity is required."),
            NumberRange(min=1, message="Stock must be at least 1."),
        ],
    )
    submit = SubmitField('Add/Update Bike ID')


    
class CreateBikeForm(Form):

    bike_name = StringField("Bike Name: ", [validators.Length(min=1, max=50), validators.DataRequired()])
    upload_bike_image = FileField("Bike Upload: ", )
    price = DecimalField("Price $: ", [validators.NumberRange(min=1, message="Price must be greater than 0"), validators.DataRequired()])
    transmission_type = SelectField("Transmission Type: ", choices=[("Manual", "Manual"), ("Automatic", "Automatic")], validators=[validators.DataRequired()])
    seating_capacity = SelectField("Seating Capacity: ", choices=[("1", "1 Seat"), ("2", "2 Seats")], default="1", validators=[validators.DataRequired()])
    engine_output = StringField("Engine Output (W): ", [validators.DataRequired()])
    stock_quantity = IntegerField('Stock Quantity', validators=[validators.DataRequired(), validators.NumberRange(min=0)])

class CreateFAQForm(Form):
    question = StringField('Question', [validators.Length(min=1, max=150), validators.DataRequired()])
    answer = TextAreaField('Answer', [validators.Length(min=1), validators.DataRequired()])

class UpdateFAQForm(Form):
    question = StringField('Question', [validators.Length(min=1, max=150), validators.DataRequired()])
    answer = TextAreaField('Answer', [validators.Length(min=1), validators.DataRequired()])