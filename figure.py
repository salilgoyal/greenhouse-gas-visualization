import pandas as pd
import plotly.graph_objects as go
import re
from plotly.subplots import make_subplots
import plotly.io as pio

'''Instructions:
Description: This file contains 5 methods which control the plotting of the actual traces, as well as creating
dictionaries and arrays that are needed in onePlotAll to control visibility of the traces (which is how the dropdown menu works)

1. method add_trace adds an individual trace.
   A. It contains one sub method, justColor, which controls the color of the data points.
      a. justColor further contains a sub method, evenOddAMC, which separates colors for the AMC sensors by whether sensor numbers
         are even or odd (so that sensors 1 and 2, which are on the same plot, get different colors, and so on for sensors 3 & 4,
         5 & 6, etc.)
      b. In Parameters_AMC, all VWC values greater than 1 were replaced with 1.01. The method makes those points black.
      c. You can change around the colors: Use CSS color names, available at https://www.w3schools.com/cssref/css_colors.asp
   B. The rest of add_trace is split up into 2 cases: If there exists an associated QC variable, or if there does not.
      a. If there does exist a QC variable (i.e. yVarQC != None), then there are two methods: QCmarker controls the shape of the
         data point on the plot (x for bad QC and circle for ok QC), and QClabeling splits up the QC into its basic bits (e.g. 24 into 16+8)
   C. Each of the two preceding cases is split into a further two cases (for a total of four cases): If there exists the need for
      error bars (note: I think these should be calles 'residuals', but I've used the term 'error' everywhere.)

2. create_TFarray creates the True/False array for all systems other than AMC. Each variable has its own T/F array. Any trace
   that should be visible when that variable is selected is True, all others are False. The True and the False are placed
   in an array so that they mirror the sequence of the variables they represent in the variable array.
   A. dlen is the number of traces per variable. For example, all the variables that are separated into 4 MP Valve Positions each
      will have 4 traces each, one for each MP valve position.
   B. In onePlotAll, the permanent traces are appended after all the variable traces. Correspondingly, since the permanent traces should
      have a 'True' in every single T/F array in their spot, these 'True's are appended at the end of the array.

3. create_TFarray_AMC creates the True/False array for any AMC systems. Again, each variable has its own T/F array. The difference is
   that the way the Trues and Falses are listed is different. The five variables (PAR_REF_AVG, PAR_INC_AVG, BATT_VOLT_MIN, RH_AVG, and
   PANEL_TEMP_AVG) are the permanent variables here. So the method puts True wherever those variables are, and True for the needed
   variable from the dropdown (like VWC, EC, etc), and False for everything else (i.e. the rest of the variables in the dropdown).

4. create_dict creates the actual dictionary that consists of the True/False array, plus a few other items.

5. make_MPValve_dfs basically takes the df, and separates it into multiple different dfs based on the segregating variable (like
   MP_VALVE_POSITION). This segregating variable doesn't have to be MP_VALVE_POSITION, but that's all I've come across so far.
   More expanation given below where the method is.
'''
#NECESSARY. Everytime this file is called, count_trace must be reset otherwise the iternal numbering of traces will be screwed up.
count_trace = 0

'''adds a single trace.
:param figure: the plotly figure. Should always be the same across all calls to this method. Figure is created in onePlotAll.py.
:param df: the original dataframe consisting of the entire csv that was created in loop.py.
:param name: the name of the trace. Usually just the name of the variable, unless you have Position 1, Position 2, in which case those are the names.
:param xVar: the x variable. Always TIMESTAMP.
:param yYar: the variable for which this trace is being plotted.
:param yVarQC: the associated QC variable. For example, if yVar = "CO2_DRY_AVG_CORR" then yVarQC = "CO2_DRY_AVG_CORR_QC".
:param rowNum: the row that this trace will be plotted in.
:param colNum: Always 1 (we only have 1 column of plots). If you have multiple columns later on, you will need to input different values.
:param chooseMode: the mode of plotting, like 'markers'. This is set in the Parameters file.
:param error: True or False depending on whether there is an associated error (residual) variable. For example, for CO2_RESIDUAL, it would be True.
              The method then assumes that the name of the error variable is CO2_RESIDUAL_ERR.
'''
def add_trace(figure, df, name, xVar, yVar, yVarQC, rowNum, colNum, chooseMode, error):
    global count_trace
    count_trace = count_trace + 1
    '''helper method to assign colors to traces.
    :param x: the value of the yVar.
    :param y: the value of the yVarQC.
    '''
    def justColor(x, y):
        #since sensors 1 & 2, 3 & 4, etc share the same plot, this helper method makes odd numbers one color and even numbers another color.
        def evenOddAMC(name, positionOfFirstDigit):
            if name[positionOfFirstDigit + 1] == "_":
                return name[positionOfFirstDigit]
            else:
                return name[positionOfFirstDigit] + name[positionOfFirstDigit + 1]
        if (name[:3] == "VWC" and x > 1) or y == -1:
            return "black"
        if name == "Tower Inlet" or name == 'Position 1' or (name[:3] == "VWC" and (int(evenOddAMC(name, 4)) % 2 != 0)):
            return "springgreen"
        elif name == "High Span" or name == 'Position 2' or (name[:3] == "VWC" and (int(evenOddAMC(name, 4)) % 2 == 0)):
            return "steelblue"
        elif name == "Low Span" or name == 'Position 3' or (name[:4] == "TEMP" and (int(evenOddAMC(name, 5)) % 2 != 0)):
            return "tomato"
        elif name == "Target" or name == 'Position 4' or (name[:4] == "TEMP" and (int(evenOddAMC(name, 5)) % 2 == 0)) or name == 'BATT_VOLT_MIN':
            return "gold"
        elif name == 'Position 5' or (name[:2] == "EC" and (int(evenOddAMC(name, 3)) % 2 != 0)) or name == 'PAR_REF_AVG':
            return 'chocolate'
        elif name == 'Position 6' or (name[:2] == "EC" and (int(evenOddAMC(name, 3)) % 2 == 0)):
            return 'olive'
        elif name == 'Position 7' or (name[:4] == "PERM" and (int(evenOddAMC(name, 5)) % 2 != 0)) or name == 'PAR_INC_AVG':
            return 'darkorchid'
        elif name == 'PERM' and (int(evenOddAMC(name, 5)) % 2 == 0) or name == 'PANEL_TEMP_AVG':
            return 'steelblue'
        elif name[:6] == "PERIOD" and (int(evenOddAMC(name, 7)) % 2 != 0):
            return 'steelblue'
        elif name[:6] == "PERIOD":
            return 'tomato'
        else:
            return "plum"

    #FIRST conditional statement
    if yVarQC != None:

        '''helper method assigns shapes based on QC.
        :param x: value of yVarQC.
        '''
        def QCmarker(x):
            if "CALIBRATION_CYLINDER" in yVar:
                if x != 0 and x != 8 and x != 16 and x != 24 and x != 128:
                    return 'x'
                else:
                    return 'circle'
            else:
                if x != 0 and x != 8 and x != 16 and x != 24:
                    return 'x'
                else:
                    return 'circle'

        '''helper method breaks up QC values into basic bits.
        :param x: value of yVarQC.
        '''
        def QClabeling(x):
            basicBits = {-1, 0, 1, 2, 4, 8, 16, 32, 64, 128, 256}
            if x in basicBits:
                return str(int(x))
            elif x / 2 < 8:
                return QClabeling(x - 8) + "+8"
            elif x / 2 < 16:
                return QClabeling(x - 16) + "+16"
            elif x / 2 < 32:
                return QClabeling(x - 32) + "+32"
            elif x / 2 < 64:
                return QClabeling(x - 64) + "+64"
            elif x / 2 < 128:
                return QClabeling(x - 128) + "+128"
            elif x / 2 < 256:
                return QClabeling(x - 256) + "+256"
        #go.Scatter (instead of go.Scattergl) is slower but supports residual bars.
        if error == True:
            errorVar = yVar + "_ERR"
            figure.add_trace(
                go.Scatter(
                    x=df[str(xVar)],
                    y=df[str(yVar)],
                    error_y = dict(type = 'data', array = df[errorVar], symmetric=True, visible = True),
                    text= list(map(QClabeling, df[str(yVarQC)])),
                    hovertemplate = "x: %{x}" + "<br>y: %{y}" + "<br>QC: %{text}",
                    hoverlabel = dict(bgcolor = list(map(justColor, df[str(yVar)]))),
                    #hoverinfo= "name + x + y + text",
                    marker=dict(symbol = list(map(QCmarker, df[str(yVarQC)])), color = list(map(justColor, df[str(yVar)], df[yVarQC]))),
                    mode='markers',
                    name=yVar + ": " + name,
                    visible =False
                ),
                row=rowNum, col=colNum
            )
        #IMPORTANT: go.Scattergl makes it faster with lots of data points, but does not support residual bars.
        elif error == False:
            figure.add_trace(
                go.Scattergl(
                    x=df[str(xVar)],
                    y=df[str(yVar)],
                    text= list(map(QClabeling, df[str(yVarQC)])),
                    hovertemplate = "x: %{x}" + "<br>y: %{y}" + "<br>QC: %{text}",
                    hoverlabel = dict(bgcolor = list(map(justColor, df[str(yVar)], df[yVarQC]))),
                    #hoverinfo= "name + x + y + text",
                    marker=dict(symbol = list(map(QCmarker, df[str(yVarQC)])), color = list(map(justColor, df[str(yVar)], df[yVarQC]))),
                    mode='markers',
                    name=yVar + ": " + name,
                    visible =False
                ),
                row=rowNum, col=colNum
            )
    #SECOND conditional statement
    elif yVarQC == None:
        if error == True:
            errorVar = yVar + "_ERR"
            figure.add_trace(
                go.Scatter(
                    x=df[str(xVar)],
                    y=df[str(yVar)],
                    error_y = dict(type = 'data', array = df[errorVar], symmetric=True, visible = True),
                    hovertemplate = "x: %{x}" + "<br>y: %{y}",
                    #hoverinfo="name + x + y",
                    mode='markers',
                    #now if yVar = 1 this could lead to incorrect black color.
                    marker=dict(color = list(map(justColor, df[str(yVar)], df[yVar]))),
                    name=yVar + ": " + name,
                    visible=False
                ),
                row=rowNum, col=colNum
            )
        elif error == False:
            figure.add_trace(
                go.Scattergl(
                    x=df[str(xVar)],
                    y=df[str(yVar)],
                    hovertemplate = "x: %{x}" + "<br>y: %{y}",
                    #hoverinfo="name + x + y",
                    mode='markers',
                    marker=dict(color = list(map(justColor, df[str(yVar)], df[yVar]))),
                    name=yVar + ": " + name,
                    visible=False
                ),
                row=rowNum, col=colNum
            )

'''creates the array of True and False for non-AMC systems.
:param index: this is the number of the desired trace when put in a list of all the traces. For example,
              in the AOSGHG system, the first variable in the order that variables are listed in in the dataframe
              is CHILLER_TEMPERATURE. It has 4 traces (Position 1 thru 4). The second variable is
              LINE_PRESSURE_TOWER_INLET, which also has 4 traces. Suppose we are creating a TF array for LINE_PRESSURE_TOWER_INLET.
              Then our index will be 5 (because the first 4 indices were taken up by the 4 traces of CHILLER_TEMPERATURE).
              The third variable is EXHAUST_FLOW, which also has 4 traces. Now we'll start at index 9.
:param dlen: This is the number of traces that the current variable has. CHILLER_TEMPERATURE, LINE_PRESSURE_TOWER_INLET and
             EXHAUST_FLOW would all have dlen = 4 since they have 4 traces each.
:param numPermanentTraces: This should be the same for all calls to this method. This is the number of permanent variables
             in our plot. For example, if we had a total of 3 plots with CO2_DRY_AVG_CORR and CH4_DRY_AVG_CORR plotted all the time,
             then numPermanentTraces = 2.
'''
def create_TFarray(index, dlen, numPermanentTraces):
    array = []
    #count_trace is the total number of traces; subtract numPermanentTraces to get the number of traces we have to fill in T/F values for.
    for i in range(count_trace - numPermanentTraces):
        if (dlen == 0):
            if (i + 1 == index):
                array.append(True)
            else:
                array.append(False)
        else:
            if (i + 1 >= index and i + 1 < index + dlen):
                array.append(True)
            else:
                array.append(False)
    #now that T/F values are filled in for the previous traces, append True's to the end of the array, one for each permanent trace.
    for i in range(numPermanentTraces):
        array.append(True)
    return array

'''creates the array of True and False for AMC systems.
:param key: the dropdown item. It will be one of VWC, EC, etc.
:param dict: the dictionary of all the variables that was created in the Parameters_AMC.py file.
:param dropdown: the array of everything that is in the dropdown i.e. ["VWC", "EC", "TEMP", "PERM", "PERIOD"]
'''
def create_TFarray_AMC(key, dict, dropdown):
    array = []
    #helper method for appending True for permanent variables: BATT_VOLT_MIN, RH_AVG, PAR_REF_AVG, PAR_INC_AVG and PANEL_TEMP_AVG.
    def decideTrueFalse(var):
        TF = True
        for item in dropdown:
            if item != key:
                #Suppose key is VWC. Returns false if the var matches any of the other options in the dropdown menu like EC or TEMP.
                if var[:len(item)] == item:
                    TF = False
        #TF = True if var matches either the key of any of the permanent variables. False if it matches any other dropdown options.
        return TF

    for var in dict:
        #suppose our key is VWC. This will append True wherever for all the variables starting with VWC.
        if var[:len(key)] == key:
            array.append(True)
        #This call to the helper method appends True for all the 5 other permanent variables like BATT_VOLT_MIN and RH_AVG.
        elif decideTrueFalse(var):
            array.append(True)
        else:
            array.append(False)
    return array

'''creates ONE dictionary that goes into a dictionary of dictionaries (listOfDicts) in onePlotAll.py, where each
dictionary corresponds to one button on the dropdown menu.
:param TFarray: the array consisting of values True and False that is produced by either create_TFarray or create_TFarray_AMC,
                that controls which traces are visible when this button is clicked in the dropdown menu.
:param title: the name of the button in the dropdown menu
:param yaxis: !!!
'''
def create_dict(TFarray, title, yaxis):
    return dict(
            args = [{"visible": TFarray},
                    {"title": title},
            ],
            label = title,
            method = 'restyle'
    )

'''creates dictionaries for whatever variable you are segregating all the other variables by (ex. MP_VALVE_POSITION)
:param df: the dataframe for the entire dataset (the original df that's created in loop.py)
:param segregateVar: the variable that is being used to segregate. Example: MP_VALVE_POSITION
:param segregateVals: the dictionary of key-value pairs where keys are the numerical values that the segregating variable takes on (like 1, 2, 3, 4)
                      and the values are the names of these keys (like 'Low Span' or 'Position 1' etc.). So this dictionary might look something
                      like {1: 'Low Span', 2: 'Target'} or {1: 'Position 1', 2: 'Position 2'}
'''
def make_MPValve_dfs(df, segregateVar, segregateVals):
    returnDict = {}
    for val in segregateVals:
        mask = (df[segregateVar] == segregateVals[val])
        dfNew = df[mask]
        #array below contains ['name to be shown on plot', df associated with this name]
        #example: towerInlet: ['Tower Inlet', the df that is associated with Tower Inlet]
        returnDict[val] = dfNew

    return returnDict
