# sqlalchemy-challenge
DU Data Analysis SQL Alchemy Challenge

## Part 1: Analyze and Explore the Climate Data
Data is stored in **Resources/hawaii.sqlite**, a sqllite database. Connected, loaded and mapped via SQL Alchemy.

### Precipitation Analysis
The following analysis is done:
1. Find the most recent date in the dataset.
2. Using that date, get the previous 12 months of precipitation data by querying the previous 12 months of data.
3. Select only the "date" and "prcp" values.
4. Load the query results into a Pandas DataFrame. Explicitly set the column names.
5. Sort the DataFrame values by "date".
6. Create a bar chart using the DataFrame plot method.
7. Use Pandas to print the summary statistics for the precipitation data.

### Station Analysis
The following analysis is done:
1. Query to calculate the total number of stations in the dataset.
2. Query to find the most-active stations (that is, the stations that have the most rows) by doing the following:
* List the stations and observation counts in descending order.
* Determine which station has the greatest number of observations.
3. In a single query, calculate the lowest, highest, and average temperatures that filters on the most-active station id found in the previous query.
4. Query to get the previous 12 months of temperature observation (TOBS) data by doing the following:
* Filter by the station that has the greatest number of observations.
* Query the previous 12 months of TOBS data for that station.
* Plot the results as a histogram with bins=12.

## Part 2: Climate App with Flask
