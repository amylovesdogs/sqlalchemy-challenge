#################################################
# Import Libraries
#################################################

# date/time functions
from time import strptime
from dateutil.relativedelta import relativedelta
from datetime import date

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import desc

# flask app
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite?check_same_thread=False")
# reflect an existing database into a new model
# Create the inspector and connect it to the engine
Base = automap_base()
Base.prepare(autoload_with=engine)

# reflect the tables
# View all of the classes that automap found
classes = Base.classes.keys()
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(bind=engine)

#################################################
# Data Functions
#################################################
# Return the most recent measurement date
# Returns a date in string format
def most_recent_date(station=None):
    if station==None:
        most_recent = session.query(Measurement).order_by(desc('date')).first()
    else:
        most_recent = session.query(Measurement).order_by(desc('date')).\
            filter(Measurement.station == station).first()
    return most_recent.date

# Return the start date of the 12 months ending on the given end date
# end_date_str is a string of the format YYYY-MM-DD
# Returns a datetime object
def get_start_date(end_date_str):
    end_date_parsed = strptime(end_date_str, "%Y-%m-%d")
    end_date_dt = date(end_date_parsed.tm_year, end_date_parsed.tm_mon, end_date_parsed.tm_mday)
    return end_date_dt - relativedelta(months=12)

# Return the last 12 months of precipitation data preceeding the end date for all stations
# Returned data is a dictionary
def precip_year(end_date):

    start_date = get_start_date(end_date)

    # Perform a query to retrieve the precipitation measurements
    return dict(session.query(Measurement.date,Measurement.prcp).\
            filter(Measurement.date >= start_date).all())

# Return the most active weather station
def most_active_station():
    activity = session.query(Measurement.station,func.count(Measurement.station)).\
            group_by(Measurement.station).\
            order_by(func.count(Measurement.station).desc()).all()
    return activity[0][0]

# Return temperature data at the given station, for the 12 months preceding the end date
# Returned data is a dictionary
def temperature_year(end_date,station):
     # Calculate the start date
    start_date = get_start_date(end_date)

    # Perform a query to retrieve the temperature measurements
    return dict(session.query(Measurement.date,Measurement.tobs).\
            filter(Measurement.station == station).\
                   filter(Measurement.date >= start_date).all())

# Return max, min and avg temperatures at the given station for the time period specified
# If no end date is given, return stats based on all data from the start date
# Returned data is a dictionary
def temperature_stats(start_date, end_date=None, station=None):
    filters = [Measurement.date >= start_date]
    if end_date != None:
        filters.append(Measurement.date <= end_date)
    if station != None:
        filters.append(Measurement.station == station)

    temp_stats = session.query(func.avg(Measurement.tobs).label('average'),
                               func.max(Measurement.tobs).label('high'),
                               func.min(Measurement.tobs).label('low')).\
                                filter(*filters)
    return {'low': temp_stats[0].low,
            'high': temp_stats[0].high,
            'avg': "{:.2f}".format(temp_stats[0].average)}

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Home Page, documents the routes
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Weather API!<br/>"
        f"Available Routes:<br/>"
        f"<b>/api/v1.0/precipitation</b>   Returns the last 12 months of precipitation data<br/>"
        f"<b>/api/v1.0/stations</b>        Returns a list of the weather statinos<br/>"
        f"<b>/api/v1.0/tobs</b>            Returns the the last 12 months of temperature data for the most active weather station<br/>"
        f"<b>/api/v1.0/YYYY-MM-DD</b>       Returns the minimum, maximum and average temperature for the time period starting with the given date<br/>"
        f"<b>/api/v1.0/YYYY-MM-DD/YYYY-MM-DD</b>   Returns the minimum, maximum and average temperature for the time period specified by the start and end dates<br/>"
    )

# Return the last year of precipitation data
@app.route("/api/v1.0/precipitation")
def precipitation():
    return jsonify(precip_year(most_recent_date()))

# Return a list of all the stations
@app.route("/api/v1.0/stations")
def stations():
    query = session.query(Station.id, Station.station).distinct()
    return jsonify(dict(query))

# Return the last year of temperature data for the most active weather station
@app.route("/api/v1.0/tobs")
def tobs():
    station = most_active_station()
    end_date = most_recent_date(station)
    temp_dict = temperature_year(end_date,station)
    return jsonify(temp_dict)

# Return the minimum temperature, the average temperature, and the maximum temperature
# for the time period starting with the specified start date and ending with the
# most recent data
# expected date format is YYYY-MM-DD
@app.route("/api/v1.0/<start_date>")
def tobs_by_start_date(start_date):
    # using try-except for verifying and converting the date
    try:
        # convert date string to date object
        start_date_parsed = strptime(start_date, "%Y-%m-%d")

    # If the date validation fails
    except ValueError:
        # return an error message
        return jsonify({'input': start_date,'error':"Incorrect date format, should be YYYY-MM-DD"})

    # Input date format is verified, return the requested data
    start_date_dt = date(start_date_parsed.tm_year, start_date_parsed.tm_mon, start_date_parsed.tm_mday)
    return jsonify(temperature_stats(start_date_dt))

# Return the minimum temperature, the average temperature, and the maximum temperature
# for the time period starting with the specified start date and ending with the
# the specified end date
# expected date format is YYYY-MM-DD
@app.route("/api/v1.0/<start_date>/<end_date>")
def tobs_by_date_range(start_date, end_date):

    # using try-except for verifying and converting the start date
    try:
        # convert date string to date object
        start_date_parsed = strptime(start_date, "%Y-%m-%d")

    # If the date validation fails
    except ValueError:
        # return an error message
        return jsonify({'start date': start_date,'error':"Incorrect date format, should be YYYY-MM-DD"})

    # using try-except for verifying and converting the end date
    try:
        # convert date string to date object
        end_date_parsed = strptime(end_date, "%Y-%m-%d")

    # If the date validation fails
    except ValueError:
        # return an error message
        return jsonify({'end date': end_date,'error':"Incorrect date format, should be YYYY-MM-DD"})

    start_date_dt = date(start_date_parsed.tm_year, start_date_parsed.tm_mon, start_date_parsed.tm_mday)
    end_date_dt = date(end_date_parsed.tm_year, end_date_parsed.tm_mon, end_date_parsed.tm_mday)

    # basic sanity check on dates
    if end_date_dt < start_date_dt:
        return jsonify({'start_date':start_date,'end date': end_date,'error': "End date can't precede start date."})

    # Input dates are verified, return the requested data
    return jsonify(temperature_stats(start_date_dt, end_date_dt))

#################################################
# Run the Application
#################################################
if __name__ == '__main__':
    app.run(debug=True)
