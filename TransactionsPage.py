from dash import html
from dash import dcc
from dash.html.P import P
from NavagationBar import create_navbar
import dash_bootstrap_components as dbc
import pandas as pd
from dash import dash_table
from dash.dependencies import Input, Output, State
from PortfolioApp import app
from datetime import datetime
import base64
import io


#Navbar is imported and assigned
nav = create_navbar()
#Header text is created
header = html.H3('Welcome to Transactions Page!', style={"text-align":"center", "margin-top":"20px", "margin-bottom":"20px"}, 
                  className="text-light")

#This function creates creates and returns the webpage to App Navigation
def create_page_Transactions():
    layout = html.Div([
        #This places the nav and header into the webpage.
        nav,
        header,

        dbc.Row([
            dbc.Col(
                #Below defines CSV File Drag and Drop Box on the Web Page
                dbc.Card([
                    dcc.Upload(id="CSVTransactions-input", children=html.Div(["Drag and Drop or ",html.A("Select Files")]),
                               style={
                                        'width': '97%',
                                        'height': '60px',
                                        'lineHeight': '60px',
                                        'borderWidth': '1px',
                                        'borderStyle': 'dashed',
                                        'borderRadius': '5px',
                                        'textAlign': 'center',
                                        'margin': '10px'
                                    }),
                    #This Text Helps User enter correctly formatted CSV Files
                    html.P('Must be a csv file with the Columns: "Transactionid","Date", "Type", "Status", "Price", "Volume", "Name"',
                            style={"text-align":"center"}),
                    #This text is set to display Block if CSV file is valid
                    html.P("That looks like a valid csv file :-)", id="ValidFileTransactions", style={"display":"None"}),
                    #This text is set to display Block if CSV file is invalid
                    html.P("That is not a valid csv file :-(", id="InvalidFileTransactions", style={"display":"None"}),
                    ],


                    #style={"margin-left":"300px"}
                ),
                width={"size":6, "offset":3},
                style={"margin-bottom":"20px"}
            )
            ]),

        #This code below Is a Download Button To Dowload a test Transactions CSV file for the User to test page out with
        dbc.Row(
            dbc.Col([
                dbc.Button("Download Test Data", id="DownloadTransactionsButton"),
                dcc.Download(id="DownloadTransactions")
                ],
                #width={"size":4, "offset":4},
                style={"margin-bottom":"20px"},
                className="d-grid gap-2 col-6 mx-auto"
            )

        ),

        #This places the Sort and filter dropdown menus side be side in a row.
        dbc.Row([
            dbc.Col(
                #Below defines Filter Dropdown menu
                dbc.Card([
                    html.H5(children=["Filter Options"], className="text-center"),
                    dcc.Dropdown(
                        id="filter_options",
                        #Below are options users can choose
                        options=[ {"label": "Bonds", "value": "Bonds"},
                                  {"label": "Stocks", "value":"Stocks"},
                                  {"label": "Fund", "value": "Fund"},
                                  {"label": "Purchased", "value": "Purchased"},
                                  {"label": "Sold", "value": "Sold"}],
                        placeholder="Select...",
                        #Below is default value
                        value=[],
                        #multiple filters can be applied
                        multi=True,
                    )],
                ),
                width={"size":4, "offset":2}

            ),

            dbc.Col(
                #Below defines the Sort options
                dbc.Card([
                    html.H5(children=["Sort Options"], className="text-center"),
                    #Below are the sorts users can choose
                    dcc.Dropdown(
                        id="sort_options",
                        options=[ {"label": "Transactionid(ASC)", "value": "TransactionidASC"},
                                  {"label": "Transactionid(DESC)", "value": "TransactionidDESC"},
                                  {"label": "Price(ASC)", "value": "PriceASC"},
                                  {"label": "Price(DESC)", "value": "PriceDESC"},
                                  {"label": "Date(ASC)", "value": "DateASC"},
                                  {"label": "Date(DESC)", "value": "DateDESC"},
                                  {"label": "Volume(ASC)", "value": "VolumeASC"},
                                  {"label": "Volume(DESC)", "value": "VolumeDESC"}],
                        placeholder="Select...",
                        #Below is the default sort applied
                        value=None,
                    )],
                ),
                width=4,

                style={"margin-bottom":"20px"}
            )
        ]),

        #Below defines the Table that is displayed
        dbc.Row([
            dbc.Col(
                dash_table.DataTable(
                    id="transaction_table",
                    page_action="native",
                    page_current=0,
                    page_size=10,
                    style_cell={"text-align": "left"},
                    style_header={
                        'backgroundColor': 'rgb(30, 30, 30)',
                        'color': 'white'
                    },
                    style_data={
                        'backgroundColor': 'rgb(50, 50, 50)',
                        'color': 'white'
                    }
                ),
                width={"size":8, "offset":2},
                style={"margin-bottom":"20px"}
            )
        ]),

        #This stores the downloaded user data so that multiple app callbacks can use the downloaded data.
        dcc.Store(id="TableData")
    ])
    return layout

"""
App callbacks are what allow the webpage to react to the user input and generate an appropriate output in the page.
App callbacks act as the back end of the website, each callback acts like an event listener in javascript based on the
particular app callback input parameters which are related to elements on the webpage. When the user makes an alteration
on the page (like changing a sort option from a dropdown) the relevant app callbacks which are related to that are triggered,
causing those callbacks to pull all the required data from the website, cache stores (dcc.Store from above) and any Databases
and then running the function it is attached to based on these inputs. These functions then use this data to run their required
code and then return values. These return values are what are then returned to the web page as outputs and can directly alter
the web page, such as revealing hidden text, updating tables, and inserting new elements to the web page.
"""

#The below callback listens for any csv input and once CSV is entered The function is run and returns
#the default filter and sort options, user prompt text and stores data in temp location
@app.callback([Output("filter_options", "value"), Output("sort_options", "value"),
               Output("ValidFileTransactions", "style"), Output("InvalidFileTransactions", "style"), Output("TableData", "data")],
              [Input("CSVTransactions-input", "contents")],
              [State("CSVTransactions-input", "filename")])
def PopulateTable(contents, filename):
    Val, Inval={"display":"None"}, {"display":"None"}

    #If no file entered then this returns no data to temp location
    if contents is None:
        return [], None, Val, Inval, {"Transactionid":[],"Date":[], "Type":[], "Status":[], "Price":[], "Volume":[], "Name":[]}

    #If not CSV file then invalid message sent and no data to temp location
    elif not("csv" in filename):
        Inval={"display":"Block", "text-align":"center"}
        return [], None, Val, Inval, {"Transactionid":[],"Date":[], "Type":[], "Status":[], "Price":[], "Volume":[], "Name":[]}
    
    else:
        try:
            #This tries to open csv file into array of records.
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            TransactionsRecords=pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        
        #If the file doesn't exist or there is some error in value (like not csv somehow) send invalid message and 
        #no data to temp location
        except (ValueError, FileNotFoundError):
            Inval={"display":"Block", "text-align":"center"}
            return [], None, Val, Inval, {"Transactionid":[],"Date":[], "Type":[], "Status":[], "Price":[], "Volume":[], "Name":[]}
        
        #If the file doesn't have required columns then sends invalid message and no data to temp location
        if list(TransactionsRecords.columns)!=["Transactionid","Date", "Type", "Status", "Price", "Volume", "Name"]:
            Inval={"display":"Block", "text-align":"center"}
            return [], None, Val, Inval, {"Transactionid":[],"Date":[], "Type":[], "Status":[], "Price":[], "Volume":[], "Name":[]}

        #If csv file passes all tests then send the valid message and send data of table to temp location.
        #Because the filter and sort options are set to default by this function. Once this function
        #returns those sort and filter options because those values were updated the FilterAndSort function
        #is automatically called with no filters and sorts which outputs all the data in the table.
        else:
            Val={"display":"Block", "text-align":"center"}
            return [], None, Val, Inval, TransactionsRecords.to_dict("records")


#Below listens for changes in the filter and sort options and then returns the resultant
#table with the current values of filters and sorts applied to be displayed
@app.callback([Output("transaction_table", "data"), Output("transaction_table", "columns")],
              [Input("filter_options", "value"), Input("sort_options", "value"), Input("TableData", "data")])
def FilterAndSort(Filters, Sort, DataDict):
    #Do nothing if no data exists
    if DataDict==None:
        return None, None

    #Creates a new array of records with filters applied
    TempFrame=pd.DataFrame.from_dict(DataDict)
    FilterFrame=ApplyFilters(Filters, TempFrame)

    #This lists through sort options and applies appropriate 
    #sorting based on what optionnis selected.
    if Sort!=None:
        if "Transactionid" in Sort:
            Column=0
        elif "Date" in Sort:
            Column=1
        elif "Price" in Sort:
            Column=4
        else:
            Column=5

        SortFrame=InsertionSort(FilterFrame, Column)

        #Checks if the descending option is selected to then 
        #reverse sort accordingly
        if Sort[len(Sort)-1:len(Sort)-5:-1]=="CSED":
            SortFrame=SortFrame[::-1]
    else:
        SortFrame=FilterFrame


    return SortFrame.to_dict("records"), [{"name": i, "id": i} for i in SortFrame.columns]

#Listens for the download button being clicked and returns a test csv file
#which is downloaded onto the user's device
@app.callback(
    Output("DownloadTransactions", "data"),
    Input("DownloadTransactionsButton", "n_clicks"),
    prevent_initial_call=True,
)
def ReturnCSVTransactions(n_clicks):
    Temp=pd.read_csv("TestTransactions.csv")
    Temp.set_index("Transactionid", inplace=True)
    return dcc.send_data_frame(Temp.to_csv, "TestTransactionsData.csv")

#Below is the insertion sort function applied to the array of records.
#Takes in the column row and applies sort on array based on that
def InsertionSort(DataFrame, Column):
    for x in range(1,len(DataFrame.index)):
        Current=DataFrame.iloc[x]
        Value=DataFrame.iloc[x, Column]
        Counter=x

        #Sorting by date is a separate case requiring conversion of string to a date object to properly sort
        #Hence conditional statement below.
        if Column==1:
            while Counter>0 and datetime.strptime(Value, "%d/%m/%Y")<datetime.strptime(DataFrame.iloc[Counter-1, Column], "%d/%m/%Y"):
                DataFrame.iloc[Counter]=DataFrame.iloc[Counter-1] # shifting element up
                Counter=Counter-1
        else:
            while Counter>0 and Value<DataFrame.iloc[Counter-1, Column]:
                DataFrame.iloc[Counter]=DataFrame.iloc[Counter-1] # shifting element up
                Counter=Counter-1

        DataFrame.iloc[Counter]=Current # inserting current element into correct slot.

    return DataFrame

#Below applies the filters to the array of records.
def ApplyFilters(Filters, DataFrame):
    Types=[] #Stores filters selected for the type of asset.
    Conditions=[] #Stores filters for the bought, sold condition of asset.

    #Checks selected filters for types and sale conditions chosen
    for x in Filters:
        if x in ["Bonds", "Stocks", "Fund"]:
            Types.append(x)
        elif x in ["Purchased", "Sold"]:
            Conditions.append(x)
    
    #If no Type filters chosen by default all are displayed
    if len(Types)==0:
        Types=["Bonds", "Stocks", "Fund"]

    #If no Conditions filters chosen by default all are displayed
    if len(Conditions)==0:
        Conditions=["Purchased", "Sold"]

    #Uses in built function in Dataframe to choose the records which contain the chosen 
    #types and conditions
    FilterFrame=DataFrame[DataFrame.Type.isin(Types) & DataFrame.Status.isin(Conditions)]
    return FilterFrame
