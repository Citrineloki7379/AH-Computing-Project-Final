import dash_bootstrap_components as dbc
import PortfolioApp

def create_navbar():
    # This creates the Navbar using Dash Bootstrap Components
    navbar = dbc.NavbarSimple(
        # Contains Dropdown menu with page links
        children=[
            dbc.DropdownMenu(
                nav=True,
                in_navbar=True,
                label="Menu", # text for user to click to show options below
                menu_variant="dark",
                size="lg",
                #Below defines the actual options within the Dropdown Menu
                children=[
                    dbc.DropdownMenuItem("Portfolio Overview Page", href='/'),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem("Transactions Page", href='/TransactionsPage'),
                    dbc.DropdownMenuItem("Stock Tracker", href='/StockPage'),
                ],
                direction="start",
            ),
        ],
        brand="Portfolio Overview",  # Set the text on the left side of the Navbar
        brand_href="/",  # Set the URL where the user will be sent when they click the brand I just created "Portfolio Overview"
        brand_style={"font-size": "40px", "font-family": "MajorMonoDisplay-Regular", "font-weight":"light"},
        sticky="top",  # Stick it to the top
        color="dark",
        dark=True,
    )

    return navbar
