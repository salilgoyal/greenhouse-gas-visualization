import pandas as pd
import plotly.graph_objects as go
import re
from plotly.subplots import make_subplots
import plotly.io as pio
#import matplotlib, random
from figure import add_trace, make_MPValve_dfs, create_TFarray, create_TFarray_AMC, create_dict

'''this is the method that creates the actual plot.
:param df: the dataframe of the entire csv.
:param numRow: the total number of rows. Set in Parameters file.
:param numCol: the number of columns. Should be 1. Set in Parameters file.
:param verticalSpacing: the spacing between each of the plots. Can be finneky, test on a local machine before changing this. Set in Parameters file.
:param chooseMode: what the data visually looks like. For example, 'markers' or 'lines' or 'lines+markers'. For further reference,
                   go to https://plotly.com/python/line-charts/ and scroll down to 'Line Plot Modes'.
:param dict: the dictionary of all the variables read from the df, where keys are variable names and values are arrays with info about MP valve, row number, etc.
:param permanentVars: the dictionary of all the permanent variables.
:param segregateVar: the name of the variable that is used to segregate data (ex. MP_VALVE_POSITION). Can also be set to None.
:param segregateVals: the dictionary of key-value pairs where keys are the numerical values that the segregating variable takes on (like 1, 2, 3, 4)
                      and the values are the names of these keys (like 'Low Span' or 'Position 1' etc.). So this dictionary might look something
                      like {1: 'Low Span', 2: 'Target'} or {1: 'Position 1', 2: 'Position 2'}
:param year: the year of the data as a string. Used in the naming of the html file.
:param month: the month of the data as a string. Used in the naming of the html file.
:param fileWriteFormat: example: "OLI_AOSGHG_b1_". The year and month are appended to the end of this. Used in naming of the html file.
'''
def onePlot(df, numRow, numCol, verticalSpacing, chooseMode, dict, permanentVars, segregateVar, segregateVals, year, month, fileWriteFormat):

    #make a dictionary of dictionaries where each member dictionary is a df for each MP valve position.
    dict_of_dfs = make_MPValve_dfs(df, segregateVar, segregateVals)

    yearVar = year
    monthVar = month

    #creates the actual figure (plot)
    fig = make_subplots(
        rows = numRow, cols = numCol,
        shared_xaxes = True,
        vertical_spacing = verticalSpacing
    )

    '''makes the call to add_trace simpler. For example, automatically fills in TIMESTAMP because that is always there.
    '''
    def call_add_trace(df, yVar, yVarQC, row, col, error):
        add_trace(fig, df, yVar, 'TIMESTAMP', yVar, yVarQC, row, col, chooseMode, error)

    '''for a variable that is separated by MP_VALVE_POSITION, this method adds all 4 traces with one call to the method.
    '''
    def call_add_trace_MP(yVar, yVarQC, row, col, error):
        for dict in dict_of_dfs:
            add_trace(fig, dict_of_dfs[dict], dict, 'TIMESTAMP', yVar, yVarQC, row, col, chooseMode, error)

    #is_AMC becomes True if there exists a variable that starts with 'VWC'
    is_AMC = False
    for key in dict:
        if key[:3] == "VWC":
            is_AMC = True

    #STEP 1: go through and add all the non-permanent traces.
    traces = 0
    for key in dict:
        #this boolean check is for whether or not the variable is segregated according to MP_VALVE_POSITION.
        if dict[key][1] == False:
            call_add_trace(df, key, dict[key][0], dict[key][2], dict[key][3], dict[key][6])
        else:
            call_add_trace_MP(key, dict[key][0], dict[key][2], dict[key][3], dict[key][6])
        traces += 1

    #STEP 2: go through and add all the permanent traces.
    #the variable permanentTraces is used when creating the True/False array in create_TFarray in figure.py to know the number of True's to append to the end of the array.
    #don't need to do this for AMC since the permanent variables were already added above in their correct locations.
    #need to do this for all other systems because permanent variables were only added to the last row above, not to any of the 1-2 or 1-4 rows.
    if not is_AMC:
        for key in permanentVars:
            if permanentVars[key][1] == False:
                call_add_trace(df, key, permanentVars[key][0], permanentVars[key][2], permanentVars[key][3], permanentVars[key][6])
            else:
                call_add_trace_MP(key, permanentVars[key][0], permanentVars[key][2], permanentVars[key][3], permanentVars[key][6])

    #This list of dictionaries contains one dictionary for each button on the dropdown menu.
    listOfDicts = []

    if is_AMC:
        AMCdropdown = ["VWC", "EC", "TEMP", "PERM", "PERIOD"]
        for key in AMCdropdown:
            listOfDicts.append(create_dict(create_TFarray_AMC(key, dict, AMCdropdown), key, key))

        fig.update_layout(
            updatemenus=[
                go.layout.Updatemenu(
                    buttons=list(listOfDicts),
                    direction="down",
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    x=0.1,
                    xanchor="left",
                    y=1.1,
                    yanchor="top",
                ),
            ]
        )

        fig.update_layout(
            annotations=[
                go.layout.Annotation(
                    text='<b>QC Bit  Description</b><br>0       Data OK<br>1       Missing Value<br>2       < valid min<br>4       > valid max',
                    align='left',
                    xref='paper',
                    yref='paper',
                    x=1.19,
                    y=0.3,
                    bordercolor='black'
                )
            ]
        )

    elif not is_AMC:
        index = 1
        numPermanentTraces = 0
        #this for loop is to find the number of permanent traces, which is used in create_TFarray in figure.py.
        for key in permanentVars:
            if permanentVars[key][1] == True:
                numAppend = 1
                if len(segregateVals) != 0:
                    numAppend = len(segregateVals)
                numPermanentTraces += numAppend
            else:
                numPermanentTraces += 1

        #Non-permanent graphs--this for loop simply appends to listOfDicts, which is used in the update_layout method below.
        for key in dict:
            #MP Values
            if dict[key][1] == True:
                dlen = len(segregateVals)
            else:
                dlen = 0
            listOfDicts.append(create_dict(create_TFarray(index, dlen, numPermanentTraces), key, key))
            if dlen == 0:
                index += 1
            else:
                index += dlen

        fig.update_layout(
            updatemenus=[
                go.layout.Updatemenu(
                    buttons=list(listOfDicts),
                    direction="down",
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    x=0.1,
                    xanchor="left",
                    y=1.1,
                    yanchor="top",
                )
            ],
        )

        fig.update_layout(
            annotations=[
                go.layout.Annotation(
                    text='<b>QC Bit  Description</b><br>0       Data OK<br>1       Missing Value<br>2       < valid min<br>4       > valid max<br>8       *SlOPE is missing value<br>16      *SLOPE_ERR is missing value<br>32      *SLOPE < valid min<br>64      *SLOPE > valid max<br>128     *SLOPE significant w.r.t. 0<br>256     QC aux var is not 0',
                    align='left',
                    xref='paper',
                    yref='paper',
                    x=1.19,
                    y=0.3,
                    bordercolor='black'
                )
            ]
        )


    #Common for all graphs, whether AMC or non-AMC. showlegend controls whether the legend on the right hand side is visible.
    fig.update_layout(
        showlegend=True,
        title_text=fileWriteFormat,
    )

    #Update axes titles
    fig.update_xaxes(title_text = 'TIMESTAMP', row = numRow, col = 1)
    if is_AMC:
        for row in range(numRow - 3 + 1):
            fig.update_yaxes(title_text = "Sensor " + str(row * 2 - 1) + " & " + str(row * 2), row = row, col = 1)
        fig.update_yaxes(title_text = "PAR_INC & PAR_REF", row = 7, col = 1)
        fig.update_yaxes(title_text = "BATT_VOLT_MIN", row = 8, col = 1)
        fig.update_yaxes(title_text = "PANEL_TEMP & RH", row = 9, col = 1)
    else:
        for key in permanentVars:
            fig.update_yaxes(title_text = key, row = permanentVars[key][2], col = permanentVars[key][3])

    fig.update_layout(height = 1500)

    fileToOutput = fileWriteFormat + yearVar + monthVar + '.html'
    pio.write_html(fig, file = fileToOutput, auto_open = False)
