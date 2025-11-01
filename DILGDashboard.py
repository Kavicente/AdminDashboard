# DILGDashboard.py
import requests
import json
from collections import Counter
from datetime import datetime
import pytz

ALERTNOW_API = "https://alertnow-wi0n.onrender.com"

def fetch_table(table_name):
    try:
        response = requests.get(f"{ALERTNOW_API}/api/{table_name}")
        return response.json() if response.status_code == 200 else []
    except:
        return []

def get_dilg_dashboard_data():
    manila = pytz.timezone('Asia/Manila')
    current_datetime = datetime.now(manila).strftime('%B %d, %Y - %I:%M %p')

    # Fetch all
    barangay = fetch_table('barangay_response') + fetch_table('barangay_fire_response') + fetch_table('barangay_crime_response') + fetch_table('barangay_health_response')
    cdrrmo = fetch_table('cdrrmo_response')
    bfp = fetch_table('bfp_response') + fetch_table('pnp_fire_response')
    health = fetch_table('health_response') + fetch_table('hospital_response') + fetch_table('barangay_health_response')
    pnp = fetch_table('pnp_response') + fetch_table('pnp_crime_response')
    crime = fetch_table('barangay_crime_response') + fetch_table('pnp_crime_response')

    # Barangays
    with open('static/barangay.txt', 'r') as f:
        barangays = [line.strip() for line in f if line.strip()]

    # Heatmap
    heatmap = Counter([f"{item.get('lat',14.6760)},{item.get('lon',121.0437)}" for item in barangay + cdrrmo + bfp + health + pnp])
    heatmap_data = [{'lat': float(k.split(',')[0]), 'lon': float(k.split(',')[1]), 'count': v, 'barangay': 'Multiple'} for k,v in heatmap.items()]

    # Count field
    def count_field(items, field):
        return dict(Counter([str(item.get(field, 'N/A')) for item in items]))

    # Calculate total incidents
    total_incidents = len(barangay + cdrrmo + bfp + health + pnp)
    
    return {
        'current_datetime': current_datetime,
        'barangays': barangays,
        'heatmap': json.dumps(heatmap_data),
        'stats': {
            'total': total_incidents
        },
        'responded_count': len([x for x in (barangay + cdrrmo + bfp + health + pnp) if x.get('responded')]),
        'pending_count': len([x for x in (barangay + cdrrmo + bfp + health + pnp) if not x.get('responded')]),

        'alerts_per_barangay': json.dumps(count_field(barangay, 'barangay')),
        'alerts_cdrrmo': json.dumps(len(cdrrmo)),
        'alerts_bfp': json.dumps(len(bfp)),
        'alerts_health': json.dumps(len(health)),
        'alerts_pnp': json.dumps(len(pnp)),

        # Road
        'road_cause': json.dumps(count_field(cdrrmo + pnp + barangay, 'accident_cause')),
        'road_type': json.dumps(count_field(cdrrmo + pnp + barangay, 'accident_type')),
        'driver_gender': json.dumps(count_field(cdrrmo + pnp + barangay, 'driver_gender')),
        'vehicle_type': json.dumps(count_field(cdrrmo + pnp + barangay, 'vehicle_type')),
        'driver_age': json.dumps(count_field(cdrrmo + pnp + barangay, 'driver_age_group')),
        'driver_condition': json.dumps(count_field(cdrrmo + pnp + barangay, 'driver_condition')),

        # Fire
        'fire_cause': json.dumps(count_field(bfp + barangay, 'fire_cause')),
        'fire_weather': json.dumps(count_field(bfp + barangay, 'weather')),
        'fire_severity': json.dumps(count_field(bfp + barangay, 'severity')),

        # Health
        'health_type': json.dumps(count_field(health, 'emergency_type')),
        'health_cause': json.dumps(count_field(health, 'cause')),
        'health_weather': json.dumps(count_field(health, 'weather')),
        'patient_age': json.dumps(count_field(health, 'patient_age_group')),
        'patient_gender': json.dumps(count_field(health, 'patient_gender')),

        # Crime
        'crime_type': json.dumps(count_field(crime, 'crime_type')),
        'crime_cause': json.dumps(count_field(crime, 'cause')),
        'crime_level': json.dumps(count_field(crime, 'crime_level')),
        'suspect_gender': json.dumps(count_field(crime, 'suspect_gender')),
        'victim_gender': json.dumps(count_field(crime, 'victim_gender')),
        'suspect_age': json.dumps(count_field(crime, 'suspect_age_group')),
        'victim_age': json.dumps(count_field(crime, 'victim_age_group')),
    }