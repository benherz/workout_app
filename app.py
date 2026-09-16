from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import urllib.parse

# Initialize the app with suppress_callback_exceptions=True
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY], suppress_callback_exceptions=True)
server = app.server 

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
    # FRIEND VIEW
    if search_string:
        parsed = urllib.parse.parse_qs(search_string.lstrip('?'))
        title = parsed.get('title', ['Unnamed Workout'])[0]
        workout_raw = parsed.get('workout', [''])[0]
        
        exercises = [ex.strip() for ex in workout_raw.split(',') if ex.strip()]
        
        return html.Div([
            html.H2(title, className="mb-4"),
            html.P("Check off each exercise as you finish:"),
            dbc.Checklist(
                options=[{"label": ex, "value": ex} for ex in exercises],
                value=[],
                id="workout-checklist",
                className="fs-4 mb-4" 
            ),
            # This empty Div will hold our success message
            html.Div(id="success-message"),
            html.Hr(),
            html.P("Finished?"),
            dbc.Button("Create Your Own Workout", href="/", color="secondary")
        ])

    # CREATOR VIEW
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
    State('url', 'href') 
)
def generate_link(n_clicks, title, exercises, current_url):
    if not n_clicks or not title or not exercises:
        return ""
    
    safe_title = urllib.parse.quote(title)
    safe_exercises = urllib.parse.quote(exercises)
    
    base_url = current_url.split('?')[0]
    final_link = f"{base_url}?title={safe_title}&workout={safe_exercises}"
    
    return dbc.Alert([
        html.H5("Your link is ready!"),
        html.P("Copy this and send it to your friend:"),
        html.A(final_link, href=final_link, target="_blank", style={"wordBreak": "break-all"})
    ], color="success")

# NEW CALLBACK: Listens to the checklist and triggers the praise message
@app.callback(
    Output('success-message', 'children'),
    Input('workout-checklist', 'value'),
    State('workout-checklist', 'options')
)
def show_praise(checked_items, all_options):
    # If the user has checked off the same number of items as there are total options
    if checked_items and len(checked_items) == len(all_options):
        return dbc.Alert("Yay I'm proud of you! 🎉", color="success", className="mt-2 mb-4")
    return ""

if __name__ == '__main__':
    app.run_server(debug=True)