# greenhouse-gas-visualization

[This README file is a work in progress].

There are three types of ghg-monitoring systems set up for this project: AOSGHG, AMC and PGS. Their graphs are set up differently, so each has a different
file in which parameters (i.e. number of variables to be displayed, time period to be displayed, etc.) are specified.


The descriptions and details of all the files are documented within the files themselves.

The files work as such:

loop.py --> Parameters_[system].py --> onePlotAll.py --> figure.py --> onePlotAll.py --> plot.html
