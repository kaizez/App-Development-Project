from wtforms import Form, StringField, RadioField, SelectField, TextAreaField, validators
from wtforms.fields import EmailField, DateField
from datetime import datetime

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
        validators.Length(min=1, max=20),
        NumberOnlyValidator()
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

    bike_location = TextAreaField('Location of Bike',
                                  [validators.length(max=200),
                                   validators.DataRequired()])

    severity = RadioField('Severity',
                          choices=[('V', 'Very Serious'),
                                   ('S', 'Serious'),
                                   ('N', 'Normal'),
                                   ('L', 'Less Serious'),
                                   ('X', 'Not so serious')],
                          default='N')

    description = TextAreaField('Description',
                                [validators.DataRequired()])

class UpdateDefectForm(Form):
    status = SelectField('Status',
                         [validators.DataRequired()],
                         choices=[('Pending', 'Pending'),
                                  ('Repaired', 'Repaired'),
                                  ('Closed', 'Closed')],
                         default='Pending')