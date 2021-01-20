import pandas as pd
import plotly.graph_objects as go
import re
from plotly.subplots import make_subplots
import plotly.io as pio
import os.path
from os import path
#import matplotlib, random
import datetime
import Parameters_PGS
from Parameters_PGS import parametersMethodPGS
import Parameters_AOSGHG
from Parameters_AOSGHG import parametersMethodAOSGHG
import Parameters_AMC
from Parameters_AMC import parametersMethodAMC
import figure

'''!!!!!IMPORTANT!!!!!!
COMMENT OUT THE CRONTAB IF YOU ARE RUNNING HISTORICAL DATA
!!!!!IMPORTANT!!!!!
'''

'''For ENA_AOSGHG_LOCAL_SOURCE uncomment/comment line 39 and lines 116-121 in this file.
'''

'''calls the correct one of the three different Parameters files.
:param year: year of file.
:param monthStart: the first month you want included.
:param monthEnd: the last month you want included (do NOT do a +1 as this method takes care of that).
:param system: in the form 'ENA_AOSGHG' or 'OLI_AMC' etc.
:param bVar: either 'b1' or 'b0'.
'''
def callParam(year, monthStart, monthEnd, system, bVar):
    #fileReadFormat is used later on to read the file. Includes path name. Currently, looks like 'data/OLI_AMC/OLI_AMC_b0_'. Change path name if needed.
    fileReadFormat = "data/" + system + "/" + system + "_" + bVar + "_"
    #fileWriteFormat is how the filename will be written. Currently, looks like 'OLI_AMC_b0_'. Month/year appended later.
    fileWriteFormat = system + "_" + bVar + "_"
    #for ENA_AOSGHG_LOCAL_SOURCE, comment the ABOVE line and uncomment the BELOW line
    #fileWriteFormat = system + "_" + "LOCAL_SOURCE" + "_" + bVar + "_"
    for month in range(monthStart, monthEnd + 1):
        monthVar = str(month)
        if len(monthVar) == 1:
            monthVar = "0" + monthVar
        filename = fileReadFormat + str(year) + monthVar + ".csv"
        if path.exists(filename):
            df = pd.read_csv(filename)
            figure.count_trace = 0
            if system[-6:] == "AOSGHG":
                parametersMethodAOSGHG(df, str(year), monthVar, fileWriteFormat)
            elif system[-3:] == "PGS":
                parametersMethodPGS(df, str(year), monthVar, fileWriteFormat)
            elif system[-3:] == "AMC":
                parametersMethodAMC(df, str(year), monthVar, fileWriteFormat)

'''These lines are three examples of test code in case you want to test something only on 1 file. Comment out everything
below these lines and just run one of these examples to test on one file.'''
#df = pd.read_csv("OLI_AMC_b0_201809.csv")
#parametersMethodAMC(df, "2018", "09", "OLI_AMC_b0_")
#df = pd.read_csv("ENA_AOSGHG_b1_201908.csv")
#parametersMethodAOSGHG(df, "2019", "08", "ENA_AOSGHG_LOCAL_SOURCE_b1_")
#df = pd.read_csv("SGP_PGS_b1_202001.csv")
#parametersMethodPGS(df, "2020", "01", "SGP_PGS_b1_")

#CURRENT MONTH AND YEAR
dt = datetime.datetime.today()
currentMonth = dt.month
currentYear = dt.year

listOfSystems1 = ["ENA_AOSGHG", "OLI_AOSGHG", "TMP_AOSGHG", "BKR_AOSGHG", "TMP_PGS", "SGP_PGS"]
for system in listOfSystems1:
    callParam(currentYear, currentMonth, currentMonth, system, 'b1')

listOfSystems2 = ["OLI_AMC", "NSA_AMC", "SGP_AMC"]
for system in listOfSystems2:
    callParam(currentYear, currentMonth, currentMonth, system, 'b0')

#BELOW THIS: CODE RUNS FOR ALL PREVIOUS MONTHS FROM THE START OF THE SYSTEM TILL NOW. ONLY DO IF THERE'S A NEED TO UPDATE ALL PREVIOUS FILES.

#FOR OLI_AMC
'''for year in range(2014, currentYear + 1):
    if year == 2014:
        callParam(year, 9, 12, "OLI_AMC", "b0")
    elif year == currentYear:
        callParam(year, 1, currentMonth, "OLI_AMC", "b0")
    else:
        callParam(year, 1, 12, "OLI_AMC", "b0")'''

#FOR NSA_AMC
'''for year in range(2012, currentYear + 1):
    if year == 2012:
        callParam(year, 8, 12, "NSA_AMC", "b0")
    elif year == currentYear:
        callParam(year, 1, currentMonth, "NSA_AMC", "b0")
    else:
        callParam(year, 1, 12, "NSA_AMC", "b0")'''

#FOR SGP_AMC
'''for year in range(2016, currentYear + 1):
    if year == 2016:
        callParam(year, 4, 12, "SGP_AMC", "b0")
    elif year == currentYear:
        callParam(year, 1, currentMonth, "SGP_AMC", "b0")
    else:
        callParam(year, 1, 12, "SGP_AMC", "b0")'''

#FOR ENA_AOSGHG
'''for year in range(2015, 2021):
    system = "ENA_AOSGHG"
    if year == 2015:
        callParam(year, 7, 12, system, "b1")
    if year == 2020:
        callParam(year, 1, 1, system, "b1")
    else:
        callParam(year, 1, 12, system, "b1")'''

#FOR ENA_AOSGHG_LOCAL_SOURCE
#goes from 2016 to 2019
#see line 39 in loop.py to comment/uncomment
'''for year in range(2016, 2020):
    system = "ENA_AOSGHG"
    callParam(year, 1, 12, system, "b1")'''

#FOR OLI_AOSGHG
'''for year in range(2015, currentYear + 1):
    system = "OLI_AOSGHG"
    if year == 2015:
        callParam(year, 6, 12, system, "b1")
    elif year == currentYear:
        callParam(year, 1, currentMonth, system, "b1")
    else:
        callParam(year, 1, 12, system, "b1")'''

#FOR TMP_AOSGHG
'''for year in range(2017, 2020):
    if year == 2017:
        callParam(year, 2, 12, "TMP_AOSGHG", "b1")
    if year == 2018:
        callParam(year, 1, 12, "TMP_AOSGHG", "b1")
    if year == 2019:
        callParam(year, 1, 1, "TMP_AOSGHG", "b1")'''

#FOR BKR_AOSGHG
'''for year in range(2019, currentYear + 1):
    if year == 2019:
        callParam(year, 5, 12, "BKR_AOSGHG", "b1")
    if year == currentYear:
        callParam(year, 1, currentMonth, "BKR_AOSGHG", "b1")'''

#FOR SGP_PGS
'''for year in range(2015, currentYear + 1):
    if year == 2015:
        callParam(year, 12, 12, "SGP_PGS", "b1")
    elif year == currentYear:
        callParam(year, 1, currentMonth, "SGP_PGS", "b1")
    else:
        callParam(year, 1, 12, "SGP_PGS", "b1")'''

#FOR TMP_PGS
'''for year in range (2019, currentYear + 1):
    if year == 2019:
        callParam(year, 2, 12, "TMP_PGS", "b1")
    elif year == currentYear:
        callParam(year, 1, currentMonth, "TMP_PGS", "b1")'''
