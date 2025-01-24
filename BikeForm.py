from wtforms import Form, StringField, DecimalField, SelectField, validators, FileField, IntegerField

class CreateBikeForm(Form):

    bike_name = StringField("Bike Name: ", [validators.Length(min=1, max=50), validators.DataRequired()])
    upload_bike_image = FileField("Bike Upload: ", )
    price = DecimalField("Price $: ", [validators.NumberRange(min=1, message="Price must be greater than 0"), validators.DataRequired()])
    transmission_type = SelectField("Transmission Type: ", choices=[("Manual", "Manual"), ("Automatic", "Automatic")], validators=[validators.DataRequired()])
    seating_capacity = SelectField("Seating Capacity: ", choices=[("1", "1 Seat"), ("2", "2 Seats")], default="1", validators=[validators.DataRequired()])
    engine_output = StringField("Engine Output (W): ", [validators.DataRequired()])
    stock_quantity = IntegerField('Stock Quantity', validators=[validators.DataRequired(), validators.NumberRange(min=0)])
