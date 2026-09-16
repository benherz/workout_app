# Test for simple webpage to enter and share workout
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import urllib.parse

# Initialize the app with a clean Bootstrap theme
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server # Needed for deployment later

app.layout = dbc.Container([
    # dcc.Location tracks the URL in the address bar
    dcc.Location(id='url', refresh=False),
    
    html.Br(),
    # This Div will swap between the Creator View and the Friend View
    html.Div(id='page-content')
], style={"maxWidth": "600px"})

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'search') # The 'search' property grabs everything after the '?'
)
def display_page(search_string):
    # FRIEND VIEW: If there is data in the URL, show the workout
    if search_string:
        # Parse the URL parameters (e.g., ?title=Leg+Day)
        parsed = urllib.parse.parse_qs(search_string.lstrip('?'))
        title = parsed.get('title', ['Unnamed Workout'])[0]
        workout_raw = parsed.get('workout', [''])[0]
        
        # Split the comma-separated exercises into a list
        exercises = [ex.strip() for ex in workout_raw.split(',') if ex.strip()]
        
        return html.Div([
            html.H2(title, className="mb-4"),
            html.P("Check off each exercise as you finish:"),
            dbc.Checklist(
                options=[{"label": ex, "value": ex} for ex in exercises],
                value=[],
                id="workout-checklist",
                className="fs-4 mb-4" # Make text larger
            ),
            html.Hr(),
            html.P("Finished?"),
            dbc.Button("Create Your Own Workout", href="/", color="secondary")
        ])

    # CREATOR VIEW: If the URL is empty, show the form
    return html.Div([
        html.H2("Create a Workout Link"),
        html.P("Enter the details, generate a link, and send it to a friend."),
        
        dbc.Input(id='title-input', placeholder="Workout Title (e.g., Tuesday Leg Burner)", className="mb-3"),
        dbc.Textarea(id='exercises-input', placeholder="Exercises separated by commas\nExample: 3x10 Squats, 3x12 Lunges, 100m Sprint", style={'height': '150px'}, className="mb-3"),
        
        dbc.Button("Generate Link", id="generate-btn", color="primary", className="mb-4"),
        
        html.Div(id='link-output')
    ])

@app.callback(
    Output('link-output', 'children'),
    Input('generate-btn', 'n_clicks'),
    State('title-input', 'value'),
    State('exercises-input', 'value'),
    State('url', 'href') # Grabs your current base domain
)
def generate_link(n_clicks, title, exercises, current_url):
    if not n_clicks or not title or not exercises:
        return ""
    
    # URL-encode the text to make it safe for web addresses
    safe_title = urllib.parse.quote(title)
    safe_exercises = urllib.parse.quote(exercises)
    
    # Construct the final link
    base_url = current_url.split('?')[0]
    final_link = f"{base_url}?title={safe_title}&workout={safe_exercises}"
    
    return dbc.Alert([
        html.H5("Your link is ready!"),
        html.P("Copy this and send it to your friend:"),
        html.A(final_link, href=final_link, target="_blank", style={"wordBreak": "break-all"})
    ], color="success")

if __name__ == '__main__':
    app.run_server(debug=True)
    
