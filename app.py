#################################################
# Import Dependencies
#################################################

import datetime as dt
import numpy as np
from dateutil.relativedelta import relativedelta

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement=Base.classes.measurement
Station=Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2017-01-01<br/>"
        f"/api/v1.0/2017-01-01/2017-01-10"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    # Create our session (link) to the DB
    session = Session(engine)

    # Calculate the date 1 year ago from the last data point in the database

    #Find max value of date in the database
    result=session.query(Measurement).order_by(Measurement.date.desc()).first()
    last_date=result.date
    
    #Calculate the date 1 year from max date
    year_ago=(dt.datetime.strptime(last_date, '%Y-%m-%d') - relativedelta(years=1)).date()
    #print(year_ago)


    # Perform a query to retrieve the date and precipitation scores
    data=session.query(Measurement.date,Measurement.prcp)\
    .filter(Measurement.date>=year_ago)\
    .filter(Measurement.date<=last_date).all()

    #Close session after use
    session.close()

    # Convert list of tuples into dictionary with date as id and precipitation quantity as value
    precp_dict=dict(data)

    return jsonify(precp_dict)

@app.route("/api/v1.0/stations")
def station():
    # Create our session (link) to the DB
    session = Session(engine)

    #List of unique stations
    station_count=session.query(Station.name).filter(Measurement.station == Station.station).distinct().all()

    #dictionary to store name and count of occurrence
    station={}
    station["name"]=[]

    #Assign values to each staion based on query result
    for row in station_count:
        station["name"].append(row[0])

    #Close session after use
    session.close()

    return jsonify(station)

@app.route("/api/v1.0/tobs")
def tobs_data():
    
    # Create our session (link) to the DB
    session = Session(engine)

    # Find the station with most records in last one year
    #Find max value of date in the database
    result=session.query(Measurement).order_by(Measurement.date.desc()).first()
    last_date=result.date
    
    #Calculate the date 1 year from max date
    year_ago=(dt.datetime.strptime(last_date, '%Y-%m-%d') - relativedelta(years=1)).date()
    #print(year_ago)

    #Find station with most number of records
    
    query=session.query(Measurement).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()
    most_active_station=query.station
    # Perform a query to retrieve the date and tobs value for most active station
    data=session.query(Measurement.date,Measurement.tobs).filter(Measurement.station==most_active_station)\
    .filter(Measurement.date>=year_ago).filter(Measurement.date<=last_date)\
    .all()

    #Close session after use
    session.close()

    # Convert list of tuples into dictionary with date as id and tobs as value
    station_date_tobs=dict(data)
    return jsonify(station_date_tobs)

"""
@app.route("/api/v1.0/<start>")
def stats_start(start):

    # Create our session (link) to the DB
    session = Session(engine)

    #Find min, average and max temperature observation for dates equal to greater than start date passed in the API
    data=session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs))\
    .filter(func.strftime("%Y-%m-%d", Measurement.date) >=start)\
    .all()
 
    #Close session after use
    session.close()

    stats_start_dict={}
    #dict(data)

    for row in data:
        stats_start_dict["Min_temp"]=row[0]
        stats_start_dict["Avg_temp"]=row[1]
        stats_start_dict["Max_temp"]=row[2]
    
    return jsonify(stats_start_dict)
"""
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats_Start_end(start,end=None):
    
    # Create our session (link) to the DB
    session = Session(engine)

    #Find min, average and max temperature observation for dates equal to greater than start date passed in the API
    if end!=None:
        data=session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs))\
        .filter(func.strftime("%Y-%m-%d", Measurement.date) >=start)\
        .filter(func.strftime("%Y-%m-%d", Measurement.date) <=end)\
        .all()
    else:
        #Find min, average and max temperature observation for dates equal to greater than start date passed in the API
        data=session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs))\
        .filter(func.strftime("%Y-%m-%d", Measurement.date) >=start)\
        .all()

    #Close session after use
    session.close()

    stats_start_end_dict={}
    #dict(data)

    for row in data:
        stats_start_end_dict["Min_temp"]=row[0]
        stats_start_end_dict["Avg_temp"]=row[1]
        stats_start_end_dict["Max_temp"]=row[2]
    
    return jsonify(stats_start_end_dict)


if __name__ == "__main__":
    app.run(debug=True)