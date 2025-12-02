"""
🌍 FORTNITE-STYLE GLOBE DASHBOARD - DATABRICKS APP (GitHub Safe Version)
==========================================================================
This file is safe to commit to GitHub - all sensitive data uses environment variables.

DEPLOYMENT INSTRUCTIONS:
1. Upload this file to your Databricks workspace
2. Ensure your cluster has the required libraries:
   - dash
   - plotly
   - pandas
   - databricks-sql-connector
3. Set the following environment variables in your app.yaml:
   - DATABRICKS_SERVER_HOSTNAME
   - DATABRICKS_HTTP_PATH
   - DATABRICKS_TOKEN
   - DATABRICKS_SCHEMA
   - AI_AGENT_ENDPOINT (for chatbot feature)
   - DATABRICKS_DASHBOARD_ID (for embedded dashboard feature)
   - DATABRICKS_WORKSPACE_ID (for embedded dashboard feature)
   - SOCIAL_LISTENING_URL (for social listening feature)
4. Deploy as a Databricks App using the Databricks CLI or UI

For more info on Databricks Apps:
https://docs.databricks.com/en/dev-tools/databricks-apps/index.html
"""

import os
import time
import re
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import dash
from dash import Dash, dcc, html, Input, Output, State, callback_context
from databricks import sql
import requests
import json

# VERSION IDENTIFIER - Check logs to confirm new version is loaded
APP_VERSION = "v7.2_GITHUB_SAFE_SOCIAL_LISTENING"
print(f"\n{'='*80}")
print(f"🚀 LOADING APP VERSION: {APP_VERSION}")
print(f"   🔒 GitHub-safe version - all credentials from environment variables")
print(f"   👤 Added user login display in top-right corner")
print(f"   🎧 Added Social Listening sidebar option with iframe embedding")
print(f"{'='*80}\n")

# ═══════════════════════════════════════════════════════════════════════════
# 🔧 CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

# Databricks connection settings - reads from environment variables
DATABRICKS_CONFIG = {
    'server_hostname': os.getenv('DATABRICKS_SERVER_HOSTNAME'),
    'http_path': os.getenv('DATABRICKS_HTTP_PATH'),
    'access_token': os.getenv('DATABRICKS_TOKEN')
}

# Validate required environment variables
required_vars = {
    'DATABRICKS_SERVER_HOSTNAME': DATABRICKS_CONFIG['server_hostname'],
    'DATABRICKS_HTTP_PATH': DATABRICKS_CONFIG['http_path'],
    'DATABRICKS_TOKEN': DATABRICKS_CONFIG['access_token']
}

missing_vars = [var for var, value in required_vars.items() if not value]
if missing_vars:
    print(f"⚠️  WARNING: Missing environment variables: {', '.join(missing_vars)}")
    print("App will start with sample data. Real data fetching will be disabled.")
    print("Set these environment variables to enable real data:")
    for var in missing_vars:
        print(f"  • {var}")
    # Don't raise error, just warn - app will use sample data

# Schema and table configuration
SCHEMA_NAME = os.getenv('DATABRICKS_SCHEMA', 'catalog.schema')

# Dashboard settings
REFRESH_INTERVAL = 30000  # 30 seconds
ROTATION_SPEED = 1.5  # degrees per frame
INITIAL_ROTATION = -30  # starting longitude

# AI Agent configuration - from environment variables
AI_AGENT_ENDPOINT = os.getenv('AI_AGENT_ENDPOINT', 'your-ai-agent-endpoint')

# Construct AI base URL from server hostname
server_hostname = DATABRICKS_CONFIG['server_hostname'] or 'your-workspace.azuredatabricks.net'
# Remove https:// if present and any trailing query params
server_hostname = server_hostname.replace('https://', '').replace('http://', '').split('?')[0]
AI_BASE_URL = f"https://{server_hostname}/serving-endpoints"

# Dashboard configuration - from environment variables
DATABRICKS_DASHBOARD_ID = os.getenv('DATABRICKS_DASHBOARD_ID', 'your-dashboard-id')
# Extract workspace ID from URL if present (e.g., ?o=1234567890123456)
workspace_id_match = re.search(r'[?&]o=(\d+)', DATABRICKS_CONFIG['server_hostname'] or '')
DATABRICKS_WORKSPACE_ID = workspace_id_match.group(1) if workspace_id_match else os.getenv('DATABRICKS_WORKSPACE_ID', 'your-workspace-id')

# Social Listening app configuration - from environment variables
SOCIAL_LISTENING_URL = os.getenv('SOCIAL_LISTENING_URL', 'https://your-social-listening-app.databricksapps.com/')

print(f"🔧 Configuration loaded:")
print(f"   • Server: {server_hostname[:50]}...")
print(f"   • Schema: {SCHEMA_NAME}")
print(f"   • AI Endpoint: {AI_AGENT_ENDPOINT}")
print(f"   • Dashboard ID: {DATABRICKS_DASHBOARD_ID[:20]}...")
print(f"   • Social Listening URL: {SOCIAL_LISTENING_URL[:50]}...")

# ═══════════════════════════════════════════════════════════════════════════
# 🗄️ DATA FETCHING
# ═══════════════════════════════════════════════════════════════════════════

def get_databricks_connection():
    """Create and return a Databricks SQL connection"""
    return sql.connect(
        server_hostname=DATABRICKS_CONFIG['server_hostname'],
        http_path=DATABRICKS_CONFIG['http_path'],
        access_token=DATABRICKS_CONFIG['access_token']
    )

def create_sample_data():
    """Create sample data for display when database is unavailable"""
    df = pd.DataFrame({
        'country': ['USA', 'Japan', 'Brazil', 'UK', 'Germany', 'Australia', 'Canada', 'France', 'India', 'Mexico'],
        'city': ['New York', 'Tokyo', 'São Paulo', 'London', 'Berlin', 'Sydney', 'Toronto', 'Paris', 'Mumbai', 'Mexico City'],
        'latitude': [40.7128, 35.6762, -23.5505, 51.5074, 52.5200, -33.8688, 43.6532, 48.8566, 19.0760, 19.4326],
        'longitude': [-74.0060, 139.6503, -46.6333, -0.1278, 13.4050, 151.2093, -79.3832, 2.3522, 72.8777, -99.1332],
        'active_sessions': [150, 120, 90, 80, 70, 65, 60, 55, 50, 45],
        'player_count': [150, 120, 90, 80, 70, 65, 60, 55, 50, 45],
        'avg_session_duration': [45.5, 52.3, 38.7, 41.2, 47.8, 39.2, 44.1, 41.8, 48.3, 42.7]
    })
    # Calculate marker sizes
    max_sessions = df['active_sessions'].max()
    min_sessions = df['active_sessions'].min()
    df['marker_size'] = 8 + (df['active_sessions'] - min_sessions) / (max_sessions - min_sessions + 1) * 35
    
    # Create hover text
    df['hover_text'] = (
        df['city'].astype(str) + ', ' + df['country'].astype(str) + '<br>' +
        '🎮 Active Sessions: ' + df['active_sessions'].astype(str) + '<br>' +
        '👥 Players: ' + df['player_count'].astype(str) + '<br>' +
        '⏱ Avg Duration: ' + df['avg_session_duration'].round(1).astype(str) + ' min'
    )
    return df

def fetch_active_players():
    """Fetch active player location data from Databricks"""
    print(f"📊 Fetching data from schema: {SCHEMA_NAME}")
    
    # Query to get total sessions per location (not split by device type)
    query = f"""
    WITH recent_sessions AS (
        SELECT 
            s.player_id,
            p.latitude,
            p.longitude,
            p.city,
            p.country
        FROM {SCHEMA_NAME}.sessions s
        JOIN {SCHEMA_NAME}.players p ON s.player_id = s.player_id
        WHERE s.status = 'completed'
        ORDER BY s.start_time DESC
        LIMIT 500
    )
    SELECT 
        latitude,
        longitude,
        city,
        country,
        COUNT(*) as active_sessions,
        COUNT(*) as player_count,
        45.0 as avg_session_duration
    FROM recent_sessions
    GROUP BY latitude, longitude, city, country
    ORDER BY active_sessions DESC
    """
    
    # Try using Spark first if available (faster when running in Databricks)
    try:
        from pyspark.sql import SparkSession
        spark = SparkSession.builder.getOrCreate()
        print("✨ Using Spark SQL (running in Databricks)")
        result = spark.sql(query)
        df = result.toPandas()
        print(f"✅ Spark query returned {len(df)} rows")
        
        if len(df) == 0:
            print("⚠️  Spark query returned 0 rows, using sample data")
            return create_sample_data()
        
        # Add required columns
        max_sessions = df['active_sessions'].max()
        min_sessions = df['active_sessions'].min()
        df['marker_size'] = 8 + (df['active_sessions'] - min_sessions) / (max_sessions - min_sessions + 1) * 35
        df['hover_text'] = (
            df['city'].astype(str) + ', ' + df['country'].astype(str) + '<br>' +
            '🎮 Active Sessions: ' + df['active_sessions'].astype(str) + '<br>' +
            '👥 Players: ' + df['player_count'].astype(str) + '<br>' +
            '⏱ Avg Duration: ' + df['avg_session_duration'].round(1).astype(str) + ' min'
        )
        return df
        
    except Exception as spark_error:
        print(f"⚠️  Spark not available: {spark_error}")
        print("📡 Falling back to SQL Connector...")
    
    # Fallback to SQL connector if Spark isn't available
    if not all([DATABRICKS_CONFIG['server_hostname'], 
                DATABRICKS_CONFIG['http_path'], 
                DATABRICKS_CONFIG['access_token']]):
        print("⚠️  Missing Databricks credentials, using sample data")
        return create_sample_data()
    
    try:
        print("🔌 Connecting to Databricks...")
        print(f"   Server: {DATABRICKS_CONFIG['server_hostname'][:50]}...")
        print(f"   HTTP Path: {DATABRICKS_CONFIG['http_path'][:50]}...")
        
        with get_databricks_connection() as conn:
            print("✅ Connection established!")
            with conn.cursor() as cursor:
                print("📝 Executing query...")
                print(f"   Query preview: {query[:100]}...")
                cursor.execute(query)
                print("✅ Query executed, fetching results...")
                columns = [desc[0] for desc in cursor.description]
                data = cursor.fetchall()
                print(f"✅ Fetched {len(data)} rows")
                df = pd.DataFrame(data, columns=columns)
                print(f"✅ DataFrame created: {len(df)} rows")
        
        if len(df) == 0:
            # Return sample data if no active sessions
            print("=" * 60)
            print("⚠️  WARNING: Query returned 0 rows!")
            print("This could mean:")
            print("  1. No sessions with status='completed' exist")
            print("  2. Schema or table names are incorrect")
            print("  3. Tables are empty")
            print("Using sample data instead.")
            print("=" * 60)
            return create_sample_data()
        
        # Calculate marker sizes
        max_sessions = df['active_sessions'].max()
        min_sessions = df['active_sessions'].min()
        df['marker_size'] = 8 + (df['active_sessions'] - min_sessions) / (max_sessions - min_sessions + 1) * 35
        
        # Create hover text
        df['hover_text'] = (
            df['city'].astype(str) + ', ' + df['country'].astype(str) + '<br>' +
            '🎮 Active Sessions: ' + df['active_sessions'].astype(str) + '<br>' +
            '👥 Players: ' + df['player_count'].astype(str) + '<br>' +
            '⏱ Avg Duration: ' + df['avg_session_duration'].round(1).astype(str) + ' min'
        )
        
        return df
        
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        import traceback
        traceback.print_exc()
        print(f"⚠️  Using sample data due to error")
        # Return sample data on error
        return create_sample_data()

# ═══════════════════════════════════════════════════════════════════════════
# 🤖 AI AGENT INTERACTION
# ═══════════════════════════════════════════════════════════════════════════

def get_ai_response(conversation_history):
    """
    Send conversation history to Databricks AI agent and get response
    Uses requests library instead of openai for better compatibility
    
    Args:
        conversation_history: List of dicts with 'role' and 'content'
    
    Returns:
        str: AI agent's response text
    """
    try:
        databricks_token = DATABRICKS_CONFIG['access_token']
        if not databricks_token:
            return "❌ Error: DATABRICKS_TOKEN not configured. Please set environment variable."
        
        # Construct API endpoint URL for Databricks AI agent
        endpoint_url = f"{AI_BASE_URL}/{AI_AGENT_ENDPOINT}/invocations"
        
        # Prepare request headers
        headers = {
            "Authorization": f"Bearer {databricks_token}",
            "Content-Type": "application/json"
        }
        
        # Prepare request payload - Databricks expects 'input' not 'messages'
        payload = {
            "input": conversation_history,
            "max_output_tokens": 1000
        }
        
        print(f"🔗 Calling AI endpoint: {endpoint_url}")
        print(f"📤 Sending {len(conversation_history)} messages in conversation")
        
        # Make POST request to Databricks AI endpoint
        # Increased timeout to 90 seconds for slow AI responses
        response = requests.post(
            endpoint_url,
            headers=headers,
            json=payload,
            timeout=90
        )
        
        # Check if request was successful
        if response.status_code != 200:
            error_msg = f"❌ API Error {response.status_code}: {response.text}"
            print(error_msg)
            return error_msg
        
        # Parse response
        response_data = response.json()
        print(f"📦 Response keys: {list(response_data.keys())}")
        
        # Extract message from response - Databricks AI agent format
        # Expected format: response.output[0].content[0].text
        if 'output' in response_data:
            output = response_data['output']
            if isinstance(output, list) and len(output) > 0:
                first_output = output[0]
                if isinstance(first_output, dict) and 'content' in first_output:
                    content = first_output['content']
                    if isinstance(content, list) and len(content) > 0:
                        first_content = content[0]
                        if isinstance(first_content, dict) and 'text' in first_content:
                            text = first_content['text']
                            print(f"✅ AI response received ({len(text)} chars)")
                            return text
        
        # Fallback: try standard OpenAI format
        if 'choices' in response_data and len(response_data['choices']) > 0:
            ai_message = response_data['choices'][0]['message']['content']
            print(f"✅ AI response received ({len(ai_message)} chars)")
            return ai_message
        
        # If we can't parse it, return the whole response for debugging
        return f"❌ Error: Unexpected response format. Response: {json.dumps(response_data, indent=2)}"
        
    except requests.exceptions.Timeout:
        return "❌ Error: Request timed out. The AI agent took too long to respond."
    except requests.exceptions.RequestException as e:
        error_msg = f"❌ Network error: {str(e)}"
        print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"❌ Error calling AI agent: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return error_msg

# ═══════════════════════════════════════════════════════════════════════════
# 🎨 GLOBE VISUALIZATION
# ═══════════════════════════════════════════════════════════════════════════

def create_globe_figure(df, rotation_lon=INITIAL_ROTATION):
    """Create the 3D globe visualization with Fortnite styling"""
    
    fig = go.Figure()
    
    # Add heatmap markers
    fig.add_trace(go.Scattergeo(
        lon=df['longitude'],
        lat=df['latitude'],
        text=df['hover_text'],
        mode='markers',
        marker=dict(
            size=df['marker_size'],
            color=df['active_sessions'],
            colorscale=[[0, '#00D9FF'], [0.5, '#FF006E'], [1, '#FF8800']],  # Blue -> Pink -> Orange
            showscale=True,
            colorbar=dict(
                title="ACTIVE<br>SESSIONS",
                thickness=15,
                len=0.6,
                x=0.98,  # Moved closer to avoid cutoff
                xanchor='right',
                bgcolor='rgba(0, 0, 0, 0.8)',
                bordercolor='#00D9FF',
                borderwidth=2,
                tickfont=dict(color='#00D9FF', family='Arial Black', size=10),
                titlefont=dict(color='#FF006E', family='Arial Black', size=12)
            ),
            line=dict(width=2, color='#00D9FF'),
            sizemode='diameter',
            opacity=0.9,
            cmin=0,
            cmax=df['active_sessions'].max()
        ),
        hovertemplate='<b>%{text}</b><br>' +
                      'Lat: %{lat:.2f}<br>' +
                      'Lon: %{lon:.2f}<br>' +
                      '<extra></extra>',
        name='Active Players'
    ))
    
    # Configure layout with Fortnite styling (matching notebook version)
    fig.update_layout(
        title=dict(
            text='CURRENTLY PLAYING - BATTLE GLOBE',
            font=dict(
                size=28,
                color='#00D9FF',
                family='Arial Black'
            ),
            x=0.5,
            xanchor='center'
        ),
        geo=dict(
            projection_type='orthographic',
            projection_rotation=dict(lon=rotation_lon, lat=20, roll=0),
            showland=True,
            landcolor='rgb(20, 20, 30)',
            showocean=True,
            oceancolor='rgb(0, 0, 0)',
            showcountries=True,
            countrycolor='rgb(60, 40, 80)',
            coastlinecolor='rgb(157, 78, 221)',
            showlakes=False,
            bgcolor='rgb(0, 0, 0)'
        ),
        paper_bgcolor='rgb(0, 0, 0)',
        plot_bgcolor='rgb(0, 0, 0)',
        margin=dict(l=0, r=0, t=60, b=0),
        showlegend=False,
        height=800,
        font=dict(color='#00D9FF', family='Arial'),
        dragmode='pan',  # Enable dragging
        hovermode='closest'  # Better hover behavior
    )
    
    # Disable scroll zoom
    fig.update_geos(
        projection_type='orthographic',
        projection_rotation=dict(lon=rotation_lon, lat=20, roll=0)
    )
    
    return fig

# ═══════════════════════════════════════════════════════════════════════════
# 🚀 DASH APPLICATION
# ═══════════════════════════════════════════════════════════════════════════

# Initialize Dash app
app = Dash(__name__, update_title=None)  # update_title=None disables "Updating..." in browser tab
server = app.server  # Expose the Flask server for Databricks Apps

# Inject custom CSS for markdown formatting
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .ai-markdown-content {
                color: #ffffff;
                font-family: Arial, sans-serif;
                line-height: 1.6;
            }
            .ai-markdown-content h1,
            .ai-markdown-content h2,
            .ai-markdown-content h3 {
                color: #00D9FF;
                margin-top: 10px;
                margin-bottom: 10px;
            }
            .ai-markdown-content h1 { font-size: 1.5em; }
            .ai-markdown-content h2 { font-size: 1.3em; }
            .ai-markdown-content h3 { font-size: 1.1em; }
            .ai-markdown-content p {
                margin: 8px 0;
                color: #ffffff;
            }
            .ai-markdown-content ul,
            .ai-markdown-content ol {
                margin: 10px 0;
                padding-left: 25px;
                color: #ffffff;
            }
            .ai-markdown-content li {
                margin: 5px 0;
                color: #ffffff;
            }
            .ai-markdown-content code {
                background-color: rgba(255, 0, 110, 0.2);
                padding: 2px 6px;
                border-radius: 3px;
                color: #FF006E;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
            }
            .ai-markdown-content pre {
                background-color: rgba(20, 20, 30, 0.9);
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #FF006E;
                overflow-x: auto;
                margin: 10px 0;
            }
            .ai-markdown-content pre code {
                background-color: transparent;
                padding: 0;
                color: #00D9FF;
            }
            .ai-markdown-content strong {
                color: #FF8800;
                font-weight: bold;
            }
            .ai-markdown-content em {
                color: #FF006E;
                font-style: italic;
            }
            .ai-markdown-content a {
                color: #00D9FF;
                text-decoration: underline;
            }
            .ai-markdown-content blockquote {
                border-left: 3px solid #00D9FF;
                padding-left: 15px;
                margin: 10px 0;
                color: #aaaaaa;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Create initial sample data figure (don't fetch from DB at startup to avoid crashes)
print("🚀 Initializing app with sample data...")
try:
    sample_df = create_sample_data()
    initial_figure = create_globe_figure(sample_df, INITIAL_ROTATION)
    print(f"✅ App initialized successfully: {len(sample_df)} locations")
    
    # Initialize cached data with sample data (will be replaced by real data after first interval)
    _cached_globe_data = sample_df
    
except Exception as e:
    print(f"❌ Error creating initial figure: {e}")
    import traceback
    traceback.print_exc()
    # Create minimal figure as last resort
    initial_figure = go.Figure()
    initial_figure.update_layout(
        title="Loading...",
        paper_bgcolor='#000000',
        plot_bgcolor='#000000',
        font=dict(color='#00D9FF')
    )
    print("⚠️  Created minimal figure as fallback")
    _cached_globe_data = sample_df if 'sample_df' in locals() else create_sample_data()

# App layout with Fortnite styling
app.layout = html.Div([
    # Hidden stores for state management
    dcc.Store(id='rotation-angle', data=INITIAL_ROTATION),
    dcc.Store(id='conversation-history', data=[]),  # Store chat conversation history
    dcc.Store(id='insights-data', data=None),  # Store fetched insights
    dcc.Store(id='current-page', data='home'),  # Track current page
    dcc.Store(id='sidebar-open', data=False),  # Track sidebar state
    
    # Sidebar menu
    html.Div(
        id='sidebar',
        style={
            'position': 'fixed',
            'left': '-320px',  # Hidden by default (width + border)
            'top': '0',
            'width': '300px',
            'height': '100vh',
            'backgroundColor': 'rgba(10, 10, 20, 0.98)',
            'border': '2px solid #00D9FF',
            'borderLeft': 'none',
            'zIndex': '2000',
            'transition': 'left 0.3s ease, visibility 0s linear 0.3s',
            'padding': '20px',
            'overflowY': 'auto',
            'visibility': 'hidden'  # Completely hide when closed
        },
        children=[
            html.H2('MENU', style={
                'color': '#00D9FF',
                'fontFamily': 'Arial Black, sans-serif',
                'fontSize': '28px',
                'marginBottom': '30px',
                'textAlign': 'center',
                'textShadow': '0 0 15px #00D9FF'
            }),
            
            # Menu items
            html.Div([
                html.Button('🏠 Home', id='menu-home', n_clicks=0, style={
                    'width': '100%',
                    'padding': '15px',
                    'marginBottom': '10px',
                    'fontSize': '18px',
                    'fontWeight': 'bold',
                    'backgroundColor': '#00D9FF',
                    'color': '#000000',
                    'border': 'none',
                    'borderRadius': '10px',
                    'cursor': 'pointer',
                    'fontFamily': 'Arial Black, sans-serif',
                    'boxShadow': '0 0 10px #00D9FF'
                }),
                
                html.Button('🏝️ My Islands', id='menu-islands', n_clicks=0, style={
                    'width': '100%',
                    'padding': '15px',
                    'marginBottom': '10px',
                    'fontSize': '18px',
                    'fontWeight': 'bold',
                    'backgroundColor': '#9D4EDD',
                    'color': '#000000',
                    'border': 'none',
                    'borderRadius': '10px',
                    'cursor': 'pointer',
                    'fontFamily': 'Arial Black, sans-serif',
                    'boxShadow': '0 0 10px #9D4EDD'
                }),
                
                html.Button('📊 Player Statistics', id='menu-stats', n_clicks=0, style={
                    'width': '100%',
                    'padding': '15px',
                    'marginBottom': '10px',
                    'fontSize': '18px',
                    'fontWeight': 'bold',
                    'backgroundColor': '#FF006E',
                    'color': '#000000',
                    'border': 'none',
                    'borderRadius': '10px',
                    'cursor': 'pointer',
                    'fontFamily': 'Arial Black, sans-serif',
                    'boxShadow': '0 0 10px #FF006E'
                }),
                
                html.Button('📈 Analytics Dashboard', id='menu-dashboard', n_clicks=0, style={
                    'width': '100%',
                    'padding': '15px',
                    'marginBottom': '10px',
                    'fontSize': '18px',
                    'fontWeight': 'bold',
                    'backgroundColor': '#FF8800',
                    'color': '#000000',
                    'border': 'none',
                    'borderRadius': '10px',
                    'cursor': 'pointer',
                    'fontFamily': 'Arial Black, sans-serif',
                    'boxShadow': '0 0 10px #FF8800'
                }),
                
                html.Button('🎧 Social Listening', id='menu-social-listening', n_clicks=0, style={
                    'width': '100%',
                    'padding': '15px',
                    'marginBottom': '10px',
                    'fontSize': '18px',
                    'fontWeight': 'bold',
                    'backgroundColor': '#FFD700',
                    'color': '#000000',
                    'border': 'none',
                    'borderRadius': '10px',
                    'cursor': 'pointer',
                    'fontFamily': 'Arial Black, sans-serif',
                    'boxShadow': '0 0 10px #FFD700'
                })
            ])
        ]
    ),
    
    # Overlay for sidebar (darkens background when sidebar is open, click to close)
    html.Div(
        id='sidebar-overlay',
        n_clicks=0,
        style={
            'position': 'fixed',
            'top': '0',
            'left': '0',
            'width': '100%',
            'height': '100vh',
            'backgroundColor': 'rgba(0, 0, 0, 0.7)',
            'zIndex': '1999',
            'display': 'none',
            'cursor': 'pointer'
        }
    ),
    
    # Main container
    html.Div([
        # Header with hamburger menu
        html.Div([
            # Hamburger menu button
            html.Button(
                '☰',
                id='hamburger-menu',
                n_clicks=0,
                style={
                    'position': 'absolute',
                    'left': '20px',
                    'top': '20px',
                    'fontSize': '32px',
                    'backgroundColor': 'transparent',
                    'border': '2px solid #00D9FF',
                    'borderRadius': '10px',
                    'width': '60px',
                    'height': '60px',
                    'cursor': 'pointer',
                    'color': '#00D9FF',
                    'boxShadow': '0 0 15px #00D9FF',
                    'zIndex': '1000'
                }
            ),
            
            # User login display (top-right)
            html.Div(
                '👤 Logged in as Brickster123',
                style={
                    'position': 'absolute',
                    'right': '20px',
                    'top': '20px',
                    'fontSize': '16px',
                    'color': '#00D9FF',
                    'fontFamily': 'Arial, sans-serif',
                    'backgroundColor': 'rgba(0, 217, 255, 0.1)',
                    'border': '2px solid #00D9FF',
                    'borderRadius': '10px',
                    'padding': '12px 20px',
                    'boxShadow': '0 0 15px rgba(0, 217, 255, 0.5)',
                    'zIndex': '1000'
                }
            ),
            
            html.Div([
                html.H1(
                    '⚡ YOUR CREATOR HUB ⚡',
                    style={
                        'textAlign': 'center',
                        'color': '#00D9FF',
                        'fontFamily': 'Arial Black, sans-serif',
                        'fontSize': '42px',
                        'margin': '10px 0 5px 0',
                        'textShadow': '0 0 20px #FF006E, 0 0 30px #00D9FF',
                        'letterSpacing': '3px'
                    }
                )
            ])
        ], style={'position': 'relative'}),
        
        # Home content (globe, stats, insights, chatbot)
        html.Div(id='home-content', children=[
        
        # Globe visualization
        html.Div([
            dcc.Graph(
                id='globe-map',
                figure=initial_figure,  # Load with initial data
                config={
                    'displayModeBar': False,  # Hide all mode bar buttons
                    'displaylogo': False,
                    'scrollZoom': False  # Disable zoom
                },
                style={'height': '800px', 'width': '100%'}  # Match notebook: 800px height
            )
        ], style={'marginBottom': '10px'}),
        
        # Stats footer
        html.Div([
            html.Div([
                html.Span('🎮', style={'fontSize': '24px', 'marginRight': '10px'}),
                html.Span(id='total-sessions', style={'fontSize': '24px', 'fontWeight': 'bold', 'color': '#00D9FF'}),
                html.Span(' ACTIVE SESSIONS', style={'fontSize': '14px', 'color': '#FF006E', 'marginLeft': '10px'})
            ], style={
                'display': 'inline-block',
                'margin': '0 30px',
                'padding': '15px 30px',
                'backgroundColor': 'rgba(0, 217, 255, 0.1)',
                'border': '2px solid #00D9FF',
                'borderRadius': '10px'
            }),
            html.Div([
                html.Span('🌍', style={'fontSize': '24px', 'marginRight': '10px'}),
                html.Span(id='total-locations', style={'fontSize': '24px', 'fontWeight': 'bold', 'color': '#FF006E'}),
                html.Span(' LOCATIONS', style={'fontSize': '14px', 'color': '#00D9FF', 'marginLeft': '10px'})
            ], style={
                'display': 'inline-block',
                'margin': '0 30px',
                'padding': '15px 30px',
                'backgroundColor': 'rgba(255, 0, 110, 0.1)',
                'border': '2px solid #FF006E',
                'borderRadius': '10px'
            }),
            html.Div([
                html.Span('⏱️', style={'fontSize': '24px', 'marginRight': '10px'}),
                html.Span(id='avg-duration', style={'fontSize': '24px', 'fontWeight': 'bold', 'color': '#FF8800'}),
                html.Span(' MIN AVG', style={'fontSize': '14px', 'color': '#00D9FF', 'marginLeft': '10px'})
            ], style={
                'display': 'inline-block',
                'margin': '0 30px',
                'padding': '15px 30px',
                'backgroundColor': 'rgba(255, 136, 0, 0.1)',
                'border': '2px solid #FF8800',
                'borderRadius': '10px'
            })
        ], style={
            'textAlign': 'center',
            'marginTop': '30px',
            'marginBottom': '30px'
        }),
        
        # Last updated timestamp
        html.Div([
            html.Span('Last Updated: ', style={'color': '#888', 'fontSize': '12px'}),
            html.Span(id='last-updated', style={'color': '#00D9FF', 'fontSize': '12px', 'fontWeight': 'bold'})
        ], style={'textAlign': 'center', 'marginBottom': '40px'}),
        
        # Key Insights Section
        html.Div([
            html.H2(
                '📊 KEY INSIGHTS',
                style={
                    'textAlign': 'center',
                    'color': '#FF8800',
                    'fontFamily': 'Arial Black, sans-serif',
                    'fontSize': '28px',
                    'margin': '0 0 20px 0',
                    'textShadow': '0 0 15px #FF8800'
                }
            ),
            
            html.Div(
                id='insights-content',
                style={
                    'backgroundColor': 'rgba(20, 20, 30, 0.9)',
                    'border': '2px solid #00D9FF',
                    'borderRadius': '10px',
                    'padding': '30px',
                    'marginBottom': '40px',
                    'fontFamily': 'Arial, sans-serif',
                    'maxHeight': '600px',
                    'overflowY': 'auto'
                },
                children=[
                    html.Div('Loading insights...', style={
                        'color': '#00D9FF',
                        'textAlign': 'center',
                        'padding': '20px'
                    })
                ]
            )
        ], style={
            'maxWidth': '1200px',
            'margin': '0 auto',
            'padding': '0 20px'
        }),
        
            # AI Chatbot Section
            html.Div([
                html.H2(
                    '🤖 FORTNITE BOT',
                    style={
                        'textAlign': 'center',
                        'color': '#FF8800',
                        'fontFamily': 'Arial Black, sans-serif',
                        'fontSize': '28px',
                        'margin': '0 0 20px 0',
                        'textShadow': '0 0 15px #FF8800'
                    }
                ),
            
            # Chat history display
            html.Div(
                id='chat-history',
                style={
                    'backgroundColor': 'rgba(20, 20, 30, 0.9)',
                    'border': '2px solid #00D9FF',
                    'borderRadius': '10px',
                    'padding': '20px',
                    'height': '400px',
                    'overflowY': 'auto',
                    'marginBottom': '20px',
                    'fontFamily': 'Arial, sans-serif'
                },
                children=[
                    html.Div(
                        "👋 Hello! I'm Fortnite Bot. Ask me anything about the game analytics!",
                        style={
                            'backgroundColor': 'rgba(0, 217, 255, 0.2)',
                            'padding': '10px 15px',
                            'borderRadius': '10px',
                            'marginBottom': '10px',
                            'border': '1px solid #00D9FF',
                            'color': '#00D9FF'
                        }
                    )
                ]
            ),
            
            # Chat input area
            html.Div([
                dcc.Input(
                    id='chat-input',
                    type='text',
                    placeholder='Type your message here...',
                    style={
                        'width': 'calc(100% - 120px)',
                        'padding': '15px',
                        'fontSize': '16px',
                        'backgroundColor': '#1a1a2e',
                        'border': '2px solid #FF006E',
                        'borderRadius': '10px',
                        'color': '#ffffff',
                        'fontFamily': 'Arial, sans-serif',
                        'marginRight': '10px'
                    },
                    n_submit=0
                ),
                dcc.Loading(
                    id='button-loading',
                    type='circle',
                    color='#00D9FF',
                    parent_style={'display': 'inline-block'},
                    children=[
                        html.Button(
                            'SEND ▶',
                            id='chat-send-button',
                            n_clicks=0,
                            disabled=False,
                            style={
                                'width': '100px',
                                'padding': '15px',
                                'fontSize': '16px',
                                'fontWeight': 'bold',
                                'backgroundColor': '#FF006E',
                                'color': '#000000',
                                'border': '2px solid #00D9FF',
                                'borderRadius': '10px',
                                'cursor': 'pointer',
                                'fontFamily': 'Arial Black, sans-serif',
                                'boxShadow': '0 0 15px #FF006E'
                            }
                        )
                    ]
                )
            ], style={'display': 'flex', 'alignItems': 'center'})
            
        ], style={
            'maxWidth': '1200px',
            'margin': '0 auto',
            'padding': '0 20px'
        })
        
        ]),  # End of home-content
        
        # Dashboard content (hidden by default)
        html.Div(id='dashboard-content', style={'display': 'none'}, children=[
            html.H2(
                '📊 ANALYTICS DASHBOARD',
                style={
                    'textAlign': 'center',
                    'color': '#FF8800',
                    'fontFamily': 'Arial Black, sans-serif',
                    'fontSize': '28px',
                    'margin': '40px 0 20px 0',
                    'textShadow': '0 0 15px #FF8800'
                }
            ),
            
            html.Div([
                html.Iframe(
                    # Use environment variables for dashboard URL
                    src=f"https://{server_hostname}/embed/dashboardsv3/{DATABRICKS_DASHBOARD_ID}?o={DATABRICKS_WORKSPACE_ID}",
                    style={
                        'width': '100%',
                        'height': '1000px',
                        'border': 'none',
                        'borderRadius': '10px'
                    }
                )
            ], style={
                'maxWidth': '1400px',
                'margin': '0 auto',
                'padding': '0 20px 40px 20px'
            })
        ]),
        
        # Social Listening content (hidden by default)
        html.Div(id='social-listening-content', style={'display': 'none'}, children=[
            html.H2(
                '🎧 SOCIAL LISTENING',
                style={
                    'textAlign': 'center',
                    'color': '#FFD700',
                    'fontFamily': 'Arial Black, sans-serif',
                    'fontSize': '28px',
                    'margin': '40px 0 20px 0',
                    'textShadow': '0 0 15px #FFD700'
                }
            ),
            
            html.Div([
                html.Iframe(
                    # Use environment variable for social listening URL
                    src=SOCIAL_LISTENING_URL,
                    style={
                        'width': '100%',
                        'height': '1000px',
                        'border': 'none',
                        'borderRadius': '10px'
                    }
                )
            ], style={
                'maxWidth': '1400px',
                'margin': '0 auto',
                'padding': '0 20px 40px 20px'
            })
        ]),
        
    ], style={
        'backgroundColor': '#000000',
        'minHeight': '100vh',
        'padding': '20px',
        'fontFamily': 'Arial, sans-serif',
        'overflowX': 'hidden'
    }),
    
        # Interval component for auto-refresh and rotation
        dcc.Interval(
            id='interval-component',
            interval=100,  # Update every 100ms for smooth rotation
            n_intervals=0,
            disabled=False  # Ensure interval is enabled
        ),
        
        # Separate interval for insights loading (fires once immediately)
        dcc.Interval(
            id='insights-loader',
            interval=500,  # Fire after 500ms
            n_intervals=0,
            max_intervals=1  # Only fire once
        ),
    
], style={'backgroundColor': '#000000', 'margin': 0, 'padding': 0, 'overflowX': 'hidden'})

# ═══════════════════════════════════════════════════════════════════════════
# 📊 CALLBACKS
# ═══════════════════════════════════════════════════════════════════════════

print("🔧 Registering rotate_globe callback...")

@app.callback(
    [Output('globe-map', 'figure'),
     Output('rotation-angle', 'data')],
    [Input('interval-component', 'n_intervals')],
    [State('rotation-angle', 'data')]
)
def rotate_globe(n_intervals, current_angle):
    """Rotate the globe continuously and automatically"""
    # Only log first callback and data refresh events (not every 100ms)
    if n_intervals == 0:
        print(f"✅ rotate_globe callback initialized")
    
    # Fetch real data on first callback (n_intervals=1) and then every 3000 intervals (5 minutes at 100ms per interval)
    # This ensures we get real data immediately after app starts
    if n_intervals == 1 or n_intervals % 3000 == 0:
        # Use global variable to cache data between rotations
        global _cached_globe_data
        try:
            print(f"🔄 Fetching real data at interval {n_intervals}...")
            _cached_globe_data = fetch_active_players()
            print(f"✅ Data loaded: {len(_cached_globe_data)} locations")
        except Exception as e:
            print(f"❌ Failed to refresh data: {e}")
            import traceback
            traceback.print_exc()
            if '_cached_globe_data' not in globals():
                _cached_globe_data = create_sample_data()
    
    # Use cached data for smooth rotation
    df = _cached_globe_data if '_cached_globe_data' in globals() else create_sample_data()
    
    if df is None or len(df) == 0:
        print("ERROR: No data available!")
        return go.Figure(), current_angle
    
    # Auto-rotation
    if current_angle is None:
        current_angle = INITIAL_ROTATION
    
    new_angle = current_angle + ROTATION_SPEED
    
    # Keep angle in valid range
    if new_angle > 180:
        new_angle -= 360
    elif new_angle < -180:
        new_angle += 360
    
    fig = create_globe_figure(df, rotation_lon=new_angle)
    return fig, new_angle

@app.callback(
    [Output('total-sessions', 'children'),
     Output('total-locations', 'children'),
     Output('avg-duration', 'children'),
     Output('last-updated', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_stats(n):
    """Update statistics displayed below the globe"""
    # Fetch data on first call (n=0), second call (n=1), and then every 3000 intervals (5 minutes at 100ms per interval)
    if n == 0 or n == 1 or n % 3000 == 0:
        # Use cached data if available to match globe display
        global _cached_globe_data
        df = _cached_globe_data if '_cached_globe_data' in globals() and _cached_globe_data is not None else fetch_active_players()
        
        total_sessions = int(df['active_sessions'].sum())
        total_locations = len(df)
        avg_duration = df['avg_session_duration'].mean()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return (
            f"{total_sessions:,}",
            f"{total_locations:,}",
            f"{avg_duration:.1f}",
            timestamp
        )
    else:
        # Return current values without fetching new data
        from dash.exceptions import PreventUpdate
        raise PreventUpdate

print("🔧 Registering chat_interaction callback...")

@app.callback(
    [Output('chat-history', 'children'),
     Output('chat-input', 'value'),
     Output('conversation-history', 'data'),
     Output('chat-send-button', 'children'),
     Output('chat-send-button', 'disabled')],
    [Input('chat-send-button', 'n_clicks'),
     Input('chat-input', 'n_submit')],
    [State('chat-input', 'value'),
     State('conversation-history', 'data'),
     State('chat-history', 'children')]
)
def chat_interaction(n_clicks, n_submit, user_input, conversation_history, current_chat_display):
    """Handle chat interactions with the AI agent"""
    # Check if callback was triggered
    ctx = callback_context
    if not ctx.triggered or (n_clicks == 0 and n_submit == 0):
        # Initial load - return initial state
        from dash.exceptions import PreventUpdate
        raise PreventUpdate
    
    # Check if user actually entered something
    if not user_input or user_input.strip() == '':
        from dash.exceptions import PreventUpdate
        raise PreventUpdate
    
    # Add user message to conversation history
    conversation_history.append({
        'role': 'user',
        'content': user_input
    })
    
    # Create user message bubble
    user_message = html.Div([
        html.Div('You:', style={
            'fontWeight': 'bold',
            'color': '#FF006E',
            'marginBottom': '5px',
            'fontSize': '14px'
        }),
        html.Div(user_input, style={
            'backgroundColor': 'rgba(255, 0, 110, 0.2)',
            'padding': '10px 15px',
            'borderRadius': '10px',
            'border': '1px solid #FF006E',
            'color': '#ffffff'
        })
    ], style={'marginBottom': '15px'})
    
    # Add user message to chat display
    updated_chat = current_chat_display + [user_message]
    
    # Get AI response
    print(f"🤖 Sending message to AI agent: {user_input}")
    ai_response_text = get_ai_response(conversation_history)
    print(f"✅ AI response received: {ai_response_text[:100]}...")
    
    # Add AI response to conversation history
    conversation_history.append({
        'role': 'assistant',
        'content': ai_response_text
    })
    
    # Create AI message bubble with markdown support
    ai_message = html.Div([
        html.Div('Fortnite Bot:', style={
            'fontWeight': 'bold',
            'color': '#00D9FF',
            'marginBottom': '5px',
            'fontSize': '14px'
        }),
        html.Div([
            dcc.Markdown(
                ai_response_text,
                dangerously_allow_html=False,
                className='ai-markdown-content'
            )
        ], style={
            'backgroundColor': 'rgba(0, 217, 255, 0.2)',
            'padding': '10px 15px',
            'borderRadius': '10px',
            'border': '1px solid #00D9FF',
            'color': '#ffffff'
        })
    ], style={'marginBottom': '15px'})
    
    # Add AI message to chat display
    updated_chat = updated_chat + [ai_message]
    
    # Clear input and return updated chat with button enabled
    return updated_chat, '', conversation_history, 'SEND ▶', False

# ═══════════════════════════════════════════════════════════════════════════
# 📊 KEY INSIGHTS CALLBACKS
# ═══════════════════════════════════════════════════════════════════════════

print("🔧 Registering insights callback...")

# Fetch insights on page load using dedicated interval
@app.callback(
    [Output('insights-data', 'data'),
     Output('insights-content', 'children')],
    Input('insights-loader', 'n_intervals'),
    State('insights-data', 'data')
)
def fetch_and_display_insights(n_intervals, current_insights):
    """Fetch key insights from AI agent once on load and display them"""
    print(f"📊 Insights callback triggered: n_intervals={n_intervals}, has_data={current_insights is not None}")
    
    # Only fetch once
    if current_insights is not None:
        print("⏭️ Already have insights, skipping")
        from dash.exceptions import PreventUpdate
        raise PreventUpdate
    
    # Trigger will fire when n_intervals becomes 1 (after 500ms)
    if n_intervals == 0:
        print("⏳ Waiting for interval to trigger")
        from dash.exceptions import PreventUpdate
        raise PreventUpdate
    
    print("📊 Fetching weekly insights from AI agent...")
    
    # Create a conversation with just the insights request
    insights_request = [{
        'role': 'user',
        'content': 'What are my key insights for this week? Please organize your response into two sections: "Island Overview" and "Strategic Recommendations".'
    }]
    
    # Get response from AI agent
    insights_response = get_ai_response(insights_request)
    
    print(f"✅ Insights received: {len(insights_response)} characters")
    print(f"🔍 Raw response preview: {insights_response[:200]}")
    
    # Clean up markdown formatting issues
    # Multiple aggressive cleaning passes
    
    # Clean up markdown - remove all asterisks and bullet markers
    cleaned_lines = []
    for line in insights_response.split('\n'):
        # Remove lines that are ONLY asterisks (any number)
        stripped = line.strip()
        if stripped and re.match(r'^\*+$', stripped):
            print(f"🧹 Removing line with only asterisks: '{line}'")
            continue
        
        # Remove bullet point markers from lines (both * and -)
        # Remove leading "* " or "- " from lines
        cleaned_line = re.sub(r'^\s*[\*\-]\s+', '', line)
        cleaned_lines.append(cleaned_line)
    
    insights_response = '\n'.join(cleaned_lines)
    
    # Remove standalone ** patterns
    insights_response = re.sub(r'\n\s*\*+\s*\n', '\n\n', insights_response)
    insights_response = re.sub(r'^\s*\*+\s*\n', '', insights_response)
    insights_response = re.sub(r'\n\s*\*+\s*$', '', insights_response)
    
    # Remove multiple consecutive blank lines
    insights_response = re.sub(r'\n\s*\n\s*\n+', '\n\n', insights_response)
    
    # Trim leading/trailing whitespace
    insights_response = insights_response.strip()
    
    print(f"✅ Cleaned response: {len(insights_response)} characters")
    print(f"🔍 Cleaned preview: {insights_response[:200]}")
    
    # Store the insights
    insights_data = {
        'insights': insights_response,
        'timestamp': pd.Timestamp.now().isoformat()
    }
    
    # Parse and format the insights for display
    insights_text = insights_response
    
    # Parse timestamp for display
    try:
        ts = pd.Timestamp(insights_data['timestamp'])
        time_str = ts.strftime('%B %d, %Y at %I:%M %p')
    except:
        time_str = 'Recently'
    
    # Split insights into sections
    sections = []
    
    # Try to find "Island Overview" and "Strategic Recommendations" sections
    # Handle both plain text and markdown-formatted headers (e.g., **Header** or ## Header)
    if 'Island Overview' in insights_text and 'Strategic Recommendations' in insights_text:
        # Split on Strategic Recommendations (with or without markdown formatting)
        parts = re.split(r'\*{0,2}\s*Strategic Recommendations\s*\*{0,2}', insights_text, flags=re.IGNORECASE)
        
        # Extract island part and remove the header
        island_part = parts[0]
        island_part = re.sub(r'\*{0,2}\s*Island Overview\s*\*{0,2}', '', island_part, flags=re.IGNORECASE).strip()
        
        # Extract strategic part
        strategic_part = parts[1].strip() if len(parts) > 1 else ''
        
        # Clean up any remaining standalone ** at the start/end of sections
        island_part = re.sub(r'^\*+\s*', '', island_part)
        island_part = re.sub(r'\s*\*+$', '', island_part)
        strategic_part = re.sub(r'^\*+\s*', '', strategic_part)
        strategic_part = re.sub(r'\s*\*+$', '', strategic_part)
        
        sections.append(
            html.Div([
                html.H3('🏝️ Island Overview', style={
                    'color': '#00D9FF',
                    'fontFamily': 'Arial Black, sans-serif',
                    'fontSize': '20px',
                    'marginBottom': '15px',
                    'borderBottom': '2px solid #00D9FF',
                    'paddingBottom': '10px'
                }),
                dcc.Markdown(
                    island_part,
                    className='ai-markdown-content'
                )
            ], style={'marginBottom': '30px'})
        )
        
        sections.append(
            html.Div([
                html.H3('⚡ Strategic Recommendations', style={
                    'color': '#FF8800',
                    'fontFamily': 'Arial Black, sans-serif',
                    'fontSize': '20px',
                    'marginBottom': '15px',
                    'borderBottom': '2px solid #FF8800',
                    'paddingBottom': '10px'
                }),
                dcc.Markdown(
                    strategic_part,
                    className='ai-markdown-content'
                )
            ], style={'marginBottom': '20px'})
        )
    else:
        # If sections aren't clearly marked, show as one block
        sections.append(
            dcc.Markdown(insights_text, className='ai-markdown-content')
        )
    
    # Create the complete display content
    display_content = html.Div([
        html.Div(f'📅 Generated: {time_str}', style={
            'color': '#888',
            'fontSize': '12px',
            'marginBottom': '20px',
            'textAlign': 'center'
        }),
        *sections
    ])
    
    return insights_data, display_content

# ═══════════════════════════════════════════════════════════════════════════
# 🍔 NAVIGATION CALLBACKS
# ═══════════════════════════════════════════════════════════════════════════

print("🔧 Registering navigation callbacks...")

# Toggle sidebar
@app.callback(
    [Output('sidebar', 'style'),
     Output('sidebar-overlay', 'style'),
     Output('sidebar-open', 'data')],
    [Input('hamburger-menu', 'n_clicks'),
     Input('sidebar-overlay', 'n_clicks')],
    State('sidebar-open', 'data')
)
def toggle_sidebar(hamburger_clicks, overlay_clicks, is_open):
    """Toggle sidebar open/closed"""
    ctx = callback_context
    if not ctx.triggered:
        from dash.exceptions import PreventUpdate
        raise PreventUpdate
    
    # Toggle state
    new_state = not is_open
    
    # Sidebar style
    sidebar_style = {
        'position': 'fixed',
        'left': '0' if new_state else '-320px',
        'top': '0',
        'width': '300px',
        'height': '100vh',
        'backgroundColor': 'rgba(10, 10, 20, 0.98)',
        'border': '2px solid #00D9FF',
        'borderLeft': 'none',
        'zIndex': '2000',
        'transition': 'left 0.3s ease' if new_state else 'left 0.3s ease, visibility 0s linear 0.3s',
        'padding': '20px',
        'overflowY': 'auto',
        'visibility': 'visible' if new_state else 'hidden'
    }
    
    # Overlay style
    overlay_style = {
        'position': 'fixed',
        'top': '0',
        'left': '0',
        'width': '100%',
        'height': '100vh',
        'backgroundColor': 'rgba(0, 0, 0, 0.7)',
        'zIndex': '1999',
        'display': 'block' if new_state else 'none'
    }
    
    return sidebar_style, overlay_style, new_state

# Navigate between pages
@app.callback(
    [Output('current-page', 'data'),
     Output('home-content', 'style'),
     Output('dashboard-content', 'style'),
     Output('social-listening-content', 'style')],
    [Input('menu-home', 'n_clicks'),
     Input('menu-dashboard', 'n_clicks'),
     Input('menu-islands', 'n_clicks'),
     Input('menu-stats', 'n_clicks'),
     Input('menu-social-listening', 'n_clicks')],
    [State('current-page', 'data')]
)
def navigate_pages(home_clicks, dashboard_clicks, islands_clicks, stats_clicks, social_clicks, current_page):
    """Navigate between home, dashboard, and social listening pages"""
    ctx = callback_context
    if not ctx.triggered:
        # Initial load - show home
        return 'home', {'display': 'block'}, {'display': 'none'}, {'display': 'none'}
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'menu-home':
        print("📍 Navigating to Home")
        return 'home', {'display': 'block'}, {'display': 'none'}, {'display': 'none'}
    elif trigger_id == 'menu-dashboard':
        print("📍 Navigating to Analytics Dashboard")
        return 'dashboard', {'display': 'none'}, {'display': 'block'}, {'display': 'none'}
    elif trigger_id == 'menu-social-listening':
        print("📍 Navigating to Social Listening")
        return 'social-listening', {'display': 'none'}, {'display': 'none'}, {'display': 'block'}
    elif trigger_id == 'menu-islands' or trigger_id == 'menu-stats':
        print(f"⏸️ {trigger_id} clicked - not yet implemented")
        # Don't navigate, keep current page
        from dash.exceptions import PreventUpdate
        raise PreventUpdate
    
    from dash.exceptions import PreventUpdate
    raise PreventUpdate

# ═══════════════════════════════════════════════════════════════════════════
# 🏃 RUN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("=" * 80)
    print("🌍 FORTNITE-STYLE GLOBE DASHBOARD - DATABRICKS APP")
    print("=" * 80)
    print(f"\n📊 Configuration:")
    print(f"   • Refresh Interval: {REFRESH_INTERVAL/1000}s")
    print(f"   • Rotation Speed: {ROTATION_SPEED}°/frame")
    print(f"   • Schema: {SCHEMA_NAME}")
    print(f"\n🚀 Starting server...")
    print(f"   • Local: http://localhost:8050")
    print(f"   • Databricks: Deploy via Databricks Apps")
    print("\n" + "=" * 80)
    
    # Run the app
    app.run_server(
        debug=False,  # Set to False for production
        host='0.0.0.0',  # Allow external connections (required for Databricks)
        port=8050
    )

