
import dash
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.SOLAR])
server=app.server
app.title="Portfolio Visualiser Tool"

# This is the code that allows Dash app to be runnable and set up CSS from pre defined Bootstrap theme 'SOLAR'