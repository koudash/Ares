# flask toolkits
from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

# Create app and pass __name__
app = Flask(__name__)

# Use flask_pymongo to set up mongo connection
app.config['MONGO_URI'] = 'mongodb://localhost:27017/Mars_app'
mongo = PyMongo(app)

# >>> ROUTE 1 <<< #
# Define actions for the index route
@app.route('/')
def index():

    # Retrieve the latest Mars data from "Mars_app" Mongo database
    mars_data = mongo.db.html_update_history.find_one(sort=[('Data_Retrv_D&T', -1)])

    #  Pass Mars data to 'index.html' for display
    return render_template('index.html', mars_data=mars_data)
# >>>>>>>>>>> I AM A ROUTE SEPARATOR <<<<<<<<<<< #    

# >>> ROUTE 2 <<< #
# Define actions for "scrape" route
@app.route('/scrape')
def scrape():
    
    # Retrieve web scrapting data for Mars
    mars_fact = scrape_mars.scrape()

    # Insert into rather than update with the newly retrieved data in Mongo DB
    # Note that data are saved with local date&time to keep track of data scraping/HTML updating histories
    mongo.db.html_update_history.insert_one(mars_fact)

    # Redirect to "/" route after data entry in MongoDB 
    return redirect('/', code=302)
# >>>>>>>>>>> I AM A ROUTE SEPARATOR <<<<<<<<<<< #

# Execute the script
if __name__ == '__main__':
    app.run(debug=True)