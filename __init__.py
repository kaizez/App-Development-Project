from flask import Flask, render_template, request, redirect, url_for
from Forms import CreateDefectForm, UpdateDefectForm
import shelve, createDefect

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/createDefect', methods=['GET', 'POST'])
def create_defect():
    create_defect_form = CreateDefectForm(request.form)
    if request.method == 'POST' and create_defect_form.validate():
        defects_dict = {}
        db = shelve.open('defect.db', 'c')

        try:
            defects_dict = db['Defects']
        except:
            print("Error in retrieving Defects from defect.db.")
            defects_dict = {}

        defect = createDefect.BikeDefect(
            create_defect_form.bike_id.data,
            create_defect_form.defect_type.data,
            create_defect_form.date_found.data,
            create_defect_form.bike_location.data,
            create_defect_form.severity.data,
            create_defect_form.description.data
        )
        defects_dict[defect.get_report_id()] = defect
        db['Defects'] = defects_dict
        db.close()

        return redirect(url_for('success'))
    return render_template('createDefect.html', form=create_defect_form)

@app.route('/success')
def success():
    return render_template('success.html')


@app.route('/updateDefect/<int:id>', methods=['GET', 'POST'])
def update_defect(id):
    update_defect_form = UpdateDefectForm(request.form)
    defects_dict = {}
    db = shelve.open('defect.db', 'r')
    try:
        defects_dict = db['Defects']
        defect = defects_dict.get(id)
        db.close()
    except:
        print("Error in retrieving Defects from defect.db.")
        return redirect(url_for('retrieve_defects'))

    if request.method == 'POST' and update_defect_form.validate():
        db = shelve.open('defect.db', 'w')
        try:
            defects_dict = db['Defects']
            defect = defects_dict.get(id)
            if defect:
                defect.set_status(update_defect_form.status.data)
                db['Defects'] = defects_dict
            db.close()
            return redirect(url_for('retrieve_defects'))
        except:
            print("Error updating defect status.")
            db.close()
            return redirect(url_for('retrieve_defects'))

    if defect:
        update_defect_form.status.data = defect.get_status()
        return render_template('updateDefect.html', form=update_defect_form, defect=defect)

    return redirect(url_for('retrieve_defects'))


@app.route('/retrieveDefect')
def retrieve_defects():
    defects_dict = {}
    try:
        db = shelve.open('defect.db', 'r')
        defects_dict = db['Defects']
        db.close()
    except:
        print("Error in retrieving Defects from defect.db.")

    defects_list = []
    for key in defects_dict:
        defect = defects_dict.get(key)
        defects_list.append(defect)

    return render_template('retrieveDefect.html', defects_list=defects_list, count=len(defects_list))


@app.route('/deleteDefect/<int:id>', methods=['POST'])
def delete_defect(id):
    defects_dict = {}
    db = shelve.open('defect.db', 'w')
    try:
        defects_dict = db['Defects']
        if id in defects_dict:  # Check if report ID exists
            defects_dict.pop(id)
            db['Defects'] = defects_dict
        db.close()
    except Exception as e:
        print(f"Error in retrieving Defects from defect.db: {e}")
        db.close()

    return redirect(url_for('retrieve_defects'))

@app.route('/admin')
def admin():
    return render_template('admin.html')


if __name__ == '__main__':
    app.run(debug=True)