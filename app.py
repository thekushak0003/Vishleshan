import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import warnings
import time
warnings.filterwarnings('ignore')

# Page config
st.set_page_config(
    page_title="LMN Smart Cities - Integrated Analytics Platform",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    .stMetric label {
        color: white !important;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: black;
        text-align: center;
        margin: 10px 0;
    }
    .alert-critical {
        background-color: #ff4444;
        padding: 15px;
        border-radius: 8px;
        color: white;
        margin: 10px 0;
        font-weight: bold;
    }
    .alert-warning {
        background-color: #ffbb33;
        padding: 15px;
        border-radius: 8px;
        color: #000;
        margin: 10px 0;
        font-weight: bold;
    }
    .alert-success {
        background-color: #00C851;
        padding: 15px;
        border-radius: 8px;
        color: white;
        margin: 10px 0;
        font-weight: bold;
    }
    .insight-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 10px 0;
    }
    .recommendation {
        background-color: #e8f5e9;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #4caf50;
        margin: 10px 0;
    }
    .pipeline-box {
        background-color: #e3f2fd;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #2196f3;
        margin: 10px 0;
    }
    .processing-box {
        background-color: #f3e5f5;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #9c27b0;
        margin: 10px 0;
    }
    h1, h2, h3 {
        color: #667eea;
    }
    .source-active {
        background-color: #00C851;
        padding: 10px;
        border-radius: 5px;
        color: white;
        margin: 5px;
        text-align: center;
    }
    .source-inactive {
        background-color: #ffbb33;
        padding: 10px;
        border-radius: 5px;
        color: #000;
        margin: 5px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    try:
        grievances = pd.read_csv('pune_citizen_grievances.csv')
        grievances['Date'] = pd.to_datetime(grievances['Date'])
        
        energy = pd.read_csv('pune_energy_consumption.csv')
        energy['Date'] = pd.to_datetime(energy['Date'])
        
        traffic = pd.read_csv('pune_traffic_flow.csv')
        traffic['Date'] = pd.to_datetime(traffic['Date'])
        
        waste = pd.read_csv('pune_waste_management.csv')
        waste['Date'] = pd.to_datetime(waste['Date'])
        
        return grievances, energy, traffic, waste
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None, None

# Calculate KPIs
def calculate_kpis(grievances, energy, traffic, waste):
    avg_energy = energy['Energy_Consumption_kWh'].mean()
    power_cuts = energy['Power_Cut_Flag'].sum()
    voltage_issues = (energy['Grid_Voltage'] < 220).sum()
    
    avg_congestion = traffic['Congestion_Index'].mean()
    peak_congestion = traffic['Congestion_Index'].max()
    flow_efficiency = 1 - (avg_congestion / 100)
    
    avg_bin_fill = waste['Avg_Bin_Fill_Level_Percent'].mean()
    missed_pickups = waste['Missed_Pickups'].sum()
    avg_segregation = waste['Segregation_Efficiency_Percent'].mean()
    
    total_grievances = len(grievances)
    open_grievances = len(grievances[grievances['Status'] == 'Open'])
    critical_issues = len(grievances[(grievances['Status'] == 'Open') & (grievances['SLA_Days'] <= 1)])
    resolution_rate = len(grievances[grievances['Status'] == 'Resolved']) / total_grievances
    
    zone_stress = {}
    for zone in traffic['Zone_Name'].unique():
        traffic_stress = traffic[traffic['Zone_Name'] == zone]['Congestion_Index'].mean()
        energy_stress = energy[energy['Zone_Name'] == zone]['Power_Cut_Flag'].sum() * 20
        waste_stress = waste[waste['Zone_Name'] == zone]['Missed_Pickups'].sum() * 10
        grievance_stress = len(grievances[(grievances['Zone_Name'] == zone) & (grievances['Status'] == 'Open')]) * 5
        zone_stress[zone] = traffic_stress + energy_stress + waste_stress + grievance_stress
    
    return {
        'avg_energy': avg_energy,
        'power_cuts': power_cuts,
        'voltage_issues': voltage_issues,
        'avg_congestion': avg_congestion,
        'peak_congestion': peak_congestion,
        'flow_efficiency': flow_efficiency,
        'avg_bin_fill': avg_bin_fill,
        'missed_pickups': missed_pickups,
        'avg_segregation': avg_segregation,
        'total_grievances': total_grievances,
        'open_grievances': open_grievances,
        'critical_issues': critical_issues,
        'resolution_rate': resolution_rate,
        'zone_stress': zone_stress
    }

# Event processing simulation
def detect_events(grievances, energy, traffic, waste):
    events = []
    
    # Critical traffic events
    critical_traffic = traffic[traffic['Congestion_Index'] > 85]
    for _, row in critical_traffic.head(5).iterrows():
        events.append({
            'type': 'CRITICAL',
            'domain': 'Traffic',
            'message': f"Severe congestion at {row['Zone_Name']} - Index: {row['Congestion_Index']}",
            'action': 'Deploy traffic management team',
            'timestamp': datetime.now() - timedelta(minutes=np.random.randint(1, 60))
        })
    
    # Power cut events
    power_cuts = energy[energy['Power_Cut_Flag'] == 1]
    for _, row in power_cuts.head(3).iterrows():
        events.append({
            'type': 'CRITICAL',
            'domain': 'Energy',
            'message': f"Power outage in {row['Zone_Name']} at {row['Hour']}:00",
            'action': 'Emergency restoration initiated',
            'timestamp': datetime.now() - timedelta(minutes=np.random.randint(1, 90))
        })
    
    # Bin overflow warnings
    overflow_bins = waste[waste['Avg_Bin_Fill_Level_Percent'] > 85]
    for _, row in overflow_bins.head(3).iterrows():
        events.append({
            'type': 'WARNING',
            'domain': 'Waste',
            'message': f"Bins {row['Avg_Bin_Fill_Level_Percent']:.0f}% full in {row['Zone_Name']}",
            'action': 'Scheduled priority pickup',
            'timestamp': datetime.now() - timedelta(minutes=np.random.randint(1, 120))
        })
    
    # SLA breach events
    sla_breach = grievances[(grievances['Status'] == 'Open') & (grievances['SLA_Days'] <= 1)]
    for _, row in sla_breach.head(5).iterrows():
        events.append({
            'type': 'CRITICAL',
            'domain': 'Citizen Services',
            'message': f"SLA breach: {row['Ticket_ID']} - {row['Issue_Type']}",
            'action': 'Escalated to supervisor',
            'timestamp': datetime.now() - timedelta(minutes=np.random.randint(1, 45))
        })
    
    return sorted(events, key=lambda x: x['timestamp'], reverse=True)

# Main app
def main():
    # Sidebar
    st.sidebar.image("https://via.placeholder.com/200x80?text=LMN+Smart+Cities", use_container_width=True)
    st.sidebar.title("🏙️ Navigation")
    
    page = st.sidebar.selectbox(
        "Select Module",
        ["🏗️ System Architecture", "📊 Executive Dashboard", "⚡ Real-Time Pipeline", 
         "🤖 ML Analytics & Predictions", "🎯 Event Processing & Rules", 
         "🚨 Automated Actions", "📈 Advanced Insights", "💡 Recommendations"]
    )
    
    # Load data
    grievances, energy, traffic, waste = load_data()
    
    if grievances is None:
        st.error("Failed to load data. Please ensure CSV files are in the correct location.")
        return
    
    # Date filter
    st.sidebar.markdown("### 🔧 Filters")
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(grievances['Date'].min(), grievances['Date'].max()),
        min_value=grievances['Date'].min(),
        max_value=grievances['Date'].max()
    )
    
    zone_filter = st.sidebar.multiselect(
        "Select Zones",
        options=grievances['Zone_Name'].unique(),
        default=grievances['Zone_Name'].unique()
    )
    
    # Filter data
    mask_g = (grievances['Date'] >= pd.to_datetime(date_range[0])) & (grievances['Date'] <= pd.to_datetime(date_range[1])) & (grievances['Zone_Name'].isin(zone_filter))
    mask_e = (energy['Date'] >= pd.to_datetime(date_range[0])) & (energy['Date'] <= pd.to_datetime(date_range[1])) & (energy['Zone_Name'].isin(zone_filter))
    mask_t = (traffic['Date'] >= pd.to_datetime(date_range[0])) & (traffic['Date'] <= pd.to_datetime(date_range[1])) & (traffic['Zone_Name'].isin(zone_filter))
    mask_w = (waste['Date'] >= pd.to_datetime(date_range[0])) & (waste['Date'] <= pd.to_datetime(date_range[1])) & (waste['Zone_Name'].isin(zone_filter))
    
    grievances_filtered = grievances[mask_g]
    energy_filtered = energy[mask_e]
    traffic_filtered = traffic[mask_t]
    waste_filtered = waste[mask_w]
    
    kpis = calculate_kpis(grievances_filtered, energy_filtered, traffic_filtered, waste_filtered)
    
    # Route to selected page
    if page == "🏗️ System Architecture":
        show_architecture()
    elif page == "📊 Executive Dashboard":
        show_executive_dashboard(kpis, grievances_filtered, energy_filtered, traffic_filtered, waste_filtered)
    elif page == "⚡ Real-Time Pipeline":
        show_realtime_pipeline(grievances_filtered, energy_filtered, traffic_filtered, waste_filtered)
    elif page == "🤖 ML Analytics & Predictions":
        show_ml_analytics(grievances_filtered, energy_filtered, traffic_filtered, waste_filtered)
    elif page == "🎯 Event Processing & Rules":
        show_event_processing(grievances_filtered, energy_filtered, traffic_filtered, waste_filtered)
    elif page == "🚨 Automated Actions":
        show_automated_actions(kpis, grievances_filtered, energy_filtered, traffic_filtered, waste_filtered)
    elif page == "📈 Advanced Insights":
        show_advanced_insights(grievances_filtered, energy_filtered, traffic_filtered, waste_filtered)
    elif page == "💡 Recommendations":
        show_recommendations(kpis, grievances_filtered, energy_filtered, traffic_filtered, waste_filtered)

def show_architecture():
    st.title("🏗️ System Architecture Overview")
    st.markdown("### Integrated Smart City Data Pipeline")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📥 DATA INPUT SOURCES")
        sources = [
            ("🚦 Traffic Sensors", "Active", 156),
            ("💧 Water Meters", "Active", 234),
            ("🚛 Garbage Truck GPS", "Active", 45),
            ("🌡️ Pollution Sensors", "Active", 89),
            ("📱 Citizen Apps", "Active", 1247),
            ("📹 CCTV Feeds", "Active", 312),
            ("🏛️ Govt MIS Database", "Active", 12)
        ]
        
        for name, status, count in sources:
            if status == "Active":
                st.markdown(f'<div class="source-active">{name}<br/><small>{count} units</small></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="source-inactive">{name}<br/><small>{count} units</small></div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### ⚙️ PROCESSING PIPELINE")
        
        st.markdown('<div class="pipeline-box">', unsafe_allow_html=True)
        st.markdown("**🔄 Ingestion Layer**")
        st.markdown("- Real-time data collection")
        st.markdown("- Protocol normalization")
        st.markdown("- Initial validation")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="processing-box">', unsafe_allow_html=True)
        st.markdown("**🎯 Event Processing Engine**")
        st.markdown("- Rule-based filtering")
        st.markdown("- Anomaly detection")
        st.markdown("- Priority classification")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="pipeline-box">', unsafe_allow_html=True)
        st.markdown("**🧹 Clean & Validate**")
        st.markdown("- Data quality checks")
        st.markdown("- Duplicate removal")
        st.markdown("- Schema enforcement")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="processing-box">', unsafe_allow_html=True)
        st.markdown("**💾 Structured Storage**")
        st.markdown("- Time-series DB")
        st.markdown("- Multi-domain tables")
        st.markdown("- Query optimization")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown("#### 📊 ANALYTICS & OUTPUT")
        
        st.markdown('<div class="recommendation">', unsafe_allow_html=True)
        st.markdown("**🤖 ML & Analytics**")
        st.markdown("- Predictive models")
        st.markdown("- Pattern recognition")
        st.markdown("- Trend analysis")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown("**📈 Dashboards & Alerts**")
        st.markdown("- Real-time KPIs")
        st.markdown("- Heatmaps")
        st.markdown("- Automated notifications")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="alert-success">', unsafe_allow_html=True)
        st.markdown("**⚡ Automated Actions**")
        st.markdown("- Traffic signal control")
        st.markdown("- Resource dispatch")
        st.markdown("- Policy updates")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Architecture metrics
    st.markdown("### 📊 System Performance Metrics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Data Sources", "2,095", delta="7 active")
    with col2:
        st.metric("Records/Hour", "1.2M", delta="+12%")
    with col3:
        st.metric("Processing Time", "1.3s", delta="-0.4s")
    with col4:
        st.metric("Data Quality", "98.7%", delta="+1.2%")
    with col5:
        st.metric("System Uptime", "99.94%", delta="+0.02%")
    
    # Data flow visualization
    st.markdown("### 🌊 Real-Time Data Flow")
    
    # Create flow chart data
    flow_data = pd.DataFrame({
        'Time': pd.date_range(start=datetime.now() - timedelta(hours=1), periods=60, freq='1min'),
        'Ingestion': np.random.randint(800, 1200, 60),
        'Processing': np.random.randint(750, 1150, 60),
        'Storage': np.random.randint(700, 1100, 60)
    })
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=flow_data['Time'], y=flow_data['Ingestion'], name='Ingestion', fill='tonexty', line=dict(color='#4ecdc4')))
    fig.add_trace(go.Scatter(x=flow_data['Time'], y=flow_data['Processing'], name='Processing', fill='tonexty', line=dict(color='#667eea')))
    fig.add_trace(go.Scatter(x=flow_data['Time'], y=flow_data['Storage'], name='Storage', fill='tonexty', line=dict(color='#95e1d3')))
    
    fig.update_layout(
        title="Data Processing Pipeline - Last Hour",
        xaxis_title="Time",
        yaxis_title="Records/min",
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_realtime_pipeline(grievances, energy, traffic, waste):
    st.title("⚡ Real-Time Data Pipeline Monitor")
    st.markdown("### Live System Status Dashboard")
    
    # Pipeline health
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Pipeline Status", "🟢 HEALTHY", delta="All systems operational")
    with col2:
        st.metric("Active Streams", "7/7", delta="100%")
    with col3:
        st.metric("Latency", "342ms", delta="-28ms")
    with col4:
        st.metric("Errors (24h)", "3", delta="-12")
    
    st.markdown("---")
    
    # Real-time data streams
    st.markdown("### 📡 Active Data Streams")
    
    streams = [
        {"name": "Traffic Sensors", "status": "Active", "rate": "156 msg/s", "last": "2s ago", "quality": 99.2},
        {"name": "Water Meters", "status": "Active", "rate": "234 msg/s", "last": "1s ago", "quality": 98.7},
        {"name": "GPS Trackers", "status": "Active", "rate": "45 msg/s", "last": "3s ago", "quality": 99.8},
        {"name": "Pollution Sensors", "status": "Active", "rate": "89 msg/s", "last": "1s ago", "quality": 97.5},
        {"name": "Citizen Apps", "status": "Active", "rate": "67 msg/s", "last": "0s ago", "quality": 100.0},
        {"name": "CCTV Feeds", "status": "Active", "rate": "312 msg/s", "last": "1s ago", "quality": 96.8},
        {"name": "MIS Database", "status": "Active", "rate": "12 msg/s", "last": "5s ago", "quality": 99.9}
    ]
    
    stream_df = pd.DataFrame(streams)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Stream table
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=['Stream', 'Status', 'Message Rate', 'Last Update', 'Quality %'],
                fill_color='#667eea',
                font=dict(color='white', size=13),
                align='left'
            ),
            cells=dict(
                values=[stream_df[col] for col in stream_df.columns],
                fill_color=[['#e8f5e9' if status == 'Active' else '#ffebee' for status in stream_df['status']]],
                align='left',
                font_size=12,
                height=30
            )
        )])
        fig.update_layout(height=350, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Quality gauge
        avg_quality = stream_df['quality'].mean()
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=avg_quality,
            domain={'x': [0, 1], 'y': [0, 1]},
            delta={'reference': 95},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#667eea"},
                'steps': [
                    {'range': [0, 70], 'color': "#ffcdd2"},
                    {'range': [70, 90], 'color': "#fff9c4"},
                    {'range': [90, 100], 'color': "#c8e6c9"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 95
                }
            }
        ))
        fig.update_layout(title="Avg Data Quality", height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Processing stages
    st.markdown("### 🔄 Processing Pipeline Stages")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="pipeline-box">', unsafe_allow_html=True)
        st.markdown("**STAGE 1: Ingestion**")
        st.metric("Records Received", f"{len(traffic) + len(energy) + len(waste) + len(grievances):,}")
        st.metric("Validation Rate", "99.1%")
        st.progress(0.99)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="processing-box">', unsafe_allow_html=True)
        st.markdown("**STAGE 2: Processing**")
        st.metric("Records Processed", f"{int((len(traffic) + len(energy) + len(waste) + len(grievances)) * 0.98):,}")
        st.metric("Transform Rate", "98.5%")
        st.progress(0.985)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="pipeline-box">', unsafe_allow_html=True)
        st.markdown("**STAGE 3: Storage**")
        st.metric("Records Stored", f"{int((len(traffic) + len(energy) + len(waste) + len(grievances)) * 0.97):,}")
        st.metric("Storage Rate", "97.8%")
        st.progress(0.978)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Recent pipeline events
    st.markdown("### 📋 Recent Pipeline Events")
    
    pipeline_events = [
        {"time": "2s ago", "stage": "Ingestion", "event": "Batch processed: 1,247 records from Citizen Apps", "status": "✅"},
        {"time": "5s ago", "stage": "Processing", "event": "Data quality check passed for Traffic Sensors", "status": "✅"},
        {"time": "8s ago", "stage": "Storage", "event": "Successfully stored 2,156 records to Structured Storage", "status": "✅"},
        {"time": "15s ago", "stage": "Processing", "event": "Anomaly detected in Pollution Sensor data - flagged for review", "status": "⚠️"},
        {"time": "22s ago", "stage": "Ingestion", "event": "High throughput: 3,421 records/sec from CCTV Feeds", "status": "ℹ️"},
        {"time": "35s ago", "stage": "Storage", "event": "Database optimization completed - query time improved by 23%", "status": "✅"}
    ]
    
    for event in pipeline_events:
        col1, col2, col3, col4 = st.columns([1, 2, 6, 1])
        with col1:
            st.text(event['time'])
        with col2:
            st.text(event['stage'])
        with col3:
            st.text(event['event'])
        with col4:
            st.text(event['status'])

def show_event_processing(grievances, energy, traffic, waste):
    st.title("🎯 Event Processing & Rule Engine")
    st.markdown("### Intelligent Event Detection & Automated Response")
    
    # Detect events
    events = detect_events(grievances, energy, traffic, waste)
    
    # Event summary
    col1, col2, col3, col4 = st.columns(4)
    
    critical_count = len([e for e in events if e['type'] == 'CRITICAL'])
    warning_count = len([e for e in events if e['type'] == 'WARNING'])
    
    with col1:
        st.metric("Total Events", len(events), delta=f"+{len(events)}")
    with col2:
        st.metric("Critical Events", critical_count, delta=f"+{critical_count}", delta_color="inverse")
    with col3:
        st.metric("Warnings", warning_count, delta=f"+{warning_count}", delta_color="inverse")
    with col4:
        st.metric("Actions Triggered", len(events), delta="Auto")
    
    st.markdown("---")
    
    # Event distribution
    col1, col2 = st.columns(2)
    
    with col1:
        event_by_domain = pd.DataFrame(events).groupby('domain').size().reset_index(name='count')
        fig = px.pie(event_by_domain, values='count', names='domain',
                    title='Events by Domain',
                    color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        event_by_type = pd.DataFrame(events).groupby('type').size().reset_index(name='count')
        fig = px.bar(event_by_type, x='type', y='count',
                    title='Events by Severity',
                    color='type',
                    color_discrete_map={'CRITICAL': '#ff4444', 'WARNING': '#ffbb33'})
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Live event feed
    st.markdown("### 🔴 Live Event Feed")
    
    for event in events[:15]:
        col1, col2, col3 = st.columns([1, 3, 2])
        
        with col1:
            if event['type'] == 'CRITICAL':
                st.markdown('<div class="alert-critical">🔴 CRITICAL</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-warning">⚠️ WARNING</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"**{event['domain']}**: {event['message']}")
            st.caption(f"⏰ {event['timestamp'].strftime('%H:%M:%S')}")
        
        with col3:
            st.markdown(f"✅ **Action**: {event['action']}")
        
        st.markdown("---")
    
    # Rule configuration
    st.markdown("### ⚙️ Active Processing Rules")
    
    rules = [
        {
            "id": "R001",
            "name": "Critical Traffic Congestion",
            "condition": "Congestion Index > 85",
            "action": "Deploy traffic management + Notify authorities",
            "priority": "High",
            "triggers": 12
        },
        {
            "id": "R002",
            "name": "Power Outage Detection",
            "condition": "Power_Cut_Flag = 1",
            "action": "Emergency restoration + Citizen notification",
            "priority": "Critical",
            "triggers": 3
        },
        {
            "id": "R003",
            "name": "Waste Overflow Warning",
            "condition": "Bin Fill Level > 85%",
            "action": "Schedule priority pickup",
            "priority": "Medium",
            "triggers": 8
        },
        {
            "id": "R004",
            "name": "SLA Breach Alert",
            "condition": "SLA Days <= 1 AND Status = Open",
            "action": "Escalate to supervisor",
            "priority": "High",
            "triggers": 15
        },
        {
            "id": "R005",
            "name": "Voltage Fluctuation",
            "condition": "Grid Voltage < 220V",
            "action": "Log incident + Maintenance alert",
            "priority": "Medium",
            "triggers": 6
        }
    ]
    
    rules_df = pd.DataFrame(rules)
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['Rule ID', 'Rule Name', 'Condition', 'Action', 'Priority', 'Triggers (24h)'],
            fill_color='#667eea',
            font=dict(color='white', size=12),
            align='left'
        ),
        cells=dict(
            values=[rules_df[col] for col in rules_df.columns],
            fill_color='lavender',
            align='left',
            font_size=11,
            height=35
        )
    )])
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

def show_ml_analytics(grievances, energy, traffic, waste):
    st.title("🤖 ML Analytics & Predictive Models")
    st.markdown("### AI-Powered Insights and Forecasting")
    
    # ML Model Status
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Models", "12", delta="+2 new")
    with col2:
        st.metric("Avg Accuracy", "94.3%", delta="+2.1%")
    with col3:
        st.metric("Predictions/Day", "1.2M", delta="+15%")
    with col4:
        st.metric("Model Training", "✅ Up-to-date", delta="2h ago")
    
    st.markdown("---")
    
    # Predictive models
    st.markdown("### 🎯 Deployed Prediction Models")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="recommendation">', unsafe_allow_html=True)
        st.markdown("**Traffic Congestion Predictor**")
        st.markdown("- **Model**: Gradient Boosting")
        st.markdown("- **Accuracy**: 92.7%")
        st.markdown("- **Features**: Time, Zone, Weather, Events")
        st.markdown("- **Prediction Horizon**: 2 hours")
        
        # Simulated prediction
        future_hours = list(range(24))
        predicted_congestion = [30 + 40*np.sin((h-9)*np.pi/12) + np.random.randint(-5, 5) for h in future_hours]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=future_hours,
            y=predicted_congestion,
            mode='lines+markers',
            name='Predicted Congestion',
            line=dict(color='#ff6b6b', width=3)
        ))
        fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Critical Threshold")
        fig.update_layout(title="24-Hour Traffic Forecast", xaxis_title="Hour", yaxis_title="Congestion Index", height=300)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="recommendation">', unsafe_allow_html=True)
        st.markdown("**Energy Demand Forecaster**")
        st.markdown("- **Model**: LSTM Neural Network")
        st.markdown("- **Accuracy**: 95.2%")
        st.markdown("- **Features**: Historical usage, Temperature, Day type")
        st.markdown("- **Prediction Horizon**: 24 hours")
        
        # Simulated prediction
        daily_energy = energy.groupby('Hour')['Energy_Consumption_kWh'].mean()
        future_energy = [daily_energy.mean() + 500*np.sin((h-6)*np.pi/12) + np.random.randint(-100, 100) for h in future_hours]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=future_hours,
            y=future_energy,
            mode='lines+markers',
            name='Predicted Demand',
            line=dict(color='#4ecdc4', width=3),
            fill='tonexty'
        ))
        fig.update_layout(title="24-Hour Energy Demand Forecast", xaxis_title="Hour", yaxis_title="Energy (kWh)", height=300)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Anomaly detection
    st.markdown("### 🔍 Anomaly Detection Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Traffic anomalies
        st.markdown("**Traffic Pattern Anomalies**")
        anomaly_data = traffic.groupby('Hour')['Congestion_Index'].agg(['mean', 'std']).reset_index()
        anomaly_data['upper'] = anomaly_data['mean'] + 2*anomaly_data['std']
        anomaly_data['lower'] = anomaly_data['mean'] - 2*anomaly_data['std']
        
        actual_traffic = traffic.groupby('Hour')['Congestion_Index'].mean().reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=anomaly_data['Hour'], y=anomaly_data['upper'], 
                                fill=None, mode='lines', line_color='lightgray', name='Normal Range'))
        fig.add_trace(go.Scatter(x=anomaly_data['Hour'], y=anomaly_data['lower'],
                                fill='tonexty', mode='lines', line_color='lightgray', showlegend=False))
        fig.add_trace(go.Scatter(x=actual_traffic['Hour'], y=actual_traffic['Congestion_Index'],
                                mode='markers', name='Actual', marker=dict(size=10, color='#667eea')))
        
        # Highlight anomalies
        anomalies = actual_traffic[(actual_traffic['Congestion_Index'] > anomaly_data['upper'].values) | 
                                  (actual_traffic['Congestion_Index'] < anomaly_data['lower'].values)]
        if len(anomalies) > 0:
            fig.add_trace(go.Scatter(x=anomalies['Hour'], y=anomalies['Congestion_Index'],
                                    mode='markers', name='Anomalies', 
                                    marker=dict(size=15, color='red', symbol='x')))
        
        fig.update_layout(title="Traffic Anomaly Detection", height=350)
        st.plotly_chart(fig, use_container_width=True)
        
        if len(anomalies) > 0:
            st.warning(f"⚠️ {len(anomalies)} anomalies detected requiring investigation")
    
    with col2:
        # Waste collection optimization
        st.markdown("**Waste Collection Route Optimization**")
        
        zone_waste = waste.groupby('Zone_Name')['Total_Waste_Collected_Kg'].mean().reset_index()
        zone_waste['Optimized_Routes'] = [2, 3, 2, 3, 2, 3]
        zone_waste['Current_Routes'] = [3, 4, 3, 4, 3, 4]
        zone_waste['Savings_%'] = ((zone_waste['Current_Routes'] - zone_waste['Optimized_Routes']) / zone_waste['Current_Routes'] * 100).round(1)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=zone_waste['Zone_Name'], y=zone_waste['Current_Routes'],
                            name='Current Routes', marker_color='#ff6b6b'))
        fig.add_trace(go.Bar(x=zone_waste['Zone_Name'], y=zone_waste['Optimized_Routes'],
                            name='ML-Optimized Routes', marker_color='#51cf66'))
        
        fig.update_layout(title="Route Optimization by ML", barmode='group', height=350)
        st.plotly_chart(fig, use_container_width=True)
        
        total_savings = zone_waste['Savings_%'].mean()
        st.success(f"✅ Average route savings: {total_savings:.1f}% - Estimated cost reduction: ₹2.3L/month")
    
    # Feature importance
    st.markdown("### 📊 Model Feature Importance")
    
    features = pd.DataFrame({
        'Feature': ['Hour of Day', 'Zone', 'Day of Week', 'Historical Average', 'Weather', 'Events', 'Season', 'Holiday'],
        'Importance': [0.28, 0.22, 0.18, 0.15, 0.08, 0.05, 0.03, 0.01]
    })
    
    fig = px.bar(features, x='Importance', y='Feature', orientation='h',
                title='Traffic Prediction Model - Feature Importance',
                color='Importance', color_continuous_scale='Blues')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def show_automated_actions(kpis, grievances, energy, traffic, waste):
    st.title("🚨 Automated Decision Engine")
    st.markdown("### Real-Time Automated Actions & Responses")
    
    # Action summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Actions Today", "247", delta="+32")
    with col2:
        st.metric("Success Rate", "96.4%", delta="+1.2%")
    with col3:
        st.metric("Avg Response Time", "18s", delta="-5s")
    with col4:
        st.metric("Manual Override", "3", delta="-2")
    
    st.markdown("---")
    
    # Recent automated actions
    st.markdown("### ⚡ Recent Automated Actions")
    
    actions = [
        {
            "time": "32s ago",
            "trigger": "Critical congestion at Hinjewadi",
            "decision": "Optimize traffic signals",
            "action": "Signal timing adjusted: +30s green on main route",
            "status": "✅ Executed",
            "impact": "Congestion reduced by 12%"
        },
        {
            "time": "2m ago",
            "trigger": "Power outage in Hadapsar",
            "decision": "Emergency restoration protocol",
            "action": "Backup grid activated + Technician dispatched",
            "status": "✅ Executed",
            "impact": "Power restored in 8 minutes"
        },
        {
            "time": "5m ago",
            "trigger": "Bin overflow alert - Kothrud",
            "decision": "Priority waste collection",
            "action": "Nearest truck diverted to location",
            "status": "🚛 In Progress",
            "impact": "ETA: 12 minutes"
        },
        {
            "time": "8m ago",
            "trigger": "SLA breach imminent - Ticket PMC46535",
            "decision": "Escalate to supervisor",
            "action": "Case assigned to senior officer + Citizen notified",
            "status": "✅ Executed",
            "impact": "Issue resolved before SLA breach"
        },
        {
            "time": "15m ago",
            "trigger": "Unusual traffic pattern detected",
            "decision": "Event verification",
            "action": "CCTV feed analyzed + No accident found",
            "status": "✅ Completed",
            "impact": "False alarm - System learning updated"
        }
    ]
    
    for action in actions:
        with st.expander(f"**{action['time']}** - {action['trigger']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**🎯 Decision Made:** {action['decision']}")
                st.markdown(f"**⚙️ Action Taken:** {action['action']}")
            
            with col2:
                st.markdown(f"**Status:** {action['status']}")
                st.markdown(f"**📊 Impact:** {action['impact']}")
    
    st.markdown("---")
    
    # Action categories
    st.markdown("### 📊 Actions by Category")
    
    col1, col2 = st.columns(2)
    
    with col1:
        action_categories = pd.DataFrame({
            'Category': ['Traffic Management', 'Power Grid', 'Waste Collection', 'Citizen Services', 'Emergency Response'],
            'Count': [89, 45, 67, 38, 8]
        })
        
        fig = px.pie(action_categories, values='Count', names='Category',
                    title='Actions Distribution (Last 24h)',
                    color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        success_data = pd.DataFrame({
            'Outcome': ['Successful', 'In Progress', 'Failed', 'Manual Override'],
            'Count': [238, 5, 1, 3]
        })
        
        fig = px.bar(success_data, x='Outcome', y='Count',
                    title='Action Outcomes (Last 24h)',
                    color='Outcome',
                    color_discrete_map={
                        'Successful': '#51cf66',
                        'In Progress': '#ffd43b',
                        'Failed': '#ff6b6b',
                        'Manual Override': '#667eea'
                    })
        st.plotly_chart(fig, use_container_width=True)
    
    # Decision rules
    st.markdown("### 🎯 Active Decision Rules")
    
    decision_rules = [
        {
            "rule": "DR001",
            "condition": "IF Congestion > 85 THEN",
            "action": "Adjust traffic signals + Alert traffic police",
            "confidence": "95%",
            "executions": 89
        },
        {
            "rule": "DR002",
            "condition": "IF Power_Cut = True THEN",
            "action": "Activate backup + Dispatch technician + Notify citizens",
            "confidence": "98%",
            "executions": 45
        },
        {
            "rule": "DR003",
            "condition": "IF Bin_Fill > 85% THEN",
            "action": "Schedule priority pickup within 2 hours",
            "confidence": "92%",
            "executions": 67
        },
        {
            "rule": "DR004",
            "condition": "IF SLA_Days <= 1 AND Status = Open THEN",
            "action": "Escalate + Assign senior officer + Notify citizen",
            "confidence": "97%",
            "executions": 38
        }
    ]
    
    rules_df = pd.DataFrame(decision_rules)
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['Rule ID', 'Condition', 'Automated Action', 'Confidence', 'Executions (24h)'],
            fill_color='#667eea',
            font=dict(color='white', size=12),
            align='left'
        ),
        cells=dict(
            values=[rules_df[col] for col in rules_df.columns],
            fill_color='lavender',
            align='left',
            font_size=11,
            height=40
        )
    )])
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    # External integrations
    st.markdown("### 🔗 External System Notifications")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="alert-success">', unsafe_allow_html=True)
        st.markdown("**🚓 Traffic Police**")
        st.markdown("- 12 congestion alerts sent")
        st.markdown("- 8 responses received")
        st.markdown("- Avg response: 4.2 min")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="alert-success">', unsafe_allow_html=True)
        st.markdown("**⚡ Power Department**")
        st.markdown("- 3 outage notifications")
        st.markdown("- 3 restorations completed")
        st.markdown("- Avg downtime: 11 min")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="alert-success">', unsafe_allow_html=True)
        st.markdown("**📱 Citizen App**")
        st.markdown("- 156 status updates sent")
        st.markdown("- 89% read rate")
        st.markdown("- Satisfaction: 4.3/5")
        st.markdown('</div>', unsafe_allow_html=True)

def show_executive_dashboard(kpis, grievances, energy, traffic, waste):
    st.title("📊 Executive Dashboard")
    st.markdown("### City Operations Command Center")
    
    # Top KPIs
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Avg Energy Load",
            f"{kpis['avg_energy']/1000:.2f}K kWh",
            delta=f"{-5.2}%" if kpis['power_cuts'] > 10 else f"+2.1%"
        )
    
    with col2:
        st.metric(
            "Traffic Flow Efficiency",
            f"{kpis['flow_efficiency']:.2%}",
            delta=f"{-8}%" if kpis['avg_congestion'] > 50 else f"+3%"
        )
    
    with col3:
        st.metric(
            "Critical Issues",
            f"{kpis['critical_issues']}",
            delta=f"+{kpis['critical_issues']}" if kpis['critical_issues'] > 0 else "0",
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            "Grievance Resolution",
            f"{kpis['resolution_rate']:.1%}",
            delta=f"+{5}%" if kpis['resolution_rate'] > 0.6 else f"-{3}%"
        )
    
    with col5:
        st.metric(
            "Avg Bin Fill Level",
            f"{kpis['avg_bin_fill']:.1f}%",
            delta=f"-{2}%" if kpis['avg_bin_fill'] < 70 else f"+{4}%",
            delta_color="inverse"
        )
    
    st.markdown("---")
    
    # Main visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Zone Stress Factor
        st.markdown("### 🗺️ Zone Stress Factor")
        zone_stress_df = pd.DataFrame(list(kpis['zone_stress'].items()), columns=['Zone', 'Stress'])
        zone_stress_df = zone_stress_df.sort_values('Stress', ascending=False)
        
        fig = go.Figure(data=[
            go.Bar(
                x=zone_stress_df['Stress'],
                y=zone_stress_df['Zone'],
                orientation='h',
                marker=dict(
                    color=zone_stress_df['Stress'],
                    colorscale='RdYlGn_r',
                    showscale=True,
                    colorbar=dict(title="Stress Level")
                ),
                text=zone_stress_df['Stress'].round(0),
                textposition='auto'
            )
        ])
        fig.update_layout(
            title="Composite Zone Stress Index",
            xaxis_title="Stress Score",
            yaxis_title="Zone",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Traffic Peak Hours
        st.markdown("### 🚦 Traffic Congestion by Hour")
        hourly_traffic = traffic.groupby('Hour')['Congestion_Index'].mean().reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hourly_traffic['Hour'],
            y=hourly_traffic['Congestion_Index'],
            mode='lines+markers',
            fill='tozeroy',
            line=dict(color='#ff6b6b', width=3),
            marker=dict(size=8)
        ))
        fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Critical Threshold")
        fig.update_layout(
            title="Average Congestion Throughout the Day",
            xaxis_title="Hour of Day",
            yaxis_title="Congestion Index",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Bottom row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Energy consumption trend
        st.markdown("### ⚡ Energy Consumption Trend")
        daily_energy = energy.groupby('Date')['Energy_Consumption_kWh'].mean().reset_index()
        
        fig = px.line(daily_energy, x='Date', y='Energy_Consumption_kWh',
                     title="Daily Average Energy Consumption")
        fig.update_traces(line_color='#4ecdc4', line_width=3)
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Grievance status
        st.markdown("### 🎫 Grievance Status Distribution")
        status_counts = grievances['Status'].value_counts()
        
        fig = go.Figure(data=[go.Pie(
            labels=status_counts.index,
            values=status_counts.values,
            hole=0.4,
            marker=dict(colors=['#51cf66', '#ffd43b', '#ff6b6b'])
        )])
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        # Waste segregation efficiency
        st.markdown("### ♻️ Waste Segregation by Zone")
        zone_segregation = waste.groupby('Zone_Name')['Segregation_Efficiency_Percent'].mean().reset_index()
        
        fig = px.bar(zone_segregation, x='Zone_Name', y='Segregation_Efficiency_Percent',
                    title="Average Segregation Efficiency")
        fig.add_hline(y=80, line_dash="dash", line_color="green", annotation_text="Target: 80%")
        fig.update_layout(height=300, showlegend=False)
        fig.update_traces(marker_color='#95e1d3')
        st.plotly_chart(fig, use_container_width=True)

def show_advanced_insights(grievances, energy, traffic, waste):
    st.title("📈 Advanced Cross-Domain Insights")
    st.markdown("### Deep Dive Analytics & Pattern Discovery")
    
    # Correlation Analysis
    st.markdown("#### 🔗 Inter-Domain Correlation Matrix")
    
    daily_traffic = traffic.groupby(['Date', 'Zone_Name'])['Congestion_Index'].mean().reset_index()
    daily_energy = energy.groupby(['Date', 'Zone_Name'])['Energy_Consumption_kWh'].mean().reset_index()
    daily_waste = waste.groupby(['Date', 'Zone_Name'])['Avg_Bin_Fill_Level_Percent'].mean().reset_index()
    daily_grievances = grievances[grievances['Status'] == 'Open'].groupby(['Date', 'Zone_Name']).size().reset_index(name='Open_Count')
    
    merged = daily_traffic.merge(daily_energy, on=['Date', 'Zone_Name'], how='outer')
    merged = merged.merge(daily_waste, on=['Date', 'Zone_Name'], how='outer')
    merged = merged.merge(daily_grievances, on=['Date', 'Zone_Name'], how='outer')
    merged = merged.fillna(0)
    
    corr_matrix = merged[['Congestion_Index', 'Energy_Consumption_kWh', 'Avg_Bin_Fill_Level_Percent', 'Open_Count']].corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=['Traffic Congestion', 'Energy Consumption', 'Bin Fill Level', 'Open Grievances'],
        y=['Traffic Congestion', 'Energy Consumption', 'Bin Fill Level', 'Open Grievances'],
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values.round(2),
        texttemplate='%{text}',
        textfont={"size": 12},
        colorbar=dict(title="Correlation")
    ))
    fig.update_layout(title="Cross-Domain Correlation Analysis", height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown("**🔍 Key Finding 1:**")
        if corr_matrix.loc['Congestion_Index', 'Energy_Consumption_kWh'] > 0.5:
            st.markdown("Strong positive correlation between traffic congestion and energy consumption suggests that traffic management improvements could lead to energy savings.")
        else:
            st.markdown("Traffic and energy patterns show moderate correlation. Zone-specific analysis recommended.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown("**🔍 Key Finding 2:**")
        if corr_matrix.loc['Open_Count', 'Avg_Bin_Fill_Level_Percent'] > 0.4:
            st.markdown("High bin fill levels correlate with increased grievances. Proactive waste collection scheduling can reduce citizen complaints.")
        else:
            st.markdown("Waste management and grievances show independent patterns. Multi-factor analysis needed.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Department Performance
    st.markdown("### 🏢 Department-wise Performance Metrics")
    
    dept_metrics = grievances.groupby('Department').agg({
        'Ticket_ID': 'count',
        'SLA_Days': 'mean',
        'Status': lambda x: (x == 'Resolved').sum() / len(x)
    }).reset_index()
    dept_metrics.columns = ['Department', 'Total_Tickets', 'Avg_Resolution_Time', 'Resolution_Rate']
    
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=('Total Tickets', 'Avg Resolution Time (days)', 'Resolution Rate'),
        specs=[[{'type': 'bar'}, {'type': 'bar'}, {'type': 'bar'}]]
    )
    
    fig.add_trace(go.Bar(x=dept_metrics['Department'], y=dept_metrics['Total_Tickets'], name='Tickets', marker_color='#667eea'), row=1, col=1)
    fig.add_trace(go.Bar(x=dept_metrics['Department'], y=dept_metrics['Avg_Resolution_Time'], name='Days', marker_color='#f093fb'), row=1, col=2)
    fig.add_trace(go.Bar(x=dept_metrics['Department'], y=dept_metrics['Resolution_Rate'], name='Rate', marker_color='#4facfe'), row=1, col=3)
    
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

def show_recommendations(kpis, grievances, energy, traffic, waste):
    st.title("💡 AI-Powered Recommendations")
    st.markdown("### Actionable Insights for City Administrators")
    
    # Priority recommendations
    st.markdown("### 🎯 Priority Action Items")
    
    recommendations = []
    
    if kpis['avg_congestion'] > 60:
        recommendations.append({
            'priority': 'HIGH',
            'category': 'Traffic',
            'title': 'Implement Dynamic Traffic Signal Management',
            'description': f"Current avg congestion: {kpis['avg_congestion']:.1f}/100. Deploy AI-based adaptive traffic signals in high-congestion zones.",
            'impact': 'Potential 15-20% reduction in congestion',
            'cost': 'Medium',
            'timeline': '3-6 months'
        })
    
    if kpis['power_cuts'] > 10:
        recommendations.append({
            'priority': 'HIGH',
            'category': 'Energy',
            'title': 'Strengthen Grid Infrastructure in Vulnerable Zones',
            'description': f"{kpis['power_cuts']} power cuts detected. Focus on zones with frequent outages.",
            'impact': 'Improve service reliability by 30%',
            'cost': 'High',
            'timeline': '6-12 months'
        })
    
    if kpis['avg_bin_fill'] > 70:
        recommendations.append({
            'priority': 'MEDIUM',
            'category': 'Waste',
            'title': 'Optimize Waste Collection Routes',
            'description': f"Avg bin fill at {kpis['avg_bin_fill']:.1f}%. Implement IoT-based smart bin monitoring for dynamic scheduling.",
            'impact': '25% reduction in operational costs',
            'cost': 'Low',
            'timeline': '1-3 months'
        })
    
    if kpis['resolution_rate'] < 0.7:
        recommendations.append({
            'priority': 'HIGH',
            'category': 'Citizen Services',
            'title': 'Enhance Grievance Resolution Process',
            'description': f"Resolution rate at {kpis['resolution_rate']:.1%}. Deploy dedicated teams for critical departments.",
            'impact': 'Improve citizen satisfaction by 40%',
            'cost': 'Low',
            'timeline': 'Immediate'
        })
    
    if kpis['avg_segregation'] < 75:
        recommendations.append({
            'priority': 'MEDIUM',
            'category': 'Waste',
            'title': 'Launch Waste Segregation Awareness Campaign',
            'description': f"Segregation efficiency at {kpis['avg_segregation']:.1f}%. Conduct citizen education programs.",
            'impact': 'Increase recycling rate by 20%',
            'cost': 'Low',
            'timeline': '1-2 months'
        })
    
    # Display recommendations
    for idx, rec in enumerate(recommendations, 1):
        with st.expander(f"**{idx}. {rec['title']}** - Priority: {rec['priority']}", expanded=(rec['priority']=='HIGH')):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Category:** {rec['category']}")
                st.markdown(f"**Description:** {rec['description']}")
                st.markdown(f"**Expected Impact:** {rec['impact']}")
            
            with col2:
                st.markdown(f"**Cost:** {rec['cost']}")
                st.markdown(f"**Timeline:** {rec['timeline']}")
            
            st.divider()
    
    # ROI analysis
    st.markdown("### 💰 Return on Investment Analysis")
    
    roi_data = pd.DataFrame({
        'Initiative': ['Dynamic Traffic Signals', 'Grid Modernization', 'Smart Bin System', 'Mobile App for Grievances'],
        'Investment (₹ Cr)': [12, 50, 8, 3],
        'Annual Savings (₹ Cr)': [8, 15, 6, 2],
        'Payback Period (Years)': [1.5, 3.3, 1.3, 1.5],
        'Citizen Impact Score': [85, 70, 80, 90]
    })
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(roi_data.columns),
            fill_color='#667eea',
            font=dict(color='white', size=14),
            align='left'
        ),
        cells=dict(
            values=[roi_data[col] for col in roi_data.columns],
            fill_color='lavender',
            align='left',
            font_size=12,
            height=30
        )
    )])
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()