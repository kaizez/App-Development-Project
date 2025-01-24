from flask import Flask, render_template, request, redirect, url_for, flash
from BikeForm import CreateBikeForm
import shelve
import folium
import gpxpy
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def extract_gpx_details(gpx_file_path):
    try:
        with open(gpx_file_path, 'r') as gpx_file:
            gpx = gpxpy.parse(gpx_file)

        total_distance = 0
        start_time = None
        end_time = None
        carbon_emission_factor = 0.1  # kg CO2 per km

        for track in gpx.tracks:
            for segment in track.segments:
                for i in range(len(segment.points) - 1):
                    point1 = segment.points[i]
                    point2 = segment.points[i + 1]

                    # Calculate distance between points
                    total_distance += point1.distance_3d(point2)

                # Capture start and end time
                if segment.points:
                    if not start_time:
                        start_time = segment.points[0].time
                    end_time = segment.points[-1].time

        # Calculate total duration in hours
        if start_time and end_time and start_time < end_time:
            total_time = (end_time - start_time).total_seconds() / 3600  # Hours
        else:
            total_time = 0

        # Calculate average speed (safe check for zero time)
        # Only consider the first `speed` or `extensions` entry for speed, if available.
        avg_speed = sum([point.speed for point in segment.points if point.speed]) / len(segment.points) if segment.points else 0

        # Convert distance to kilometers
        total_distance_km = total_distance / 1000

        # Calculate total carbon emissions
        total_carbon_emissions = total_distance_km * carbon_emission_factor

        print(f"Total distance: {total_distance_km} km, Total time: {total_time} hours, Average speed: {avg_speed} km/h")

        return {
            "total_distance": round(total_distance_km, 2),
            "avg_speed": round(avg_speed, 2),
            "duration": f"{int(total_time)} hours {int((total_time % 1) * 60)} mins" if total_time > 0 else "N/A",
            "carbon_emissions": round(total_carbon_emissions, 2)
        }
    except Exception as e:
        print(f"Error processing GPX file: {e}")
        return {"total_distance": 0, "avg_speed": 0, "duration": "N/A", "carbon_emissions": 0}

def generate_svg_points(gpx_file_path):
    try:
        with open(gpx_file_path, 'r') as gpx_file:
            gpx = gpxpy.parse(gpx_file)

        route_coordinates = [
            (point.latitude, point.longitude)
            for track in gpx.tracks
            for segment in track.segments
            for point in segment.points
        ]

        min_lat = min(coord[0] for coord in route_coordinates)
        max_lat = max(coord[0] for coord in route_coordinates)
        min_lon = min(coord[1] for coord in route_coordinates)
        max_lon = max(coord[1] for coord in route_coordinates)

        width_scale = 200  # Adjust scaling factor
        height_scale = 150  # Adjust scaling factor

        svg_points = " ".join([
            f"{((lon - min_lon) / (max_lon - min_lon) * width_scale)},{(max_lat - lat) / (max_lat - min_lat) * height_scale}"
            for lat, lon in route_coordinates
        ])
        return svg_points
    except Exception as e:
        print(f"Error generating SVG points: {e}")
        return ""


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/createBike', methods=['GET', 'POST'])
def create_bike():
    create_bike_form = CreateBikeForm(request.form)

    if request.method == 'POST' and create_bike_form.validate():
        db = shelve.open('bike.db', 'c')
        bikes_dict = db.get('Bikes', {})

        file = request.files.get('upload_bike_image')
        filename = ''
        if file and file.filename != '':
            from werkzeug.utils import secure_filename
            filename = secure_filename(file.filename)
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        bike_id = len(bikes_dict) + 1
        bike_data = {
            "bike_id": bike_id,
            "bike_name": create_bike_form.bike_name.data,
            "upload_bike_image": filename,
            "price": float(create_bike_form.price.data),
            "transmission_type": create_bike_form.transmission_type.data,
            "seating_capacity": create_bike_form.seating_capacity.data,
            "engine_output": create_bike_form.engine_output.data,
            "stock_quantity": int(create_bike_form.stock_quantity.data),
        }

        bikes_dict[bike_id] = bike_data
        db['Bikes'] = bikes_dict
        db.close()

        flash("Bike created successfully!", "success")
        return redirect(url_for('retrieve_bikes'))
    return render_template('createBike.html', form=create_bike_form)


@app.route('/retrieveBikes')
def retrieve_bikes():
    db = shelve.open('bike.db', 'c')
    bikes_dict = db.get('Bikes', {})
    db.close()

    converted_bikes_dict = {
        bike_id: bike if isinstance(bike, dict) else bike.__dict__
        for bike_id, bike in bikes_dict.items()
    }
    return render_template('retrieveBikes.html', count=len(converted_bikes_dict), bikes=converted_bikes_dict)


@app.route('/updateBike/<int:id>/', methods=['GET', 'POST'])
def update_bike(id):
    update_bike_form = CreateBikeForm(request.form)

    # Open the database
    with shelve.open('bike.db', 'c') as db:
        bikes_dict = db.get('Bikes', {})
        bike = bikes_dict.get(id)

        if not bike:
            flash("Bike not found.", "error")
            return redirect(url_for('retrieve_bikes'))

        if request.method == 'POST' and update_bike_form.validate():
            # Update bike details
            bike["bike_name"] = update_bike_form.bike_name.data
            bike["price"] = float(update_bike_form.price.data)
            bike["transmission_type"] = update_bike_form.transmission_type.data
            bike["seating_capacity"] = update_bike_form.seating_capacity.data
            bike["engine_output"] = update_bike_form.engine_output.data
            bike["stock_quantity"] = int(update_bike_form.stock_quantity.data)

            # Handle image upload
            file = request.files.get('upload_bike_image')
            if file and file.filename != '':
                # Remove old image if it exists
                old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], bike.get("upload_bike_image", ""))
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)

                # Save new image
                from werkzeug.utils import secure_filename
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                bike["upload_bike_image"] = filename

            # Save updated bike to the database
            bikes_dict[id] = bike
            db['Bikes'] = bikes_dict

            flash("Bike updated successfully!", "success")
            return redirect(url_for('retrieve_bikes'))

        # Pre-fill the form with existing bike details
        update_bike_form.bike_name.data = bike["bike_name"]
        update_bike_form.price.data = bike["price"]
        update_bike_form.transmission_type.data = bike["transmission_type"]
        update_bike_form.seating_capacity.data = bike["seating_capacity"]
        update_bike_form.engine_output.data = bike["engine_output"]
        update_bike_form.stock_quantity.data = bike["stock_quantity"]

    return render_template('updateBikes.html', form=update_bike_form, bike=bike)


@app.route('/viewBikes')
def view_bikes():
    db = shelve.open('bike.db', 'r')
    bikes_dict = db.get('Bikes', {})
    db.close()

    return render_template('viewBikes.html', count=len(bikes_dict), bikes=bikes_dict)


@app.route('/deleteBike/<int:id>/', methods=['POST'])
def delete_bike(id):
    db = shelve.open('bike.db', 'c')
    bikes_dict = db.get('Bikes', {})

    if id in bikes_dict:
        del bikes_dict[id]
        db['Bikes'] = bikes_dict
        flash("Bike deleted successfully!", "success")
    else:
        flash("Bike not found.", "error")

    db.close()
    return redirect(url_for('retrieve_bikes'))

@app.route('/dashBoard', methods=['GET'])
def dashboard():
    # Load data from persistent storage
    with shelve.open('dashboard_data.db') as db:
        gpx_details = db.get('gpx_details', {"total_distance": 0, "avg_speed": 0, "carbon_emissions": 0, "duration": 0})
        bike_count = db.get('bike_count', 0)

    # Generate SVG points based on the last GPX file uploaded (if available)
    gpx_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'latest.gpx')
    if os.path.exists(gpx_file_path):
        svg_points = generate_svg_points(gpx_file_path)
    else:
        svg_points = ""

    # Weekly Leaderboard Data
    leaderboard = [
        {"name": "Jun Hao", "change": "up", "avatar": "J", "color": "#ff9aa2"},
        {"name": "Bryce", "change": "up", "avatar": "B", "color": "#9bcdf8"},
        {"name": "Rais", "change": "up", "avatar": "R", "color": "#c2c7ff"},
        {"name": "Wei Kiat", "change": "down", "avatar": "W", "color": "#d6d8db"}
    ]

    # Render the normal dashboard
    return render_template(
        'dashBoard.html',
        svg_points=svg_points,
        total_emissions=gpx_details["carbon_emissions"],
        bike_count=bike_count,
        total_miles=gpx_details["total_distance"],
        avg_speed=gpx_details["avg_speed"],
        duration=gpx_details["duration"],
        leaderboard=leaderboard
    )

import math

@app.route('/dashBoardAdmin', methods=['GET', 'POST'])
def dashboard_admin():
    # Initialize default values
    gpx_details = {"total_distance": 0, "avg_speed": 0, "carbon_emissions": 0, "duration": 0.0}
    bike_increment = 1  # Increment bike count by 1 for each upload

    if request.method == 'POST':
        gpx_file = request.files.get('gpx_file')

        with shelve.open('dashboard_data.db') as db:
            # Ensure keys exist in storage
            if 'gpx_details' not in db:
                db['gpx_details'] = gpx_details
            if 'bike_count' not in db:
                db['bike_count'] = 0

            if gpx_file and gpx_file.filename.endswith('.gpx'):
                gpx_upload_path = os.path.join(app.config['UPLOAD_FOLDER'], 'latest.gpx')  # Save as 'latest.gpx'
                gpx_file.save(gpx_upload_path)

                # Extract GPX details and update cumulative data
                new_gpx_details = extract_gpx_details(gpx_upload_path)

                # Parse the duration string safely
                duration_str = new_gpx_details.get('duration', "0 hours 0 mins")
                try:
                    # Extract hours and minutes from the string
                    hours = int(duration_str.split('hours')[0].strip())
                    minutes = int(duration_str.split('hours')[1].split('mins')[0].strip())
                    total_hours = hours + (minutes / 60)  # Convert to total hours
                    new_duration = math.ceil(total_hours)  # Round up to the nearest hour
                except (ValueError, IndexError):
                    new_duration = 0.0  # Default to 0 if parsing fails

                # Ensure `duration` is stored as a float
                current_gpx_details = db['gpx_details']
                try:
                    current_duration = float(current_gpx_details.get('duration', 0.0))
                except ValueError:
                    current_duration = 0.0  # Reset to 0.0 if the existing value is invalid

                current_gpx_details['duration'] = current_duration + new_duration
                current_gpx_details['total_distance'] += new_gpx_details['total_distance']
                current_gpx_details['avg_speed'] = (
                    (current_gpx_details['avg_speed'] + new_gpx_details['avg_speed']) / 2
                )
                current_gpx_details['carbon_emissions'] += new_gpx_details['carbon_emissions']
                db['gpx_details'] = current_gpx_details  # Save back to shelve

                # Increment bike count
                db['bike_count'] += bike_increment
                flash(f"GPX file '{gpx_file.filename}' uploaded and processed successfully!", "success")
            else:
                flash("Invalid file type. Please upload a valid GPX file.", "error")

    # Load data to render the admin dashboard
    with shelve.open('dashboard_data.db') as db:
        gpx_details = db.get('gpx_details', {"total_distance": 0, "avg_speed": 0, "carbon_emissions": 0, "duration": 0.0})
        bike_count = db.get('bike_count', 0)

    return render_template(
        'dashBoardAdmin.html',
        gpx_details=gpx_details,
        bike_count=bike_count
    )
@app.route('/resetDashboard', methods=['POST'])
def reset_dashboard():
    # Path to the shelve database
    shelve_path = 'dashboard_data.db'

    # Reset the shelve database
    with shelve.open(shelve_path, writeback=True) as db:
        db.clear()  # Clear all existing data
        db['gpx_details'] = {
            "total_distance": 0,
            "avg_speed": 0,
            "carbon_emissions": 0,
            "duration": 0.0
        }
        db['bike_count'] = 0

    flash("Dashboard has been reset to default values.", "success")
    return redirect('/dashBoardAdmin')


if __name__ == '__main__':
    app.run(debug=True)
