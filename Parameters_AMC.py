import pandas as pd
import plotly.graph_objects as go
import re
from plotly.subplots import make_subplots
import plotly.io as pio
#import matplotlib, random
import datetime
import math
from onePlotAll import onePlot

"""Instructions:
Terms: Permanent Variable = a variable for which a graph will always be shown regardless of what you select in the dropdown.
       Segregating Variable = a variable like MP_VALVE_POSITION that splits other variables into different colors.

1. Set number of rows and number of columns you want in numRow and numCol. numCol usually = 1.
2. Set the mode you want in variable mode. Options include: markers, lines, lines+markers. For further reference,
                   go to https://plotly.com/python/line-charts/ and scroll down to 'Line Plot Modes'.
3. Set vertical spacing between each graph
4. Set values that you  want to mask (like -9999) by adding to the array masks
5. Set the permanent variables you want in the permanentVars dictionary. The dictionary consists of key-value pairs,
    where the key is the name of the variable and the value is an array consisting of:
    [the associated QC variable,
    True or False depending on whether it will be split into different colors based on a segregating variable
        (select True only if you want it to be segregated AND len(segregateVals) > 0),
    the row,
    the col,
    the mode,
    True or False depending on whether it is a permanent variable (i.e. True),
    True or False depending on whether the variable has an associated Error variable (i.e. residual): for example, CO2_RESIDUAL_ERR]
6. Set the segregating variable in segregateVar (like MP_VALVE_POSITION). Set an associated dictionary in segregateVals that
    consists of key-value pairs where the key is the name of the segregation (like 'Tower Inlet') and
    the value is the number that codes for that segregation (like 1 codes for 'Tower Inlet' and 2 codes for 'High Span').
    **No segregating vars for AMC, so segregateVar = None and segregateVals will be empty.**
7. No modifications needed here but the dictOfVars goes through and grabs all the variables in the csv file,
   skipping the QC variables and ERR variables and adding them to the array instead of as separate keys.
"""
def parametersMethodAMC(df, year, month, fileWriteFormat):
    #YEAR AND MONTH ARE BOTH STRINGS!!
    fileWriteFormat = fileWriteFormat

    numRow = 9
    numCol = 1
    verticalSpacing = 0.02
    mode = 'markers'

    variableCol = 1

    variables = list(df.columns)

    #If you want to add more masks, just append to the masks array.
    #https://kanoki.org/2019/07/17/pandas-how-to-replace-values-based-on-conditions/
    masks = [-9999, 9999999]
    for variable in variables:
        for mask in masks:
            masked = (df[variable] != mask)
            df[variable] = df[variable][masked]
        if variable[:3] == "VWC" and variable[-3:] != "_QC":
            df[variable].mask(df[variable] > 1, 1.01, inplace = True)

    #these are the variable that will be displayed in the dropdown.
    mainVars = ["VWC", "EC", "TEMP", "PERM", "PERIOD"]

    permanentVars = {'BATT_VOLT_MIN': ['BATT_VOLT_MIN_QC', False, 8, 1, mode, True, False],
                    'PANEL_TEMP_AVG': ['PANEL_TEMP_AVG_QC', False, 9, 1, mode, True, False],
                    'RH_AVG': ['RH_AVG_QC', False, 9, 1, mode, True, False],
                    'PAR_INC_AVG': ['PAR_INC_AVG_QC', False, 7, 1, mode, True, False],
                    'PAR_REF_AVG': ['PAR_REF_AVG_QC', False, 7, 1, mode, True, False]}

    #SEGREGATION
    #if you want to segregate ONE plot by a variable, like CO2 by MP Valve Position, input info below:
    segregateVar = None
    segregateVals = {}

    #Format: (key = the variable): (value = an array)
    #array format: [QCVariable, T/F (should var be split up by MP valve position?), row, col, mode, T/F (Permanent?), T/F (Error bars?)]
    #NOTE: if Error is true, 'figure.py' file assumes that name of error variable is just normal variable + "_ERR"
    dictOfVars = {}

    #Non Permanent Variables here
    l = len(variables)
    for index, variable in enumerate(variables):
        next = ""
        qc = ""
        variableRow = 0
        error = False
        if index < (l - 1):
            next = variables[index + 1]
        else:
            next = None
        #no variable that is excluded in this IF condition is included as a key (in the key-value pairings of the dictionary).
        if variable != 'JUL' and variable != 'TIMESTAMP' and variable[-3:] != '_QC':
            #if a QC variable exists, it is appended in the array (where the array is the value in the key-value pairings of the dictionary).
            if next != None and next[-3:] == '_QC':
                qc = next
            else:
                qc = None
            #AMCsensorNumber is just used to calculate the variable row, is not passed on to any other methods.
            AMCsensorNumber = -1
            #this loop calculates the variable row. Assigns sensors 1 & 2 to row 1, sensors 3 & 4 to row 2, and so on.
            for mainVar in mainVars:
                if variable[:(len(mainVar))] == mainVar:
                    startIndex = len(mainVar) + 1
                    if variable[startIndex + 1] == "_":
                        endIndex = startIndex + 1
                    else:
                        endIndex = startIndex + 2
                    AMCsensorNumber = int(variable[startIndex:endIndex])
                    variableRow = math.ceil(AMCsensorNumber / 2)
            #variableRow is still 0 for all the permanent variables (not VWC, EC, etc.) This assigns them (so like BATT_VOLT_MIN, etc.) MANUALLY. change MANUALLY if desired.
            if variableRow == 0:
                if variable[:3] == "PAR":
                    variableRow = 7
                elif variable[:4] == "BATT":
                    variableRow = 8
                #else condition takes care of PAR_REF_AVG and PAR_INC_AVG.
                else:
                    variableRow = 9
                AMCsensorNumber = 0
            if len(segregateVals) == 0:
                dictOfVars[variable] = [qc, False, variableRow, variableCol, mode, False, error]
            else:
                dictOfVars[variable] = [qc, True, variableRow, variableCol, mode, False, error]
    onePlot(df, numRow, numCol, verticalSpacing, mode, dictOfVars, permanentVars, segregateVar, segregateVals, year, month, fileWriteFormat)
