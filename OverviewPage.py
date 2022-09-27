from dash import html
from dash import dcc
from NavagationBar import create_navbar
import dash_bootstrap_components as dbc
import pandas as pd
from dash import dash_table
from dash.dependencies import Input, Output, State
from PortfolioApp import app
from datetime import datetime
import base64
import io
import plotly.graph_objects as go
import plotly.express as px
from TransactionsPage import InsertionSort

#Navbar is imported and assigned
nav = create_navbar()
#Header text is created
header = html.H3('Welcome to Overview Page!', style={"text-align":"center", "margin-top":"20px", "margin-bottom":"20px"}, 
className="text-light")


#This function creates creates and returns the webpage
def create_page_Overview():
    #This places the nav and header into the webpage.
    layout = html.Div([
        nav,
        header,

        dbc.Row([
            dbc.Col(
                #Below defines Stock Dropdown menu
                dbc.Card([
                    #This is the CSV upload Box code
                    dcc.Upload(id="CSVOverview-input", children=html.Div(["Drag and Drop or ",html.A("Select Files")]),
                                #Below defines box dimensions and positioning
                               style={
                                        'width': '97%',
                                        'height': '60px',
                                        'lineHeight': '60px',
                                        'borderWidth': '1px',
                                        'borderStyle': 'dashed',
                                        'borderRadius': '5px',
                                        'textAlign': 'center',
                                        'margin': '10px'
                                    } ),
                    #Below are text in hidden divs. These are updated when user inputs csv file
                    #If valid validfile overview is shown else invalidfile overview text shown
                    html.P('Must be a csv file with the Columns: "Portfolioid", "Date", "TotalValue", "FundValue", "StockValue", "BondValue", "TotalVolume", "FundVolume", "StockVolume", "BondVolume"',
                            style={"text-align":"center"}),
                    html.P("That looks like a valid csv file :-)", id="ValidFileOverview", style={"display":"None"}),
                    html.P("That is not a valid csv file :-(", id="InvalidFileOverview", style={"display":"None"}),
                    ],

                ),
                #Below defines container of file box dimensions and postion on page.
                width={"size":6, "offset":3},
                style={"margin-bottom":"20px"}
            )
            ]),

        #Below defines a temporary store of graph data as a dictonary
        #(Array of records essentially)
        dcc.Store(id="GraphData"),

        #Below defines container which contains download button.
        dbc.Row(
            dbc.Col([
                dbc.Button("Download Test Data", id="DownloadOverviewButton"),
                dcc.Download(id="DownloadOverview")
                ],
                style={"margin-bottom":"20px"},
                className="d-grid gap-2 col-6 mx-auto"
            )
        ),

        #Below defines containers in row below buttons.
        dbc.Row([
            #Below defines the line chart postion and size.
            dbc.Col(
                dcc.Graph(id="LineChart"),
                width={"size":8, "offset":2},
                style={"margin-bottom":"20px"}
            )
            ]),
        
        #Below defines container below line chart
        dbc.Row([
            #Below defines Pie chart size and positioning
            dbc.Col(
                dcc.Graph(id="PieChart"),
                width={"size":4, "offset":2},
                style={"margin-bottom":"20px"}
            ),
            #Below defines Pie chart of Volume size and postioning.
            dbc.Col(
                dcc.Graph(id="VolumeChart"),
                width={"size":4},
                style={"margin-bottom":"20px"}
            )
            ])
    ])
    return layout


#This function listens for changes in state of the CSV input box. Once CSV file is entered 
#The function is excecuted taking CSV file entered and returning values for what the graphs 
#should contain, displaying the correct validity of file text and storing the CSV data as a
#dictonary in a temporary created location id"GraphData"
@app.callback([Output("ValidFileOverview", "style"), Output("InvalidFileOverview", "style"), Output("GraphData", "data"),
               Output("PieChart", "figure"), Output("LineChart", "figure"), Output("VolumeChart", "figure")],
              [Input("CSVOverview-input", "contents")],
              [State("CSVOverview-input", "filename")])
def PopulateGraphs(contents, filename):
    Val, Inval={"display":"None"}, {"display":"None"}

    #Checks if anything is entered into the CSV box
    if contents is None:
        return Val, Inval, None, EmptyGraph(), EmptyGraph(), EmptyGraph()

    #Checks file type
    elif not("csv" in filename):
        Inval={"display":"Block", "text-align":"center"}
        return Val, Inval, None, EmptyGraph(), EmptyGraph(), EmptyGraph()
    
    else:
        #Below tries to read CSV file
        try:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            OverviewRecords=pd.read_csv(io.StringIO(decoded.decode('utf-8')))

        #If any errors then this picks them up and sends fail message to user.
        except (ValueError, FileNotFoundError):
            Inval={"display":"Block", "text-align":"center"}
            return Val, Inval, None, EmptyGraph(), EmptyGraph(), EmptyGraph()
        
        #If the required columns aren't there file is rejected.
        if list(OverviewRecords.columns)!=["Portfolioid", "Date", "TotalValue", "FundValue", 
        "StockValue", "BondValue", "TotalVolume", "FundVolume", "StockVolume", "BondVolume"]:
            Inval={"display":"Block", "text-align":"center"}
            return Val, Inval, None, EmptyGraph(), EmptyGraph(), EmptyGraph()
        
        #If file Passes all tests valid text is displayed, graphs populated and data stored.
        else:
            Val={"display":"Block", "text-align":"center"}
            OverviewRecords=InsertionSort(OverviewRecords, 1)
            return Val, Inval, OverviewRecords.to_dict("records"), PieChart(OverviewRecords), LineChart(OverviewRecords), VolumeChart(OverviewRecords)

#This function listens for when the download button is clicked and once that happens 
#The function is run which causes a test file to be downloaded onto user device.
@app.callback(
    Output("DownloadOverview", "data"),
    Input("DownloadOverviewButton", "n_clicks"),
    prevent_initial_call=True,
)
def ReturnCSVOverview(n_clicks):
    Temp=pd.read_csv("TestOverview.csv")
    Temp.set_index("Portfolioid", inplace=True)
    return dcc.send_data_frame(Temp.to_csv, "TestOverviewData.csv")

#This function creates the Pie chart
def PieChart(Data):
    fig=go.Figure(
        data=[go.Pie(
        labels=["Funds","Stocks", "Bonds"], #Adds :abels to each segment
        #Below adds data that Pie chart is going to be based on.
        values=[Data.iloc[len(Data.index)-1, 3], Data.iloc[len(Data.index)-1, 4], Data.iloc[len(Data.index)-1, 5]],
        hole=0.3 #Adds hole in centre of chart.
        )]
        )

    fig.update_layout(template="plotly_dark", title="Latest Portfolio Composition (Price)")
    return fig

#This function creates LineChart
def LineChart(Data):
    fig=px.line(Data, x="Date", y="TotalValue", template="plotly_dark", title="Total Portfolio Value Over Time")
    return fig

#This creates blank graph if no CSV file or invalid CSV file is entered.
def EmptyGraph():
    fig=go.Figure()
    fig.update_layout(template="plotly_dark", title="Will be populated on valid csv file upload")
    return fig

#This creates the Volume Pie chart
def VolumeChart(Data):
    fig=go.Figure(
        data=[go.Pie(
        labels=["Funds","Stocks", "Bonds"],
        values=[Data.iloc[len(Data.index)-1, 7], Data.iloc[len(Data.index)-1, 8], Data.iloc[len(Data.index)-1, 9]],
        hole=0.3
        )]
        )

    fig.update_layout(template="plotly_dark", title="Latest Portfolio Composition (Volume)")
    return fig
