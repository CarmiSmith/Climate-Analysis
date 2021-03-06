# Import 
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///hawaii.sqlite")
# Reflect database
Base = automap_base()
# Reflect tables
Base.prepare(engine, reflect=True)
# Variable for tables
Measurement = Base.classes.measurement

# Use flask to set up app to view data
app = Flask(__name__)

# Home route
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date/<start><br/>"
        f"/api/v1.0/startend/<start>/<end>"
    )



# Percipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session for API
    session = Session(engine)
    
    """Return a list of all prcp names."""
    # Query to retrieve the data and precipitation scores
    one_year_ago = dt.date(2017,8,18) - dt.timedelta(days=365)
    last_year = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date.desc()).all()

    #close session
    session.close()

    # Create a dictionary and retrieve data
    all_prcp = []
    for date, prcp in last_year:
        prcp_dict = {}
        prcp_dict[date] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)

# Stations route
@app.route("/api/v1.0/stations")
def stations():
    # Create our session for API
    session = Session(engine)

    # Query the database and get station names
    results = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()
    
    #close session
    session.close()

    # Convert to normal list
    all_station = list(np.ravel(results))
    
    return jsonify(all_station)

# Tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session for API
    session = Session(engine)
    
    # Get tobs and date from a year ago
    one_year_ago = dt.date(2017,8,18) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date.desc()).all()
    
    #close session
    session.close()

    # Create a dictionary and retrieve data
    all_tobs = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict[date] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

# Custom start to end route
@app.route("/api/v1.0/start_date/<start>")
def start_date(start):
    start = dt.datetime.strptime(start, '%Y-%m-%d')

    # Create our session for API
    session = Session(engine)

    # Query database
    results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    
    #close session
    session.close()

    # Create a dictionary and retrieve data
    t_normals = []
    for min_tobs, avg_tobs, max_tobs in results:
        temp_dict = {}
        temp_dict["Min TOBS"] = min_tobs
        temp_dict["AVG TOBS"] = avg_tobs
        temp_dict["MAX TOBS"] = max_tobs
        t_normals.append(temp_dict)
    
    return jsonify(t_normals)

# custom date range route
@app.route("/api/v1.0/startend/<start>/<end>")
def startend(start,end):
    start = dt.datetime.strptime(start, '%Y-%m-%d')
    end = dt.datetime.strptime(end, '%Y-%m-%d')

    # Create our session for API
    session = Session(engine)
   
    # Query to calculate TMIN, TAVG, and TMAX 
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    # Close session
    session.close()

    # Create a dictionary and retrieve data
    t_normals = []
    for min_tobs, avg_tobs, max_tobs in results:
        temp_dict = {}
        temp_dict["Min TOBS"] = min_tobs
        temp_dict["AVG TOBS"] = avg_tobs
        temp_dict["MAX TOBS"] = max_tobs
        t_normals.append(temp_dict)
    
    return jsonify(t_normals)

# Keeps flask running while open   
if __name__ == '__main__':
    app.run(debug=True)
