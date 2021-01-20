import pandas as pd
import plotly.graph_objects as go
import re
from plotly.subplots import make_subplots
import plotly.io as pio
#import matplotlib, random
import datetime
from onePlotAll import onePlot

"""Instructions:
Terms: Permanent Variable = a variable for which a graph will always be shown regardless of what you select in the dropdown.
       Segregating Variable = a variable like MP_VALVE_POSITION that splits other variables into different colors.

1. Set number of rows and number of columns you want in numRow and numCol. numCol usually = 1.
    Remember, numRow = (# of permanent variables you want) + 1; the +1 is for the plot that will change according to the dropdown
    The bottom row typically has the graph that displays changing variables, but this can be altered.
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
7. No modifications needed here but the dictOfVars goes through and grabs all the variables in the csv file,
   skipping the QC variables and ERR variables and adding them to the array instead of as separate keys.
"""

def parametersMethodPGS(df, year, month, fileWriteFormat):
    #YEAR AND MONTH ARE BOTH STRINGS!!
    
    yearVar = year
    monthVar = month
    fileWriteFormat = fileWriteFormat
    numRow = 5
    numCol = 1
    verticalSpacing = 0.02
    mode = 'markers'

    #This is the row and column for the graph that changes when you change the dropdown menu. Typically last graph.
    variableRow = 5
    variableCol = 1

    variables = list(df.columns)

    #If you want to add more masks, just append to the masks array.
    #https://kanoki.org/2019/07/17/pandas-how-to-replace-values-based-on-conditions/
    masks = [-9999]
    for variable in variables:
        for mask in masks:
            masked = (df[variable] != mask)
            df[variable] = df[variable][masked]

    #Permanent Variables here
    permanentVars = {'CO2_DRY_AVG_CORR': ['CO2_DRY_AVG_CORR_QC', True, 1, 1, mode, True, False],
                    'CH4_DRY_AVG_CORR': ['CH4_DRY_AVG_CORR_QC', True, 2, 1, mode, True, False],
                    'CO2_RESIDUAL': [None, True, 3, 1, mode, True, True],
                    'CH4_RESIDUAL': [None, True, 4, 1, mode, True, True]}

    #SEGREGATION
    #if you want to segregate ONE plot by a variable, like CO2 by MP Valve Position, input info below:
    segregateVar = 'MP_VALVE_POSITION'
    segregateVals = {'Position 1': 1, 'Position 2': 2, 'Position 3': 3, 'Position 4': 4, 'Position 5': 5, 'Position 6': 6, 'Position 7': 7}

    #Format: (key = the variable): (value = an array)
    #array format: [QCVariable, T/F (should var be split up by MP valve position?), row, col, mode, T/F (Permanent?), T/F (Error bars?)]
    #NOTE: if Error is true, 'figure.py' file assumes that name of error variable is just normal variable + "_ERR"
    dictOfVars = {}

    #Non Permanent Variables are all added here
    l = len(variables)
    for index, variable in enumerate(variables):
        next = ""
        qc = ""
        error = False
        if index < (l - 1):
            next = variables[index + 1]
        else:
            next = None
        #no variable that is excluded in this IF condition is included as a key (in the key-value pairings of the dictionary).
        if variable != 'JUL' and variable != 'TIMESTAMP' and variable[-3:] != '_QC' and variable[-9:] != 'KNOWN_ERR' and variable[-12:] != 'RESIDUAL_ERR':
            #if a QC variable exists, it is appended in the array (where the array is the value in the key-value pairings of the dictionary).
            if next != None and next[-3:] == '_QC':
                qc = next
            else:
                qc = None
            #Error bars are displayed is this IF condition is satisfied.
            if next != None and (next[-9:] == 'KNOWN_ERR' or next[-12:] == 'RESIDUAL_ERR'):
                error = True
            #If segregateVals is empty, the second array element becomes False, meaning nothing is segregated.
            if len(segregateVals) == 0:
                dictOfVars[variable] = [qc, False, variableRow, variableCol, mode, False, error]
            else:
                dictOfVars[variable] = [qc, True, variableRow, variableCol, mode, False, error]
    onePlot(df, numRow, numCol, verticalSpacing, mode, dictOfVars, permanentVars, segregateVar, segregateVals, yearVar, monthVar, fileWriteFormat)
