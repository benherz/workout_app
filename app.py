import os
import random
import dash
from dash import Dash, html, dcc, Input, Output, State, ctx
import dash_bootstrap_components as dbc

# Tell Dash to look in the 'imgs' folder for static files
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY], assets_folder='imgs')

def format_time(seconds):
    """Formats raw seconds into hh:mm:ss"""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def get_random_image():
    """Scans the imgs folder and returns a random file name"""
    imgs_dir = 'imgs'
    if not os.path.exists(imgs_dir):
        return None
    # Filter for standard image types
    valid_ext = ('.png', '.jpg', '.jpeg', '.gif', '.webp')
    files = [f for f in os.listdir(imgs_dir) if f.lower().endswith(valid_ext)]
    
    if not files:
        return None
    return random.choice(files)

app.layout = dbc.Container([
    html.H2("Cardio Timer", className="mt-5 mb-4 text-center"),
    
    # Input and Start Button
    html.Div([
        dbc.Input(id="time-input", type="number", placeholder="Minutes", min=1, style={"width": "120px", "display": "inline-block"}),
        dbc.Button("Start", id="start-btn", color="success", className="ms-3")
    ], className="text-center mb-5"),
    
    # The big clock display
    html.H1("00:00:00", id="timer-display", className="display-1 text-center font-monospace mb-4"),
    
    # Invisible components handling the logic
    dcc.Store(id="time-store", data=0),
    dcc.Interval(id="interval-component", interval=1000, disabled=True),
    
    # Containers for the success message and image
    html.Div(id="success-message", className="text-center mt-4"),
    html.Div(id="image-container", className="text-center mt-3")
    
], style={"maxWidth": "600px"})

@app.callback(
    Output('time-store', 'data'),
    Output('timer-display', 'children'),
    Output('interval-component', 'disabled'),
    Output('success-message', 'children'),
    Output('image-container', 'children'),
    Input('interval-component', 'n_intervals'),
    Input('start-btn', 'n_clicks'),
    State('time-input', 'value'),
    State('time-store', 'data'),
    prevent_initial_call=True
)
def update_timer(n_intervals, start_clicks, input_minutes, current_seconds):
    triggered = ctx.triggered_id
    
    # 1. Start Button Clicked
    if triggered == 'start-btn':
        if not input_minutes or input_minutes <= 0:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
        total_seconds = int(input_minutes * 60)
        # Reset everything: Set new time, format it, enable timer, clear old messages/images
        return total_seconds, format_time(total_seconds), False, "", ""
        
    # 2. Timer is Ticking
    elif triggered == 'interval-component':
        if current_seconds > 0:
            new_sec = current_seconds - 1
            display_text = format_time(new_sec)
            
            # 3. Timer reaches Zero
            if new_sec == 0:
                msg = dbc.Alert("Yay I'm proud of you! 🎉", color="success")
                
                # Fetch image and create HTML element
                img_file = get_random_image()
                if img_file:
                    # app.get_asset_url correctly routes to the imgs folder
                    img_element = html.Img(src=app.get_asset_url(img_file), style={"maxWidth": "100%", "borderRadius": "10px", "maxHeight": "400px"})
                else:
                    img_element = html.P("No images found in the 'imgs' folder.", className="text-muted")
                
                return new_sec, display_text, True, msg, img_element
            
            # Just tick down (do not update success message or image)
            return new_sec, display_text, dash.no_update, dash.no_update, dash.no_update
            
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

if __name__ == '__main__':
    app.run_server(debug=True)