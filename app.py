from flask import Flask, render_template, request, redirect, url_for, session
from flask_pymongo import PyMongo
from bson import json_util

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/materials_database"
mongo = PyMongo(app)

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)

@app.route('/submit_material', methods=['GET', 'POST'])
def submit_material():
    # Fetch attribute types for the form dropdown
    attribute_types = list(mongo.db.attribute_types.find())

    if request.method == 'POST':
        material_data = {
            'name': request.form['name'],
        }

        # Handle scalar fields
        scalar_labels = request.form.getlist('scalarLabel[]')
        scalar_values = request.form.getlist('scalarValue[]')
        for label, value in zip(scalar_labels, scalar_values):
            material_data[label] = value

        # Handle 2D array fields
        axis_names_1 = request.form.getlist('axisName1[]')
        axis_names_2 = request.form.getlist('axisName2[]')
        dynamic_values = request.form.getlist('dynamicField[]')

        for axis_name1, axis_name2, value_pairs in zip(axis_names_1, axis_names_2, dynamic_values):
            pairs = [pair.split(',') for pair in value_pairs.split(';') if pair]
            material_data[axis_name1] = {
                'axis_name': axis_name2,
                'values': pairs
            }

        # Extract all attribute names
        all_attribute_names = set(scalar_labels + axis_names_1 + axis_names_2)

        # Check for new attribute names and add them to the database
        existing_attribute_names = {attr['name'] for attr in attribute_types}
        new_attributes = all_attribute_names - existing_attribute_names
        for attr in new_attributes:
            if attr and attr != "new":
                mongo.db.attribute_types.insert_one({'name': attr})

        mongo.db.materials.insert_one(material_data)
        return redirect(url_for('index'))

    attribute_types_serializable = json_util.dumps(attribute_types)
    return render_template('submit_material.html', attribute_types=attribute_types_serializable)


