# greenhouse-gas-visualization

This repository contains code written to create interactive visualizations for data from several greenhouse gas (GHG) monitors located across the United States. The purpose of this project was to upgrade the type of visualizations a research team at Lawrence Berkeley Lab was previously using (static JPEG images containing months of data at a time, highly illegible) to make them customizable and interactive.

There are three types of GHG-monitoring systems set up for this project: AOSGHG, AMC and PGS. Their graphs require different formats, so each system has a different
file in which parameters (i.e. number of variables to be displayed, time period to be displayed, etc.) are specified.

The descriptions and details of all the files are documented within the files themselves.

The files work as such:

loop.py --> Parameters_[system].py --> onePlotAll.py --> figure.py --> onePlotAll.py --> plot.html

The output of this project can be viewed here: http://arm.lbl.gov/pecsview/salil/ (you need to select a variable from the dropdown menu to see the plot). There were additional bash scripts to automate fetching the data from servers and running these files to automatically generate new plots each month for each system; those scripts are on the research team's servers.
