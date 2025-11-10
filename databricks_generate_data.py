"""
Databricks Synthetic Data Generator for Fortnite-Style Game Analytics
Run this in a Databricks notebook to generate tables directly in your workspace
Tables will be saved to: <catalog>.<schema> (configure SCHEMA_NAME below)
"""

# Databricks notebook source
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from pyspark.sql import SparkSession

# Initialize Spark session (already available in Databricks as 'spark')
# spark = SparkSession.builder.getOrCreate()

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# COMMAND ----------
# Configuration
NUM_PLAYERS = 1000
NUM_SESSIONS = 10000
NUM_TRANSACTIONS = 2500
NUM_ISLANDS = 30
START_DATE = datetime(2024, 5, 1)  # 6 months of data
END_DATE = datetime(2024, 10, 31)
SCHEMA_NAME = "users.your_username"  # ⚠️ CHANGE THIS to your Databricks catalog.schema

print(f"Configuration:")
print(f"  Players: {NUM_PLAYERS}")
print(f"  Sessions: {NUM_SESSIONS}")
print(f"  Transactions: {NUM_TRANSACTIONS}")
print(f"  Date Range: {START_DATE.date()} to {END_DATE.date()}")
print(f"  Target Schema: {SCHEMA_NAME}")

# COMMAND ----------
# Geographic data with coordinates
REGIONS = {
    'LATAM': {
        'cities': [
            {'city': 'São Paulo', 'state': 'SP', 'country': 'Brazil', 'lat': -23.5505, 'lon': -46.6333, 'weight': 0.25},
            {'city': 'Rio de Janeiro', 'state': 'RJ', 'country': 'Brazil', 'lat': -22.9068, 'lon': -43.1729, 'weight': 0.15},
            {'city': 'Mexico City', 'state': 'CDMX', 'country': 'Mexico', 'lat': 19.4326, 'lon': -99.1332, 'weight': 0.20},
            {'city': 'Buenos Aires', 'state': 'BA', 'country': 'Argentina', 'lat': -34.6037, 'lon': -58.3816, 'weight': 0.12},
            {'city': 'Bogotá', 'state': 'DC', 'country': 'Colombia', 'lat': 4.7110, 'lon': -74.0721, 'weight': 0.10},
            {'city': 'Santiago', 'state': 'RM', 'country': 'Chile', 'lat': -33.4489, 'lon': -70.6693, 'weight': 0.08},
            {'city': 'Lima', 'state': 'LIM', 'country': 'Peru', 'lat': -12.0464, 'lon': -77.0428, 'weight': 0.06},
            {'city': 'Guadalajara', 'state': 'JAL', 'country': 'Mexico', 'lat': 20.6597, 'lon': -103.3496, 'weight': 0.04},
        ],
        'device_weights': {'mobile': 0.65, 'pc': 0.25, 'console': 0.10},
        'avg_transaction': (5, 20),
    },
    'NA': {
        'cities': [
            {'city': 'Los Angeles', 'state': 'CA', 'country': 'USA', 'lat': 34.0522, 'lon': -118.2437, 'weight': 0.20},
            {'city': 'New York', 'state': 'NY', 'country': 'USA', 'lat': 40.7128, 'lon': -74.0060, 'weight': 0.18},
            {'city': 'Chicago', 'state': 'IL', 'country': 'USA', 'lat': 41.8781, 'lon': -87.6298, 'weight': 0.12},
            {'city': 'Toronto', 'state': 'ON', 'country': 'Canada', 'lat': 43.6532, 'lon': -79.3832, 'weight': 0.15},
            {'city': 'Houston', 'state': 'TX', 'country': 'USA', 'lat': 29.7604, 'lon': -95.3698, 'weight': 0.10},
            {'city': 'Atlanta', 'state': 'GA', 'country': 'USA', 'lat': 33.7490, 'lon': -84.3880, 'weight': 0.10},
            {'city': 'Miami', 'state': 'FL', 'country': 'USA', 'lat': 25.7617, 'lon': -80.1918, 'weight': 0.08},
            {'city': 'Seattle', 'state': 'WA', 'country': 'USA', 'lat': 47.6062, 'lon': -122.3321, 'weight': 0.07},
        ],
        'device_weights': {'mobile': 0.35, 'pc': 0.40, 'console': 0.25},
        'avg_transaction': (10, 50),
    },
    'EU': {
        'cities': [
            {'city': 'London', 'state': 'ENG', 'country': 'UK', 'lat': 51.5074, 'lon': -0.1278, 'weight': 0.25},
            {'city': 'Paris', 'state': 'IDF', 'country': 'France', 'lat': 48.8566, 'lon': 2.3522, 'weight': 0.20},
            {'city': 'Berlin', 'state': 'BE', 'country': 'Germany', 'lat': 52.5200, 'lon': 13.4050, 'weight': 0.15},
            {'city': 'Madrid', 'state': 'MD', 'country': 'Spain', 'lat': 40.4168, 'lon': -3.7038, 'weight': 0.15},
            {'city': 'Amsterdam', 'state': 'NH', 'country': 'Netherlands', 'lat': 52.3676, 'lon': 4.9041, 'weight': 0.10},
            {'city': 'Rome', 'state': 'LAZ', 'country': 'Italy', 'lat': 41.9028, 'lon': 12.4964, 'weight': 0.10},
            {'city': 'Stockholm', 'state': 'ST', 'country': 'Sweden', 'lat': 59.3293, 'lon': 18.0686, 'weight': 0.05},
        ],
        'device_weights': {'mobile': 0.40, 'pc': 0.45, 'console': 0.15},
        'avg_transaction': (8, 40),
    },
    'ASIA': {
        'cities': [
            {'city': 'Tokyo', 'state': 'TYO', 'country': 'Japan', 'lat': 35.6762, 'lon': 139.6503, 'weight': 0.30},
            {'city': 'Seoul', 'state': 'SEO', 'country': 'South Korea', 'lat': 37.5665, 'lon': 126.9780, 'weight': 0.25},
            {'city': 'Singapore', 'state': 'SG', 'country': 'Singapore', 'lat': 1.3521, 'lon': 103.8198, 'weight': 0.20},
            {'city': 'Mumbai', 'state': 'MH', 'country': 'India', 'lat': 19.0760, 'lon': 72.8777, 'weight': 0.15},
            {'city': 'Sydney', 'state': 'NSW', 'country': 'Australia', 'lat': -33.8688, 'lon': 151.2093, 'weight': 0.10},
        ],
        'device_weights': {'mobile': 0.70, 'pc': 0.20, 'console': 0.10},
        'avg_transaction': (3, 25),
    }
}

ISLAND_THEMES = [
    'Battle Royale', 'Team Deathmatch', 'Capture the Flag', 'Zone Wars',
    'Box Fights', 'Edit Course', 'Parkour', 'Racing', 'Survival', 'Creative Sandbox',
    'Prop Hunt', 'Hide and Seek', 'Red vs Blue', 'Gun Game', 'Murder Mystery'
]

TRANSACTION_TYPES = [
    'purchase_vbucks', 'purchase_skin', 'purchase_emote', 
    'purchase_pickaxe', 'purchase_glider', 'purchase_battle_pass',
    'purchase_bundle', 'refund'
]

# COMMAND ----------
# Helper Functions

def get_region_weights(date):
    """Returns region probability weights based on date (LATAM growth over time)"""
    months_elapsed = (date - START_DATE).days / 30
    
    if months_elapsed < 2:
        return {'NA': 0.60, 'EU': 0.25, 'ASIA': 0.10, 'LATAM': 0.05}
    elif months_elapsed < 4:
        return {'NA': 0.50, 'EU': 0.20, 'ASIA': 0.10, 'LATAM': 0.20}
    else:
        return {'NA': 0.45, 'EU': 0.15, 'ASIA': 0.08, 'LATAM': 0.32}

def select_city_from_region(region):
    """Select a city from a region based on weights"""
    cities = REGIONS[region]['cities']
    weights = [c['weight'] for c in cities]
    city_data = random.choices(cities, weights=weights, k=1)[0]
    return city_data

def generate_ip_address():
    """Generate a random IP address (as integer)"""
    return random.randint(16777216, 3758096383)

# COMMAND ----------
# Generate Players Table

def generate_players():
    """Generate player table with LATAM growth over time"""
    print("Generating players...")
    players = []
    
    for player_id in range(1, NUM_PLAYERS + 1):
        # Distribute player creation dates across time period
        days_since_start = int(np.random.exponential(scale=60))
        if days_since_start > (END_DATE - START_DATE).days:
            days_since_start = (END_DATE - START_DATE).days
        
        create_date = START_DATE + timedelta(days=days_since_start)
        
        # Select region based on create date (LATAM growth!)
        region_weights = get_region_weights(create_date)
        region = random.choices(
            list(region_weights.keys()),
            weights=list(region_weights.values()),
            k=1
        )[0]
        
        # Select city from region
        city_data = select_city_from_region(region)
        
        # Device type based on region
        device_weights = REGIONS[region]['device_weights']
        device_type = random.choices(
            list(device_weights.keys()),
            weights=list(device_weights.values()),
            k=1
        )[0]
        
        # Player level (newer players have lower levels)
        days_active = (END_DATE - create_date).days
        player_level = max(1, int(np.random.gamma(2, 3) * (days_active / 30)))
        
        # Total time played (correlated with level)
        total_time_played = int(player_level * np.random.uniform(20, 60))
        
        # Last login (some players have churned)
        if random.random() < 0.15:  # 15% churned
            last_login_date = create_date + timedelta(days=random.randint(0, min(14, days_active)))
        else:
            # Active players logged in recently
            days_since_last = int(np.random.exponential(scale=3))
            last_login_date = END_DATE - timedelta(days=min(days_since_last, days_active))
        
        players.append({
            'player_id': player_id,
            'ip_address': generate_ip_address(),
            'create_date': create_date,
            'city': city_data['city'],
            'state': city_data['state'],
            'country': city_data['country'],
            'latitude': city_data['lat'],
            'longitude': city_data['lon'],
            'player_level': player_level,
            'device_type': device_type,
            'total_time_played': total_time_played,
            'last_login_date': last_login_date,
            'region': region  # Keep for session generation
        })
    
    return pd.DataFrame(players)

players_df = generate_players()
print(f"✓ Generated {len(players_df)} players")

# COMMAND ----------
# Generate Islands Table

def generate_islands():
    """Generate custom island/game mode table"""
    print("Generating islands...")
    islands = []
    
    for island_id in range(1, NUM_ISLANDS + 1):
        theme = random.choice(ISLAND_THEMES)
        create_date = START_DATE + timedelta(days=random.randint(0, 30))
        
        islands.append({
            'island_id': island_id,
            'creator_player_id': random.randint(1, min(100, NUM_PLAYERS)),
            'island_name': f"{theme} Arena {island_id}",
            'category': theme,
            'create_date': create_date,
            'total_plays': 0,  # Will be calculated from sessions
            'avg_rating': round(np.random.uniform(3.5, 5.0), 2)
        })
    
    return pd.DataFrame(islands)

islands_df = generate_islands()
print(f"✓ Generated {len(islands_df)} islands")

# COMMAND ----------
# Generate Sessions Table

def generate_sessions(players_df):
    """Generate session table with realistic patterns"""
    print("Generating sessions...")
    sessions = []
    
    # Weight towards active players
    active_players = players_df[players_df['last_login_date'] > END_DATE - timedelta(days=14)]
    player_weights = np.ones(len(players_df))
    player_weights[active_players.index] *= 5
    player_weights = player_weights / player_weights.sum()
    
    for session_id in range(1, NUM_SESSIONS + 1):
        # Select player
        player_idx = np.random.choice(len(players_df), p=player_weights)
        player = players_df.iloc[player_idx]
        
        # Session date between player create and last login
        start = player['create_date']
        end = min(player['last_login_date'], END_DATE)
        if end <= start:
            end = start + timedelta(days=1)
        
        days_range = (end - start).days
        session_date = start + timedelta(days=random.randint(0, max(1, days_range)))
        
        # Time of day (peak hours vary by region)
        if player['region'] == 'LATAM':
            # LATAM peak hours 7-11 PM (indices 19-23)
            hour_probs = np.array([0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.02, 0.03, 0.04, 0.04, 0.03, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.10, 0.08, 0.06, 0.03])
            hour_probs = hour_probs / hour_probs.sum()  # Normalize to sum to 1.0
            hour = int(np.random.choice(range(24), p=hour_probs))
        else:
            # More evenly distributed
            hour_probs = np.array([0.01, 0.01, 0.01, 0.01, 0.01, 0.02, 0.02, 0.03, 0.04, 0.04, 0.04, 0.04, 0.05, 0.05, 0.06, 0.07, 0.07, 0.08, 0.09, 0.09, 0.08, 0.06, 0.04, 0.02])
            hour_probs = hour_probs / hour_probs.sum()  # Normalize to sum to 1.0
            hour = int(np.random.choice(range(24), p=hour_probs))
        
        start_time = session_date.replace(hour=hour, minute=random.randint(0, 59))
        
        # Session duration
        if player['device_type'] == 'mobile':
            duration_minutes = int(np.random.gamma(2, 8))
        else:
            duration_minutes = int(np.random.gamma(3, 12))
        
        duration_minutes = max(3, min(duration_minutes, 120))
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Performance metrics
        score = int(np.random.gamma(5, 200))
        objectives_completed = random.randint(0, 10)
        deaths = random.randint(0, 15)
        eliminations = random.randint(0, 20)
        
        # Session status
        status_weights = [0.75, 0.20, 0.05] if player['device_type'] != 'mobile' else [0.65, 0.30, 0.05]
        status = random.choices(['completed', 'abandoned', 'crashed'], weights=status_weights)[0]
        
        sessions.append({
            'session_id': session_id,
            'player_id': player['player_id'],
            'start_time': start_time,
            'end_time': end_time,
            'ip_address': player['ip_address'],
            'island_id': random.randint(1, NUM_ISLANDS),
            'score': score,
            'objectives_completed': objectives_completed,
            'deaths': deaths,
            'eliminations': eliminations,
            'time_played_minutes': duration_minutes,
            'status': status,
            'device_type': player['device_type']
        })
    
    return pd.DataFrame(sessions)

sessions_df = generate_sessions(players_df)
print(f"✓ Generated {len(sessions_df)} sessions")

# COMMAND ----------
# Generate Transactions Table

def generate_transactions(players_df, sessions_df):
    """Generate transaction table with regional patterns"""
    print("Generating transactions...")
    transactions = []
    
    # Only ~40% of players make purchases
    paying_players = players_df.sample(frac=0.4)
    
    transaction_id = 1
    for _, player in paying_players.iterrows():
        # Number of transactions per player
        if random.random() < 0.05:  # 5% whales
            num_trans = random.randint(10, 30)
        elif random.random() < 0.25:  # 25% dolphins
            num_trans = random.randint(3, 10)
        else:  # 70% minnows
            num_trans = random.randint(1, 3)
        
        player_sessions = sessions_df[sessions_df['player_id'] == player['player_id']]
        
        for _ in range(num_trans):
            # Transaction date around a session
            if len(player_sessions) > 0:
                session = player_sessions.sample(1).iloc[0]
                trans_date = session['start_time'] + timedelta(hours=random.randint(-2, 2))
            else:
                trans_date = player['create_date'] + timedelta(days=random.randint(0, 30))
            
            # Amount based on region
            region = player['region']
            min_amt, max_amt = REGIONS[region]['avg_transaction']
            
            # Transaction type affects amount
            trans_type = random.choice(TRANSACTION_TYPES)
            if trans_type == 'purchase_battle_pass':
                amount = random.randint(950, 1000)
            elif trans_type == 'purchase_bundle':
                amount = random.randint(1500, 3000)
            elif trans_type == 'refund':
                amount = -random.randint(500, 2000)
            else:
                amount = random.randint(int(min_amt * 100), int(max_amt * 100))
            
            # Credit card (last 4 digits only)
            cc_last4 = random.randint(1000, 9999)
            
            transactions.append({
                'transaction_id': transaction_id,
                'player_id': player['player_id'],
                'type': trans_type,
                'timestamp': trans_date,
                'amount': amount,
                'credit_card_last4': cc_last4
            })
            transaction_id += 1
    
    return pd.DataFrame(transactions)

transactions_df = generate_transactions(players_df, sessions_df)
print(f"✓ Generated {len(transactions_df)} transactions")

# COMMAND ----------
# Generate Cohorts and Player_Cohorts Tables

def generate_cohorts():
    """Generate cohort definitions"""
    print("Generating cohorts...")
    cohorts = [
        {'cohort_id': 1, 'name': 'veteran_player', 'create_date': START_DATE},
        {'cohort_id': 2, 'name': 'new_player', 'create_date': START_DATE},
        {'cohort_id': 3, 'name': 'spenders', 'create_date': START_DATE},
        {'cohort_id': 4, 'name': 'mobile_players', 'create_date': START_DATE},
        {'cohort_id': 5, 'name': 'latam_players', 'create_date': START_DATE + timedelta(days=60)},
        {'cohort_id': 6, 'name': 'churned_players', 'create_date': START_DATE},
        {'cohort_id': 7, 'name': 'binge_players', 'create_date': START_DATE},
        {'cohort_id': 8, 'name': 'casual_players', 'create_date': START_DATE},
    ]
    return pd.DataFrame(cohorts)

def generate_player_cohorts(players_df, transactions_df):
    """Generate player_cohort junction table"""
    print("Generating player-cohort mappings...")
    player_cohorts = []
    
    for _, player in players_df.iterrows():
        player_id = player['player_id']
        assigned_cohorts = []
        
        # Veteran vs new
        if player['player_level'] >= 20:
            assigned_cohorts.append(1)
        elif (END_DATE - player['create_date']).days < 30:
            assigned_cohorts.append(2)
        
        # Spenders
        if player_id in transactions_df['player_id'].values:
            assigned_cohorts.append(3)
        
        # Mobile
        if player['device_type'] == 'mobile':
            assigned_cohorts.append(4)
        
        # LATAM
        if player['region'] == 'LATAM':
            assigned_cohorts.append(5)
        
        # Churned
        if (END_DATE - player['last_login_date']).days >= 14:
            assigned_cohorts.append(6)
        
        # Binge vs casual
        if player['total_time_played'] > 500:
            assigned_cohorts.append(7)
        elif player['total_time_played'] < 100:
            assigned_cohorts.append(8)
        
        for cohort_id in assigned_cohorts:
            player_cohorts.append({
                'player_id': player_id,
                'cohort_id': cohort_id
            })
    
    return pd.DataFrame(player_cohorts)

cohorts_df = generate_cohorts()
player_cohorts_df = generate_player_cohorts(players_df, transactions_df)

print(f"✓ Generated {len(cohorts_df)} cohorts")
print(f"✓ Generated {len(player_cohorts_df)} player-cohort mappings")

# COMMAND ----------
# Calculate derived fields

# Update island total_plays from sessions
island_plays = sessions_df.groupby('island_id').size()
islands_df['total_plays'] = islands_df['island_id'].map(island_plays).fillna(0).astype(int)

# Calculate lifetime_spend for players
player_spend = transactions_df[transactions_df['amount'] > 0].groupby('player_id')['amount'].sum()
players_df['lifetime_spend'] = players_df['player_id'].map(player_spend).fillna(0).astype(int)

# Remove helper column from players
players_df = players_df.drop(columns=['region'])

print("✓ Calculated derived fields")

# COMMAND ----------
# Display summary statistics

print("\n" + "=" * 60)
print("DATA SUMMARY - LATAM GROWTH STORY")
print("=" * 60)

# Regional distribution
print("\nPlayer Distribution by Region:")
region_dist = players_df.groupby('country').size().sort_values(ascending=False).head(10)
for country, count in region_dist.items():
    pct = (count / len(players_df)) * 100
    print(f"  {country:20s}: {count:4d} players ({pct:5.1f}%)")

# Device distribution
print("\nDevice Type Distribution:")
device_counts = players_df['device_type'].value_counts()
for device, count in device_counts.items():
    pct = (count / len(players_df)) * 100
    print(f"  {device:8s}: {count:4d} players ({pct:5.1f}%)")

# Transaction stats
total_revenue = transactions_df[transactions_df['amount'] > 0]['amount'].sum() / 100
print(f"\nTotal Revenue: ${total_revenue:,.2f}")
print(f"Paying Players: {len(transactions_df['player_id'].unique())} ({len(transactions_df['player_id'].unique())/len(players_df)*100:.1f}%)")

# Cohort distribution
print("\nCohort Membership:")
cohort_sizes = player_cohorts_df.groupby('cohort_id').size()
for cohort_id, size in cohort_sizes.items():
    cohort_name = cohorts_df[cohorts_df['cohort_id'] == cohort_id]['name'].values[0]
    print(f"  {cohort_name:20s}: {size:4d} players")

# COMMAND ----------
# Save tables to Databricks

print("\n" + "=" * 60)
print(f"SAVING TABLES TO {SCHEMA_NAME}")
print("=" * 60)

# Convert pandas DataFrames to Spark DataFrames and save as tables
spark_players = spark.createDataFrame(players_df)
spark_players.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.players")
print(f"✓ Saved {SCHEMA_NAME}.players ({len(players_df)} records)")

spark_islands = spark.createDataFrame(islands_df)
spark_islands.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.islands")
print(f"✓ Saved {SCHEMA_NAME}.islands ({len(islands_df)} records)")

spark_sessions = spark.createDataFrame(sessions_df)
spark_sessions.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.sessions")
print(f"✓ Saved {SCHEMA_NAME}.sessions ({len(sessions_df)} records)")

spark_transactions = spark.createDataFrame(transactions_df)
spark_transactions.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.transactions")
print(f"✓ Saved {SCHEMA_NAME}.transactions ({len(transactions_df)} records)")

spark_cohorts = spark.createDataFrame(cohorts_df)
spark_cohorts.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.cohorts")
print(f"✓ Saved {SCHEMA_NAME}.cohorts ({len(cohorts_df)} records)")

spark_player_cohorts = spark.createDataFrame(player_cohorts_df)
spark_player_cohorts.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.player_cohorts")
print(f"✓ Saved {SCHEMA_NAME}.player_cohorts ({len(player_cohorts_df)} records)")

# COMMAND ----------
# Verify tables were created

print("\n" + "=" * 60)
print("VERIFICATION")
print("=" * 60)

tables = spark.sql(f"SHOW TABLES IN {SCHEMA_NAME}").collect()
print(f"\nTables in {SCHEMA_NAME}:")
for table in tables:
    table_name = table.tableName
    count = spark.sql(f"SELECT COUNT(*) as cnt FROM {SCHEMA_NAME}.{table_name}").collect()[0].cnt
    print(f"  ✓ {table_name:20s}: {count:6d} records")

# COMMAND ----------
# Sample queries to get started

print("\n" + "=" * 60)
print("SAMPLE QUERIES TO GET YOU STARTED")
print("=" * 60)

print("\n-- View LATAM player growth over time")
print(f"SELECT DATE_TRUNC('month', create_date) as month, country, COUNT(*) as new_players")
print(f"FROM {SCHEMA_NAME}.players")
print(f"WHERE country IN ('Brazil', 'Mexico', 'Argentina', 'Colombia', 'Chile')")
print(f"GROUP BY month, country")
print(f"ORDER BY month, new_players DESC")

print("\n-- Find churned players (not played in 14+ days)")
print(f"SELECT player_id, city, country, last_login_date, DATEDIFF(CURRENT_DATE(), last_login_date) as days_inactive")
print(f"FROM {SCHEMA_NAME}.players")
print(f"WHERE DATEDIFF(CURRENT_DATE(), last_login_date) >= 14")
print(f"ORDER BY days_inactive DESC")

print("\n-- Top performing islands")
print(f"SELECT island_name, category, total_plays, avg_rating")
print(f"FROM {SCHEMA_NAME}.islands")
print(f"ORDER BY total_plays DESC")
print(f"LIMIT 10")

print("\n-- Session metrics by device type")
print(f"SELECT s.device_type, COUNT(*) as sessions, AVG(s.time_played_minutes) as avg_minutes")
print(f"FROM {SCHEMA_NAME}.sessions s")
print(f"GROUP BY s.device_type")

print("\n-- Revenue by country")
print(f"SELECT p.country, COUNT(DISTINCT t.player_id) as paying_players, SUM(t.amount)/100 as total_revenue")
print(f"FROM {SCHEMA_NAME}.transactions t")
print(f"JOIN {SCHEMA_NAME}.players p ON t.player_id = p.player_id")
print(f"WHERE t.amount > 0")
print(f"GROUP BY p.country")
print(f"ORDER BY total_revenue DESC")

print("\n" + "=" * 60)
print("DATA GENERATION COMPLETE!")
print("=" * 60)
print(f"\n🎮 All tables saved to: {SCHEMA_NAME}")
print("🌎 Story: LATAM playerbase grew from 5% to 32% over 6 months!")
print("📱 Mobile-first LATAM market with unique engagement patterns")
print("💰 Growing monetization opportunity in emerging markets")
print("\nNext steps:")
print("  1. Build your dashboard with the spinning globe visualization")
print("  2. Integrate Agent Bricks for AI-powered insights")
print("  3. Create churn, session, and revenue charts")
print("  4. Demo the LATAM growth story! 🚀")

