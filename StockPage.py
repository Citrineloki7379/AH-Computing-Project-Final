from dash import html
from dash import dcc
from pandas.core.frame import DataFrame
from pandas.core.indexes.base import Index
from NavagationBar import create_navbar
import dash_bootstrap_components as dbc
import pandas as pd
from dash import dash_table
import plotly.graph_objects as go
import plotly.express as px
from dash.dependencies import Input, Output, State
import datetime
import time
import requests
import io
import yfinance as yf
from TickerPopulation import DataPopulation, GetTickers
from PortfolioApp import app

#Navbar is imported and assigned
nav = create_navbar()
#Header text is created
header = html.H3('Welcome to Stock Tracker!', style={"text-align":"center", "margin-top":"20px", "margin-bottom":"20px"}, 
                  className="text-light")

Tickers=GetTickers()

#This function creates creates and returns the webpage
def create_page_StockTracker():
    #This places the nav and header into the webpage.
    layout = html.Div([
        nav,
        header,
        #Below defines container with the dropdown menu for page
        dbc.Row([
            dbc.Col(
                #Below defines Stock Dropdown menu
                dbc.Card([
                    html.H5(children=["Stock Options"], className="text-center"),
                    dcc.Dropdown(
                        id="stock_options",
                        #Below are options users can choose
                        options=[ {"label": str(i), "value": str(i)} for i in Tickers],
                        value=Tickers[0],
                        #multiple filters cannot be applied
                        multi=False,
                        clearable=False
                    )],
                ),
                width={"size":6, "offset":3},
                style={"margin-bottom":"20px"}
            )
            ]),
        
        #Below defines the container which contains the candlestick graph
        dbc.Row([
            dbc.Col(
                dcc.Graph(id="Stock-Graph"),
                width={"size":8, "offset":2},
                style={"margin-bottom":"20px"}
            )
            ]),

        #Below is the container with the Indicators and Volume graph.
        dbc.Row([
            dbc.Col(
                dcc.Graph(id="Volume-Graph"),
                width={"size":4, "offset":2}
                ),
            dbc.Col(
                dcc.Graph(id="Indicators"),
                width=4,
                style={"margin-bottom":"20px"}
                )
            ])

    ])
    return layout

#This function listens for user changes in the selection of the stock in the dropdown menu 
#then executes the function below to load and display graphs on the stock data.
@app.callback([Output("Stock-Graph", "figure"), Output("Volume-Graph", "figure"),Output("Indicators", "figure")],
              [Input("stock_options", "value")])
def display_charts(value):
    dataframe=DataPopulation(value) # Receive Data and store in array of records

    #Below creates the graphs for the page
    Candlestick=display_candlestick(value, dataframe)
    Volume=display_volume(value, dataframe)
    Indicators=display_indicators(value, dataframe)

    return Candlestick, Volume, Indicators


#Below is the definition for the candlestick graph.
def display_candlestick(value, df):
    fig = go.Figure(go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"]
    ))
    #Below adds plot colour style and axis titles
    fig.update_layout( template="plotly_dark", title="Price Variation of "+value, xaxis_title="Date", yaxis_title="Price in USD" )

    return fig

#Below is the definition of the Volume graph
def display_volume(value, df):
    fig=go.Figure([(
        go.Bar(
            x=df.index,
            y=df["Volume"]
        )
    )])
    #Below adds plot colour style and axis titles
    fig.update_layout( template="plotly_dark", title="Volume of "+value+" traded", xaxis_title="Date", yaxis_title="Volume of trades")

    return fig

#Below creates the indicators based on data
def display_indicators(value, df):
    fig=go.Figure()

    fig.add_trace(go.Indicator(
        mode = "delta", #defines indicator type
        value = df.iloc[len(df.index)-1, 3], #Defines value it should use
        delta = {"reference": df.iloc[len(df.index)-31, 3], "valueformat": ".0f"}, # defines what the above should be compared to 
        title = {"text": "30 Day Price Shift"},#Defines title
        domain={"x":[0.0, 0.4], "y":[0.0, 0.4]}))#defines position within container.

    fig.add_trace(go.Indicator(
        mode = "number+gauge+delta",#defines indicator type
        value = VolAvg(df, 0, 30),#Defines value it should use, Average volume last 30 days
        delta = {"reference": VolAvg(df, 30, 30), "valueformat": ".0f"},# defines what the above should be compared to 
        title = {"text": "Daily Volume", "align":"center"},#Defines title
        domain={"x":[0.6, 1.0], "y":[0.0, 0.4]}))#defines position within container.

    fig.add_trace(go.Indicator(
        mode = "delta",#defines indicator type
        value = df.iloc[len(df.index)-1, 3],#Defines value it should use
        delta = {"reference": df.iloc[len(df.index)-8, 3], "valueformat": ".0f"},
        title = {"text": "7 Day Price Shift"},
        domain={"x":[0.0, 0.4], "y":[0.6, 1.0]}))

    fig.add_trace(go.Indicator(
        mode = "number+gauge+delta",#defines indicator type
        value = VolAvg(df, 0, 7),#Defines value it should use, Average volume last 7 days
        delta = {"reference": VolAvg(df, 7, 7), "valueformat": ".0f"},# defines what the above should be compared to
        title = {"text": "Daily Volume", "align":"center"},#Defines title
        domain={"x":[0.6, 1.0], "y":[0.6, 1.0]}))#defines position within container.

    fig.update_layout(template="plotly_dark")
    return fig

#Below is used to calculate average volume from given date range based on 
#array of records of stock data.
def VolAvg(Dataframe, Days, Length):
    Total=0
    for x in range(Length):
        Total=Total+Dataframe.iloc[len(Dataframe.index)-1-Days-x, 5]
    return int(Total/Length)
