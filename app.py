import dash
from dash import Dash, html, dcc, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import urllib.parse

# Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY], suppress_callback_exceptions=True)
server = app.server 

def format_time(seconds):
    """Helper to format raw seconds into hh:mm:ss"""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    html.Br(),
    html.Div(id='page-content')
], style={"maxWidth": "600px"})

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'search') 
)
def display_page(search_string):
    # FRIEND VIEW (Timer)
    if search_string:
        parsed = urllib.parse.parse_qs(search_string.lstrip('?'))
        title = parsed.get('title', ['Unnamed Cardio'])[0]
        
        # Safely get the minutes from the URL and convert to total seconds
        try:
            minutes = int(parsed.get('time', ['0'])[0])
        except ValueError:
            minutes = 0
            
        total_seconds = minutes * 60
        
        return html.Div([
            html.H2(title, className="mb-4 text-center"),
            
            # The big clock display
            html.H1(format_time(total_seconds), id="timer-display", className="display-1 text-center mb-4 font-monospace"),
            
            # Invisible components that handle the actual counting
            dcc.Store(id="time-store", data=total_seconds),
            dcc.Interval(id="interval-component", interval=1000, n_intervals=0, disabled=True),
            
            # Controls
            html.Div([
                dbc.Button("Start", id="start-btn", color="success", className="me-2"),
                dbc.Button("Pause", id="pause-btn", color="warning"),
            ], className="text-center mb-4"),
            
            # Empty Div to hold the success message
            html.Div(id="success-message"),
            
            html.Hr(),
            html.P("Finished?", className="text-center"),
            html.Div(dbc.Button("Create Your Own Timer", href="/", color="secondary"), className="text-center")
        ])

    # CREATOR VIEW (Form)
    return html.Div([
        html.H2("Create a Cardio Timer"),
        html.P("Set the time, generate a link, and send it to a friend."),
        
        dbc.Input(id='title-input', placeholder="Workout Title (e.g., Sunday 5k Run)", className="mb-3"),
        dbc.Input(id='time-input', type='number', placeholder="Time limit (in minutes)", min=1, className="mb-3"),
        
        dbc.Button("Generate Link", id="generate-btn", color="primary", className="mb-4"),
        
        html.Div(id='link-output')
    ])

# Generate the URL
@app.callback(
    Output('link-output', 'children'),
    Input('generate-btn', 'n_clicks'),
    State('title-input', 'value'),
    State('time-input', 'value'),
    State('url', 'href') 
)
def generate_link(n_clicks, title, minutes, current_url):
    if not n_clicks or not title or not minutes:
        return ""
    
    safe_title = urllib.parse.quote(title)
    
    base_url = current_url.split('?')[0]
    # We now put the 'time' parameter in the URL instead of 'workout'
    final_link = f"{base_url}?title={safe_title}&time={minutes}"
    
    return dbc.Alert([
        html.H5("Your link is ready!"),
        html.P("Copy this and send it to your friend:"),
        html.A(final_link, href=final_link, target="_blank", style={"wordBreak": "break-all"})
    ], color="success")

# Timer Logic: Handles Start, Pause, and Ticking
@app.callback(
    Output('time-store', 'data'),
    Output('timer-display', 'children'),
    Output('interval-component', 'disabled'),
    Output('success-message', 'children'),
    Input('interval-component', 'n_intervals'),
    Input('start-btn', 'n_clicks'),
    Input('pause-btn', 'n_clicks'),
    State('time-store', 'data'),
    prevent_initial_call=True
)
def update_timer(n_intervals, start_clicks, pause_clicks, current_seconds):
    # dash.ctx tells us exactly what triggered this callback
    triggered = ctx.triggered_id
    
    if triggered == 'start-btn':
        # Don't update the time, just enable the interval clock
        return dash.no_update, dash.no_update, False, dash.no_update
        
    elif triggered == 'pause-btn':
        # Don't update the time, just disable the interval clock
        return dash.no_update, dash.no_update, True, dash.no_update
        
    elif triggered == 'interval-component':
        # If the clock ticked and we have time left, subtract 1 second
        if current_seconds > 0:
            new_sec = current_seconds - 1
            display_text = format_time(new_sec)
            
            # If they hit 0, stop the clock and show the message
            if new_sec == 0:
                msg = dbc.Alert("Yay I'm proud of you! 🎉", color="success", className="text-center mt-3")
                return new_sec, display_text, True, msg
            
            # Otherwise, just update the time and text
            return new_sec, display_text, dash.no_update, dash.no_update
            
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update

if __name__ == '__main__':
    app.run_server(debug=True)