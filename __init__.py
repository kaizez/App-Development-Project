from forms import DateSelectionForm, PaymentForm, BikeIDManagementForm, LockUnlockForm  # Add the new form classes

import logging
import shelve
import random
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session
from werkzeug.utils import secure_filename
from myclass import Product, Order, carparks, BikeID
from math import radians, sin, cos, sqrt, atan2
import os  # Required to access environment variables


def load_env(file_path=".env"):
    """A simple .env file loader."""
    try:
        with open(file_path, "r") as env_file:
            for line in env_file:
                # Ignore comments and empty lines
                line = line.strip()
                if line.startswith("#") or not line:
                    continue
                
                # Parse key-value pairs
                key, value = line.split("=", 1)
                os.environ[key] = value.strip()
    except FileNotFoundError:
        print(f"Warning: .env file not found at {file_path}")
    except Exception as e:
        print(f"Error loading .env file: {e}")

# Load the .env variables
load_env()

# Access the variables
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# Create the Flask app
app = Flask(__name__)
app.secret_key = 'yes'  # Set the secret key for the app
logging.basicConfig(level=logging.DEBUG)  # Set the logging level to debug


# create the flask app
app = Flask(__name__)
# set the secret key for the app
app.secret_key = 'yes'
# set the logging level to debug
logging.basicConfig(level=logging.DEBUG)

def initialize_products():
    """Initialize the products database if it doesn't exist"""
    try:
        with shelve.open('product.db', 'c') as db:
            products = {
                1: Product(1, "Activa-E", 30.00, "Manual, 2 Seater, 700W", stock=10),
                2: Product(2, "Ecima", 45.00, "Manual, 2 Seater, 900W", stock=15),
                3: Product(3, "EV Urban", 65.00, "Manual, 2 Seater, 1200W", stock=20),
                4: Product(4, "EV Fun", 75.00, "Manual, 1 Seater, 1500W", stock=5),
                5: Product(5, "Energica Experia", 90.00, "Manual, 2 Seater, 1380W", stock=8),
                6: Product(6, "Niggaton", 90.00, "Manual, 2 Seater, 1380W", stock=10)
            }
            db['products'] = products
            logging.info("Products initialized successfully")
    except Exception as e:
        logging.error(f"Error initializing products: {e}")
@app.route('/')
def home():
    """Home page of the application"""
    return render_template('home.html')

@app.route('/products')
def view_products():
    try:
        logging.debug("Attempting to open product.db")
        with shelve.open('product.db', 'r') as db:
            logging.debug(f"Database opened, keys: {list(db.keys())}")
            products = db.get('products', {})
            logging.debug(f"Products retrieved: {len(products)}")
            return render_template('products.html', products=products.values())
    except Exception as e:
        logging.error(f"Error in view_products: {str(e)}", exc_info=True)
        flash("Error loading products", "error")
        return redirect(url_for('home'))

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
#Add products to Db
    try:
        with shelve.open('product.db', 'r') as db:
            products = db.get('products', {})
            product = products.get(product_id)
            
            if not product:
                flash("Product not found", "error")
                return redirect(url_for('view_products'))

        with shelve.open('cart.db', 'c') as db:
            cart = {}  # Reset cart
            cart[product_id] = {
                'product': product, #Product object saved under "Product"
                'quantity': 1
            }
            db['cart'] = cart

        return redirect(url_for('checkout'))
    except Exception as e:
        flash("Error processing item", "error")
        return redirect(url_for('view_products'))
    

@app.route('/checkout', methods=['GET', 'POST'])## JUst selecting date for rental
def checkout():
    form = DateSelectionForm()#initializes an instance of the DateSelectionForm from forms.py
    try:
        with shelve.open('cart.db', 'r') as db:
            cart = db.get('cart', {})
            
            if not cart:
                flash("No item in cart", "error")
                return redirect(url_for('view_products'))
            
            item = list(cart.values())[0]  # Get the first item (which in this case is all the items)
            base_price = item['product'].get_price()
            
            if form.validate_on_submit():
                days = (form.end_date.data - form.start_date.data).days + 1 #calc days from .end_date and .start_date in days, and +1 represents include the start and end date
                total = base_price * days
                
                session['rental_info'] = {# Store dates and price in session
                    'start_date': form.start_date.data.strftime('%Y-%m-%d'),
                    'end_date': form.end_date.data.strftime('%Y-%m-%d'),
                    'days': days,
                    'total': total
                }
                
                return redirect(url_for('payment'))
            
            return render_template('checkout.html', 
                                 form=form, 
                                 cart_items=cart.values(), 
                                 total=base_price)
    except Exception as e:
        logging.error(f"Error in checkout: {str(e)}", exc_info=True)
        flash("Error processing checkout", "error")
        return redirect(url_for('view_products'))

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    form = PaymentForm()
    rental_info = session.get('rental_info')
    
    if not rental_info:
        flash("Please select rental dates first", "error")
        return redirect(url_for('checkout'))
    
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                with shelve.open('cart.db', 'r') as db:
                    cart = db.get('cart', {})
                    if not cart:
                        flash("Cart is empty", "error")
                        return redirect(url_for('view_products'))
                    
                # Generate order ID based on current timestamp
                order_id = datetime.now().strftime('%Y%m%d%H%M%S')
                
                # Get rental dates from session
                rental_dates = {
                    'start_date': rental_info['start_date'],
                    'end_date': rental_info['end_date'],
                    'days': rental_info['days']
                }
                
                # Store user email in session for unlock/lock functionality
                session['user_email'] = form.email.data
                logging.info(f"Stored email in session: {form.email.data}")
                
                # Find nearest carpark if coordinates are provided
                nearest_carpark = None
                if form.latitude.data and form.longitude.data:
                    try:
                        nearest_carpark = find_nearest_carpark(
                            float(form.latitude.data),
                            float(form.longitude.data)
                        )
                    except ValueError as e:
                        logging.error(f"Error finding nearest carpark: {e}")
                        flash("Error processing location data", "error")
                        return render_template('payment.html', form=form, google_maps_api_key=GOOGLE_MAPS_API_KEY)
                
                # Compile customer information
                customer_info = {
                    'full_name': form.full_name.data,
                    'email': form.email.data,
                    'address': form.address.data,
                    'city': form.city.data,
                    'postal_code': form.postal_code.data,
                    'payment_info': {
                        'card_last_4': form.card_no.data[-4:],  # Only store last 4 digits
                        'exp_date': form.exp_date.data
                    }
                }
                
                # Add carpark information if available
                if nearest_carpark:
                    customer_info['assigned_carpark'] = nearest_carpark
                    logging.info(f"Assigned carpark: {nearest_carpark['name']} for order {order_id}")
                
                # Create new order
                order = Order(
                    order_id=order_id,
                    items=dict(cart),
                    total=rental_info['total'],
                    customer_info=customer_info,
                    order_date=datetime.now(),
                    rental_dates=rental_dates
                )
                
                # Save order to database
                try:
                    with shelve.open('orders.db', 'c') as db:
                        orders = db.get('orders', {})
                        orders[order_id] = order
                        db['orders'] = orders
                        logging.info(f"Order {order_id} saved successfully")
                except Exception as e:
                    logging.error(f"Error saving order to database: {e}")
                    flash("Error saving order", "error")
                    return render_template('payment.html', form=form, google_maps_api_key=GOOGLE_MAPS_API_KEY)
                
                # Clear session data except for email
                rental_info = session.pop('rental_info', None)
                
                # Clean up cart
                try:
                    with shelve.open('cart.db', 'c') as db:
                        if 'cart' in db:
                            del db['cart']
                except Exception as e:
                    logging.error(f"Error clearing cart: {e}")
                
                flash("Order placed successfully!", "success")
                return redirect(url_for('order_confirmation', order_id=order_id))
                
            except Exception as e:
                logging.error(f"Error processing payment: {e}", exc_info=True)
                flash("Error processing payment", "error")
                return render_template('payment.html', form=form, google_maps_api_key=GOOGLE_MAPS_API_KEY)
        else:
            # If form validation fails, log errors and re-render template
            logging.warning(f"Form validation failed: {form.errors}")
            return render_template('payment.html', form=form, google_maps_api_key=GOOGLE_MAPS_API_KEY)

    # GET request - render empty form
    return render_template('payment.html', form=form, google_maps_api_key=GOOGLE_MAPS_API_KEY)# Add new route for viewing orders

@app.route('/orders')
def view_orders():
    """View all orders"""
    try:
        with shelve.open('orders.db', 'r') as db:
            orders = db.get('orders', {})
            logging.debug(f"Retrieved orders: {orders}")
            if orders:
                # Verify the first order has the required methods for debugging
                first_order = next(iter(orders.values()))
                logging.debug(f"First order attributes: {dir(first_order)}")
            return render_template('orders.html', orders=orders.values()) #renders order page with all orders
    except Exception as e:
        logging.error(f"Error in view_orders: {str(e)}")
        flash("Error viewing orders", "error")
        return redirect(url_for('home'))

@app.route('/order/<order_id>')
def view_order(order_id):
    """View a specific order"""
    try:
        with shelve.open('orders.db', 'r') as db:
            orders = db.get('orders', {}) # Get all orders
            order = orders.get(order_id) # Find specific order
            if order:
                return render_template('order_details.html', order=order, google_maps_api_key=GOOGLE_MAPS_API_KEY)
            flash("Order not found", "error")
    except Exception as e:
        logging.error(f"Error in view_order: {str(e)}", exc_info=True)
        flash("Error retrieving order", "error")
    return redirect(url_for('view_orders'))

@app.route('/order_confirmation/<order_id>') ## just display order dates, duration and ID
def order_confirmation(order_id):
    """Order confirmation page"""
    try:
        with shelve.open('orders.db', 'r') as db:
            orders = db.get('orders', {})
            order = orders.get(order_id)
            if order:
                return render_template('order_confirmation.html', order_id=order_id, order=order, google_maps_api_key=GOOGLE_MAPS_API_KEY)
            flash("Order not found", "error")
    except Exception as e:
        logging.error(f"Error in order_confirmation: {str(e)}", exc_info=True)
        flash("Error retrieving order details", "error")
    return redirect(url_for('home'))

@app.route('/order/<order_id>/edit', methods=['GET', 'POST'])
def edit_order(order_id):
    try:
        with shelve.open('orders.db', 'c') as db:# Open orders database in write mode
            orders = db.get('orders', {})
            order = orders.get(order_id)
            
            if request.method == 'POST': #new order date recieved via post request from forms
                # Convert string dates to datetime objects
                start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
                end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
                
                # Calculate new duration
                days = (end_date - start_date).days + 1
                
                # Update order details
                order.rental_dates['start_date'] = request.form['start_date']
                order.rental_dates['end_date'] = request.form['end_date']
                order.rental_dates['days'] = days
                
                # Update total based on new duration
                base_price = list(order.get_items().values())[0]['product'].get_price()
                order.total = base_price * days
                
                #save editted order
                orders[order_id] = order
                db['orders'] = orders
                flash("Order updated successfully")
                return redirect(url_for('view_order', order_id=order_id))
                
            return render_template('edit_order.html', order=order)
    except Exception as e:
        flash("Error updating order")
        return redirect(url_for('view_orders'))
    
@app.route('/order/<order_id>/delete', methods=['POST'])
def delete_order(order_id):
    try:
        with shelve.open('orders.db', 'c') as db: # write mode
            orders = db.get('orders', {}) # get all order
            if order_id in orders:
                del orders[order_id] # delete order
                db['orders'] = orders
                flash("Order deleted successfully")
            else:
                flash("Order not found")
        return redirect(url_for('view_orders'))
    except Exception as e:
        flash("Error deleting order")
        return redirect(url_for('view_orders'))
    

def find_nearest_carpark(latitude, longitude):
    """
    Find the nearest carpark to the given coordinates using a simple distance calculation.
    """
    if not latitude or not longitude:
        return None
        
    def calculate_distance(lat1, lng1, lat2, lng2):
        # Simple Euclidean distance - for more accuracy, you might want to use haversine formula
        return ((lat1 - lat2) ** 2 + (lng1 - lng2) ** 2) ** 0.5
    
    nearest_carpark = None
    min_distance = float('inf')
    
    for carpark_id, carpark_data in carparks.items():
        # Since your carpark data is in [name, lat, lng] format
        name = carpark_data[0]
        carpark_lat = carpark_data[1]
        carpark_lng = carpark_data[2]
        
        distance = calculate_distance(
            float(latitude),
            float(longitude),
            carpark_lat,
            carpark_lng
        )
        
        if distance < min_distance:
            min_distance = distance
            nearest_carpark = {
                'id': carpark_id,
                'name': name,
                'distance': distance,
                'coordinates': {'lat': carpark_lat, 'lng': carpark_lng}
            }
    
    return nearest_carpark

@app.route('/manage-ids', methods=['GET', 'POST'])
def manage_ids():
    form = BikeIDManagementForm()
    if form.validate_on_submit():
        try:
            with shelve.open('product.db', 'c') as product_db:
                products = product_db.get('products', {})
                bike_name = form.bike_name.data

                # Check if product exists, if not create
                existing_product = None
                for product in products.values():
                    if product.get_name() == bike_name:
                        existing_product = product
                        break

                if not existing_product:
                    new_product_id = len(products) + 1
                    new_product = Product(new_product_id, bike_name, 0, "", form.stock.data)
                    products[new_product_id] = new_product
                else:
                    existing_product._Product__stock += form.stock.data

                product_db['products'] = products

                # Regenerate bike IDs
                initialize_bike_ids(products)

                flash('Product and bike IDs updated successfully!', 'success')
                return redirect(url_for('manage_ids'))

        except Exception as e:
            logging.error(f"Error in manage_ids: {str(e)}")
            flash('Error processing request', 'error')

    if request.method == 'POST' and 'edit_bike_id' in request.form:
        try:
            old_bike_id = request.form.get('old_bike_id')
            new_bike_id = request.form.get('new_bike_id')

            with shelve.open('bike_ids.db', 'c') as db:
                bike_ids = db.get('bike_ids', {})

                if old_bike_id in bike_ids:
                    bike_info = bike_ids.pop(old_bike_id)
                    bike_ids[new_bike_id] = bike_info

                    db['bike_ids'] = bike_ids

                    flash(f"Bike ID updated from {old_bike_id} to {new_bike_id} successfully!", 'success')
                else:
                    flash("Old Bike ID not found.", 'error')

        except Exception as e:
            logging.error(f"Error updating bike ID: {str(e)}")
            flash('Error updating bike ID', 'error')

    try:
        bike_inventory = {}
        with shelve.open('bike_ids.db', 'r') as db:
            bike_ids = db.get('bike_ids', {})

        with shelve.open('product.db', 'r') as db:
            products = db.get('products', {})

        # Build inventory
        for product in products.values():
            product_name = product.get_name()
            bike_inventory[product_name] = {
                'stock': product.get_stock(),
                'rental': product.get_rental(),
                'ids': {
                    bike_id: {**bike_info, 'id': bike_id}  # Add the ID to the dictionary
                    for bike_id, bike_info in bike_ids.items()
                    if bike_info['name'] == product_name
                }
            }

    except Exception as e:
        bike_inventory = {}
        logging.error(f"Error retrieving bike IDs and products: {str(e)}")

    return render_template('manage_ids.html', form=form, bike_inventory=bike_inventory)

@app.route('/unlock', methods=['GET', 'POST'])
def unlock_bike():
    form = LockUnlockForm()
    if form.validate_on_submit():
        try:
            bike_id = form.bike_id.data.upper()
            user_email = session.get('user_email')
            
            if not user_email:
                flash('Please create an order first', 'error')
                return render_template('unlock.html', form=form)
            
            # Get bike ID data
            with shelve.open('bike_ids.db', 'c') as db:
                bike_ids = db.get('bike_ids', {})
                if bike_id not in bike_ids:
                    flash('Invalid bike ID', 'error')
                    return render_template('unlock.html', form=form)
                
                bike_info = bike_ids[bike_id]
                bike_name = bike_info['name']
            
            # Get product data and check stock
            with shelve.open('product.db', 'c') as db:
                products = db.get('products', {})
                product = None
                for p in products.values():
                    if p.get_name() == bike_name:
                        product = p
                        break
                
                if not product:
                    flash('Product not found', 'error')
                    return render_template('unlock.html', form=form)
                
                if product.get_stock() <= 0:
                    flash('No bikes available for this model', 'error')
                    return render_template('unlock.html', form=form)
            
            # Verify rental status
            with shelve.open('orders.db', 'r') as db:
                orders = db.get('orders', {})
                has_valid_rental = False
                for order in orders.values():
                    if (order.get_customer_info()['email'] == user_email and 
                        any(item['product'].get_name() == bike_name 
                            for item in order.get_items().values())):
                        has_valid_rental = True
                        break
                
                if not has_valid_rental:
                    flash('No active rental found for this bike', 'error')
                    return render_template('unlock.html', form=form)
            
            # Process unlock
            if bike_info['status'] == 'unlocked':
                flash('Bike is already unlocked', 'error')
                return render_template('unlock.html', form=form)
            
            # Update bike status
            with shelve.open('bike_ids.db', 'c') as db:
                bike_ids = db.get('bike_ids', {})
                bike_ids[bike_id]['status'] = 'unlocked'
                bike_ids[bike_id]['current_user'] = user_email
                db['bike_ids'] = bike_ids
            
            # Update product stock and rental count
            with shelve.open('product.db', 'c') as db:
                products = db.get('products', {})
                for p in products.values():
                    if p.get_name() == bike_name:
                        p.increase_rental()
                        break
                db['products'] = products
            
            flash('Bike unlocked successfully!', 'success')
            return redirect(url_for('lock_success'))
            
        except Exception as e:
            logging.error(f"Error in unlock_bike: {str(e)}")
            flash('Error processing request', 'error')
            
    return render_template('unlock.html', form=form)

@app.route('/lock', methods=['GET', 'POST'])
def lock_bike():
    form = LockUnlockForm()
    if form.validate_on_submit():
        try:
            bike_id = form.bike_id.data.upper()
            user_email = session.get('user_email')
            
            # Get bike ID data
            with shelve.open('bike_ids.db', 'c') as db:
                bike_ids = db.get('bike_ids', {})
                if bike_id not in bike_ids:
                    flash('Invalid bike ID', 'error')
                    return render_template('lock.html', form=form)
                
                bike_info = bike_ids[bike_id]
                bike_name = bike_info['name']
            
            # Get product data
            with shelve.open('product.db', 'c') as db:
                products = db.get('products', {})
                product = None
                for p in products.values():
                    if p.get_name() == bike_name:
                        product = p
                        break
                
                if not product:
                    flash('Product not found', 'error')
                    return render_template('lock.html', form=form)
            
            # Verify current user
            if bike_info['current_user'] != user_email:
                flash('You are not the current user of this bike', 'error')
                return render_template('lock.html', form=form)
            
            # Update bike status
            with shelve.open('bike_ids.db', 'c') as db:
                bike_ids = db.get('bike_ids', {})
                bike_ids[bike_id]['status'] = 'locked'
                bike_ids[bike_id]['current_user'] = None
                db['bike_ids'] = bike_ids
            
            # Update product stock 
            with shelve.open('product.db', 'c') as db:
                products = db.get('products', {})
                for p in products.values():
                    if p.get_name() == bike_name:
                        p.decrease_rental()
                        break
                db['products'] = products
            
            flash('Bike locked successfully!', 'success')
            return redirect(url_for('lock_success'))
            
        except Exception as e:
            logging.error(f"Error in lock_bike: {str(e)}")
            flash('Error processing request', 'error')
            
    return render_template('lock.html', form=form)

@app.route('/delete-id/<id_string>', methods=['POST'])
def delete_id(id_string):
    try:
        # Instead of deleting bike ID, reset its status
        with shelve.open('bike_ids.db', 'c') as db:
            bike_ids = db.get('bike_ids', {})
            if id_string in bike_ids:
                bike_ids[id_string]['status'] = 'available'
                bike_ids[id_string]['current_user'] = None
                db['bike_ids'] = bike_ids
                flash('Bike ID reset successfully!', 'success')
            else:
                flash('Bike ID not found', 'error')
    except Exception as e:
        logging.error(f"Error in delete_id: {str(e)}")
        flash('Error processing request', 'error')
        
    return redirect(url_for('manage_ids'))

@app.route('/lock-success')
def lock_success():
    return render_template('lock_success.html')


def initialize_orders():
    """Initialize the orders database if it doesn't exist"""
    try:
        with shelve.open('orders.db', 'c') as db:
            if 'orders' not in db:
                db['orders'] = {}
            logging.info("Orders database initialized successfully")
    except Exception as e:
        logging.error(f"Error initializing orders database: {e}")

def initialize_bike_ids(products):
    """Initialize bike IDs based on existing products"""
    try:
        with shelve.open('bike_ids.db', 'c') as db:
            bike_ids = {}
            for idx, product in enumerate(products.values(), 1):
                # Generate bike IDs based on product order
                bike_id = f"BIKE{idx:03d}"
                bike_ids[bike_id] = {
                    'name': product.get_name(),
                    'status': 'available',
                    'current_user': None
                }
            db['bike_ids'] = bike_ids
            logging.info("Bike IDs database initialized successfully")
    except Exception as e:
        logging.error(f"Error initializing bike IDs database: {e}")
        
@app.route('/check-session')
def check_session():
    email = session.get('user_email')
    return f"Current email in session: {email}"

# Add this to your if __name__ == '__main__': block
if __name__ == '__main__':
    initialize_products()
    initialize_orders()
    
    # Load products first before initializing bike IDs
    with shelve.open('product.db', 'r') as db:
        products = db.get('products', {})
        initialize_bike_ids(products)
    
    app.run(debug=True)

