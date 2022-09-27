#This downloads all the required Dash dependancies and the webpages.

from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from OverviewPage import create_page_Overview
from TransactionsPage import create_page_Transactions
from StockPage import create_page_StockTracker
from PortfolioApp import app


#This code is required for the app to function.
server = app.server
app.config.suppress_callback_exceptions = True
app.css.config.serve_locally = True

app.layout = html.Div([
    dcc.Location(id='url', refresh=False), # This stores current url for whole user session
    html.Div(id='page-content') # This is the div used to insert selected page on screen
])

# Code below handles changing the current page to user desired page.
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    
    #Below checks current url value and displays appropriate page 
    if pathname == '/TransactionsPage':
        return create_page_Transactions()

    if pathname == '/StockPage':
        return create_page_StockTracker()

    else:
        return create_page_Overview()

# This runs the app
if __name__ == '__main__':
    app.run_server(debug=True)



