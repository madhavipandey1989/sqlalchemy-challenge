# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new modelpwd

Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
Base.metadata.tables
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


def find1YearOldDateFromMostRecentRecord(session):
    # Find the most recent date in the data set.
    most_recent = session.query(Measurement.date, func.max(Measurement.date)).first()[0]
    # Design a query to retrieve the last 12 months of precipitation data and plot the results. 
    # Starting from the most recent data point in the database. 
    most_recent_date = dt.datetime.strptime(most_recent, '%Y-%m-%d')
    # Calculate the date one year from the last date in data set.
    prev_year = most_recent_date - dt.timedelta(days=365)

    return prev_year



@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Find 1 year date from last record
    prev_year = find1YearOldDateFromMostRecentRecord(session)

    # Perform a query to retrieve the data and precipitation scores
    # Get the data from DB for last 1 year for columns o date and prcp.
    precip_scores = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).all()
    
    resultDict = {}
    #Loop the rows and convert to dictionary
    for date, prcp in precip_scores:
        resultDict[str(date)] = prcp

    #close the session with db
    session.close()
    # Convert dictionaly to Jason and return
    return jsonify(resultDict)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # List all stations from query.
    stationsRows = session.query(Station.station).all()
    
    stationsList = []
    #Loop through rows to get Station names
    for station in stationsRows:
        stationsList.append(station[0])

    #close the session with db
    session.close()
    # Convert list to Jason and return as results
    return jsonify(stationsList)



@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Find 1 year date from last record
    prev_year = find1YearOldDateFromMostRecentRecord(session)

    # Get the data from DB for last 1 year for columns o date and prcp.
    tobs_rows = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= prev_year)\
        .filter(Measurement.station == 'USC00519281').all()
    
    tobsDict = {}
    #Loop the rows and convert to list
    for date, tobs in tobs_rows:
        tobsDict[date] = tobs

    #close the session with db
    session.close()
    # Convert dictionaly to Jason and return
    return jsonify(tobsDict)


# defined 2 paths, and end parameter as optional.
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperatures(start, end=''):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # if end parameter is defined, consider in additional filter, otherwise apply filter based on start date provided. 
    # Calculate Min, Max and Avg Tenperature for given date range
    if(end!=''):
        rowsGreaterThanStartDate = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start, Measurement.date <= end).all()
    else:
        rowsGreaterThanStartDate = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    # convert result in dictionary
    tobsDict = {}
    tobsDict['Min Temp'] = rowsGreaterThanStartDate[0][0]
    tobsDict['Max Temp'] = rowsGreaterThanStartDate[0][1]
    tobsDict['Avg Temp'] = rowsGreaterThanStartDate[0][2]

    #close the session with db
    session.close()
    # Convert dictionary to Jason and return
    return jsonify(tobsDict)




if __name__ == '__main__':
    app.run(debug=True)