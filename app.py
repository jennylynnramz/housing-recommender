# Dependencies
from flask import Flask, render_template, request, redirect
import pandas as pd
import the_magic
import time
import os

# Create instance of Flask app
app = Flask(__name__)

# Database Setup
from flask_sqlalchemy import SQLAlchemy
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', '')
#app.py change db uri to local
# db_username = "jennylynnramz"
# db_password = "catcatapricot"
# dbname = "database1"
# endpoint = "database1.cmrlzk1tjuhz.us-west-1.rds.amazonaws.com"

db_username = "postgres"
db_password = "postgres"
dbname = "housing_rec"
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{db_username}:{db_password}@localhost:5433/{dbname}"

# Remove tracking modifications
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


# Connects to the database using the app config
db = SQLAlchemy(app)


# #####################

class Input_Results(db.Model):
    __tablename__ = 'input_results'

    # id = db.Column(db.Integer, primary_key=True)
    user_input = db.Column(db.String, primary_key=True)
    results = db.Column(db.String)

    def __repr__(self):
        return str(user_input) + " :: <br><br>" + str(results)


#######################
# from models import Input_Results

# print(input_results)

# Route that renders the welcome page and receives user inputs
@app.route("/", methods=["GET", "POST"])
def user_inputs():
    app.logger.debug('user_inputs() called.')

    if request.method == "POST":
        post_start_time = time.perf_counter()
        app.logger.debug('POST request received.')
        req = request.form

        summer_temp = req["summer-temp"]
        winter_temp = req["winter-temp"]
        city_size = req["city-size"]
        house_size = req["house-size"]
        budget = req["budget"]
        bedrooms = req["bedrooms"]
        bathrooms = req["bathrooms"]
        yard = req["yard"]
        # Array of user inputs
        input_array = [summer_temp, winter_temp, city_size, house_size, budget, bedrooms, bathrooms, yard]
        
        print(f"""
            Form submitted:\n
            Summer Temp: {summer_temp}\n
            Winter Temp: {winter_temp}\n
            City Size: {city_size}\n
            House Size: {house_size}\n
            Budget: {budget}\n
            Bedrooms: {bedrooms}\n
            Bathrooms: {bathrooms}\n
            Yard: {yard}\n 
            """)

        hot_code(input_array)

        return check_database(input_array, db, post_start_time)
    
    else:
        return render_template("index.html")

###########################
#Checking to see if inputted user data matches anything already tested:
def check_database(input_array, db, post_start_time):

    try:
        results = db.session.query(Input_Results.results).filter(Input_Results.user_input == str(input_array)).first()
        if results != None:
            return recreate_previous(input_array, results)
        else:
            print("Checked database, no match was found")
            return find_new_results(input_array, db, post_start_time)

    except Exception as e:
        print("something broke inside of check_database")
        print(e)
        

def recreate_previous(input_array, results):
    print(input_array)
    # print(results)
    print("This might be it")

    print(type(results))
    mytable = str(results).replace("('", "").replace("',)", "").replace("\\n", "")
    # mytable = results.replace("(", "")
    # mytable = (results.rstrip("\n"))



    return render_template('display_results.html', table=mytable)


def find_new_results(input_array, db, post_start_time):

    get_table_data = the_magic.make_prediction(input_array, db)
    mytable = get_table_data.to_html(classes="results table table-striped")
    
    # TIMER TO TRACK EFFICIENCY
    post_end_time = time.perf_counter()
    time_spent_processing_post_request = post_end_time - post_start_time
    app.logger.debug("Spent " + str(time_spent_processing_post_request) + " seconds processing POST.")

    # DATABASE
    the_input_results = Input_Results(user_input=str(input_array), results=mytable)
    db.session.add(the_input_results)
    db.session.commit()

    return render_template('display_results.html',  table=mytable , titles=get_table_data.columns.values)

        
def hot_code(input_array):
    if input_array[2] == "Small Town":
        input_array[2] = 0
    elif input_array[2] == "Medium City":
        input_array[2] = 1
    else:
        input_array[2] = 2

        # Yard Size
    if input_array[7] == "Yes":
        input_array[7] = 1
    else:
        input_array[7] = 0
            
    print(f"""
        Hot Coded array:\n
        Summer Temp: {input_array[0]}\n
        Winter Temp: {input_array[1]}\n
        City Size: {input_array[2]}\n
        House Size: {input_array[3]}\n
        Budget: {input_array[4]}\n
        Bedrooms: {input_array[5]}\n
        Bathrooms: {input_array[6]}\n
        Yard: {input_array[7]}\n 
        """)

    return(input_array)
        

if __name__ == "__main__":
    app.run(debug=True)