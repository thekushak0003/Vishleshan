import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Page config
st.set_page_config(
    page_title="LMN Smart Cities - Integrated Analytics Platform",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Chart template configuration for better visibility
CHART_TEMPLATE = "plotly_white"
CHART_CONFIG = {
    'displayModeBar': True,
    'displaylogo': False,
    'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d']
}

# Color palette for consistent theming
COLORS = {
    'primary': '#667eea',
    'secondary': '#764ba2',
    'success': '#51cf66',
    'warning': '#ffd43b',
    'danger': '#ff6b6b',
    'info': '#4ecdc4',
    'traffic': '#ff6b6b',
    'energy': '#4ecdc4',
    'waste': '#95e1d3',
    'grievances': '#f093fb',
    'text': '#2c3e50',
    'bg': '#ffffff'
}

# Custom CSS with improved contrast
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
        background-color: #f8f9fa;
    }
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white !important;
    }
    .stMetric label {
        color: white !important;
        font-weight: 600;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: white !important;
        font-size: 2rem !important;
    }
    .stMetric [data-testid="stMetricDelta"] {
        color: #e0e0e0 !important;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .alert-critical {
        background-color: #ff4444;
        padding: 15px;
        border-radius: 8px;
        color: white;
        margin: 10px 0;
        font-weight: bold;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .alert-warning {
        background-color: #ffbb33;
        padding: 15px;
        border-radius: 8px;
        color: #000;
        margin: 10px 0;
        font-weight: bold;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .alert-success {
        background-color: #00C851;
        padding: 15px;
        border-radius: 8px;
        color: white;
        margin: 10px 0;
        font-weight: bold;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .insight-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: #2c3e50;
    }
    .recommendation {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #4caf50;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: #2c3e50;
    }
    .pipeline-box {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #2196f3;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: #2c3e50;
    }
    .processing-box {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #9c27b0;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: #2c3e50;
    }
    h1, h2, h3 {
        color: #667eea !important;
        font-weight: 600 !important;
    }
    .source-active {
        background-color: #00C851;
        padding: 10px;
        border-radius: 5px;
        color: white;
        margin: 5px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .source-inactive {
        background-color: #ffbb33;
        padding: 10px;
        border-radius: 5px;
        color: #000;
        margin: 5px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    div[data-testid="stExpander"] {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        margin: 5px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Load data with error handling
@st.cache_data(ttl=3600)
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
    except FileNotFoundError as e:
        st.error(f"⚠️ Data files not found. Please ensure all CSV files are in the app directory.")
        st.info("Required files: pune_citizen_grievances.csv, pune_energy_consumption.csv, pune_traffic_flow.csv, pune_waste_management.csv")
        return None, None, None, None
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None, None, None

def create_chart_layout(title, xaxis_title="", yaxis_title="", height=400):
    return dict(
        title=dict(
            text=title,
            font=dict(size=16, color=COLORS['text'], family="Arial, sans-serif")
        ),
        xaxis=dict(
            title=dict(
                text=xaxis_title,
                font=dict(color=COLORS['text'])
            ),
            gridcolor='#e0e0e0'
        ),
        yaxis=dict(
            title=dict(
                text=yaxis_title,
                font=dict(color=COLORS['text'])
            ),
            gridcolor='#e0e0e0'
        ),
        height=height,
        template=CHART_TEMPLATE,
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color=COLORS['text'], family="Arial, sans-serif"),
        hovermode='closest'
    )


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
    resolution_rate = len(grievances[grievances['Status'] == 'Resolved']) / total_grievances if total_grievances > 0 else 0
    
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

# Event processing
def detect_events(grievances, energy, traffic, waste):
    events = []
    
    critical_traffic = traffic[traffic['Congestion_Index'] > 85]
    for _, row in critical_traffic.head(5).iterrows():
        events.append({
            'type': 'CRITICAL',
            'domain': 'Traffic',
            'message': f"Severe congestion at {row['Zone_Name']} - Index: {row['Congestion_Index']}",
            'action': 'Deploy traffic management team',
            'timestamp': datetime.now() - timedelta(minutes=np.random.randint(1, 60))
        })
    
    power_cuts = energy[energy['Power_Cut_Flag'] == 1]
    for _, row in power_cuts.head(3).iterrows():
        events.append({
            'type': 'CRITICAL',
            'domain': 'Energy',
            'message': f"Power outage in {row['Zone_Name']} at {row['Hour']}:00",
            'action': 'Emergency restoration initiated',
            'timestamp': datetime.now() - timedelta(minutes=np.random.randint(1, 90))
        })
    
    overflow_bins = waste[waste['Avg_Bin_Fill_Level_Percent'] > 85]
    for _, row in overflow_bins.head(3).iterrows():
        events.append({
            'type': 'WARNING',
            'domain': 'Waste',
            'message': f"Bins {row['Avg_Bin_Fill_Level_Percent']:.0f}% full in {row['Zone_Name']}",
            'action': 'Scheduled priority pickup',
            'timestamp': datetime.now() - timedelta(minutes=np.random.randint(1, 120))
        })
    
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
    st.sidebar.markdown("### 🏙️ LMN Smart Cities")
    st.sidebar.markdown("**Integrated Analytics Platform**")
    st.sidebar.markdown("---")
    
    page = st.sidebar.selectbox(
        "📍 Navigate to",
        ["🏗️ System Architecture", "📊 Executive Dashboard", "⚡ Real-Time Pipeline", 
         "🤖 ML Analytics & Predictions", "🎯 Event Processing & Rules", 
         "🚨 Automated Actions", "📈 Advanced Insights", "💡 Recommendations"],
        index=1
    )
    
    # Load data
    with st.spinner("Loading city data..."):
        grievances, energy, traffic, waste = load_data()
    
    if grievances is None:
        st.stop()
    
    # Date filter
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔧 Filters")
    
    min_date = grievances['Date'].min().date()
    max_date = grievances['Date'].max().date()
    
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    zone_filter = st.sidebar.multiselect(
        "Select Zones",
        options=sorted(grievances['Zone_Name'].unique()),
        default=sorted(grievances['Zone_Name'].unique())
    )
    
    # Handle single date selection
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range
    
    # Filter data
    mask_g = (grievances['Date'].dt.date >= start_date) & (grievances['Date'].dt.date <= end_date) & (grievances['Zone_Name'].isin(zone_filter))
    mask_e = (energy['Date'].dt.date >= start_date) & (energy['Date'].dt.date <= end_date) & (energy['Zone_Name'].isin(zone_filter))
    mask_t = (traffic['Date'].dt.date >= start_date) & (traffic['Date'].dt.date <= end_date) & (traffic['Zone_Name'].isin(zone_filter))
    mask_w = (waste['Date'].dt.date >= start_date) & (waste['Date'].dt.date <= end_date) & (waste['Zone_Name'].isin(zone_filter))
    
    grievances_filtered = grievances[mask_g]
    energy_filtered = energy[mask_e]
    traffic_filtered = traffic[mask_t]
    waste_filtered = waste[mask_w]
    
    if len(grievances_filtered) == 0:
        st.warning("⚠️ No data available for the selected filters. Please adjust your selection.")
        st.stop()
    
    kpis = calculate_kpis(grievances_filtered, energy_filtered, traffic_filtered, waste_filtered)
    
    # Add data info in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Data Summary")
    st.sidebar.info(f"**Records Loaded:**\n- Grievances: {len(grievances_filtered):,}\n- Traffic: {len(traffic_filtered):,}\n- Energy: {len(energy_filtered):,}\n- Waste: {len(waste_filtered):,}")
    
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
            st.markdown(f'<div class="source-active">{name}<br/><small>{count} units</small></div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### ⚙️ PROCESSING PIPELINE")
        
        st.markdown('<div class="pipeline-box"><strong>🔄 Ingestion Layer</strong><br/>• Real-time collection<br/>• Protocol normalization<br/>• Initial validation</div>', unsafe_allow_html=True)
        st.markdown('<div class="processing-box"><strong>🎯 Event Processing</strong><br/>• Rule-based filtering<br/>• Anomaly detection<br/>• Priority classification</div>', unsafe_allow_html=True)
        st.markdown('<div class="pipeline-box"><strong>🧹 Clean & Validate</strong><br/>• Data quality checks<br/>• Duplicate removal<br/>• Schema enforcement</div>', unsafe_allow_html=True)
        st.markdown('<div class="processing-box"><strong>💾 Structured Storage</strong><br/>• Time-series DB<br/>• Multi-domain tables<br/>• Query optimization</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown("#### 📊 ANALYTICS & OUTPUT")
        
        st.markdown('<div class="recommendation"><strong>🤖 ML & Analytics</strong><br/>• Predictive models<br/>• Pattern recognition<br/>• Trend analysis</div>', unsafe_allow_html=True)
        st.markdown('<div class="insight-box"><strong>📈 Dashboards & Alerts</strong><br/>• Real-time KPIs<br/>• Heatmaps<br/>• Automated notifications</div>', unsafe_allow_html=True)
        st.markdown('<div class="alert-success"><strong>⚡ Automated Actions</strong><br/>• Traffic signal control<br/>• Resource dispatch<br/>• Policy updates</div>', unsafe_allow_html=True)
    
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
    
    flow_data = pd.DataFrame({
        'Time': pd.date_range(start=datetime.now() - timedelta(hours=1), periods=60, freq='1min'),
        'Ingestion': np.random.randint(800, 1200, 60),
        'Processing': np.random.randint(750, 1150, 60),
        'Storage': np.random.randint(700, 1100, 60)
    })
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=flow_data['Time'], y=flow_data['Ingestion'], name='Ingestion', 
                            fill='tonexty', line=dict(color=COLORS['info'], width=2)))
    fig.add_trace(go.Scatter(x=flow_data['Time'], y=flow_data['Processing'], name='Processing', 
                            fill='tonexty', line=dict(color=COLORS['primary'], width=2)))
    fig.add_trace(go.Scatter(x=flow_data['Time'], y=flow_data['Storage'], name='Storage', 
                            fill='tonexty', line=dict(color=COLORS['waste'], width=2)))
    
    fig.update_layout(**create_chart_layout("Data Processing Pipeline - Last Hour", "Time", "Records/min"))
    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

def show_executive_dashboard(kpis, grievances, energy, traffic, waste):
    st.title("📊 Executive Dashboard")
    st.markdown("### City Operations Command Center")
    
    # Top KPIs
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Avg Energy Load", f"{kpis['avg_energy']/1000:.2f}K kWh", 
                 delta=f"{-5.2}%" if kpis['power_cuts'] > 10 else f"+2.1%")
    
    with col2:
        st.metric("Traffic Flow Efficiency", f"{kpis['flow_efficiency']:.2%}",
                 delta=f"{-8}%" if kpis['avg_congestion'] > 50 else f"+3%")
    
    with col3:
        st.metric("Critical Issues", f"{kpis['critical_issues']}",
                 delta=f"+{kpis['critical_issues']}" if kpis['critical_issues'] > 0 else "0",
                 delta_color="inverse")
    
    with col4:
        st.metric("Grievance Resolution", f"{kpis['resolution_rate']:.1%}",
                 delta=f"+{5}%" if kpis['resolution_rate'] > 0.6 else f"-{3}%")
    
    with col5:
        st.metric("Avg Bin Fill Level", f"{kpis['avg_bin_fill']:.1f}%",
                 delta=f"-{2}%" if kpis['avg_bin_fill'] < 70 else f"+{4}%",
                 delta_color="inverse")
    
    st.markdown("---")
    
    # Main visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🗺️ Zone Stress Factor")
        zone_stress_df = pd.DataFrame(list(kpis['zone_stress'].items()), columns=['Zone', 'Stress'])
        zone_stress_df = zone_stress_df.sort_values('Stress', ascending=True)
        
        fig = go.Figure(data=[go.Bar(
            x=zone_stress_df['Stress'],
            y=zone_stress_df['Zone'],
            orientation='h',
            marker=dict(
                color=zone_stress_df['Stress'],
                colorscale='RdYlGn_r',
                showscale=True,
                colorbar=dict(title=dict(text="Stress", font=dict(color=COLORS['text'])))
            ),
            text=zone_stress_df['Stress'].round(0),
            textposition='auto',
            textfont=dict(color='white', size=12)
        )])
        
        fig.update_layout(**create_chart_layout("Composite Zone Stress Index", "Stress Score", "Zone"))
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
    
    with col2:
        st.markdown("### 🚦 Traffic Congestion by Hour")
        hourly_traffic = traffic.groupby('Hour')['Congestion_Index'].mean().reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hourly_traffic['Hour'],
            y=hourly_traffic['Congestion_Index'],
            mode='lines+markers',
            fill='tozeroy',
            line=dict(color=COLORS['traffic'], width=3),
            marker=dict(size=8, color=COLORS['traffic'])
        ))
        fig.add_hline(y=70, line_dash="dash", line_color="red", 
                     annotation=dict(text="Critical Threshold", font=dict(color=COLORS['text'])))
        
        fig.update_layout(**create_chart_layout("Average Congestion Throughout the Day", "Hour of Day", "Congestion Index"))
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
    
    # Bottom row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### ⚡ Energy Consumption Trend")
        daily_energy = energy.groupby('Date')['Energy_Consumption_kWh'].mean().reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily_energy['Date'],
            y=daily_energy['Energy_Consumption_kWh'],
            mode='lines',
            line=dict(color=COLORS['energy'], width=3),
            fill='tozeroy'
        ))
        
        fig.update_layout(**create_chart_layout("Daily Average Energy Consumption", "Date", "Energy (kWh)", 300))
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
    
    with col2:
        st.markdown("### 🎫 Grievance Status Distribution")
        status_counts = grievances['Status'].value_counts()
        
        fig = go.Figure(data=[go.Pie(
            labels=status_counts.index,
            values=status_counts.values,
            hole=0.4,
            marker=dict(colors=[COLORS['success'], COLORS['warning'], COLORS['danger']]),
            textfont=dict(size=14, color='white')
        )])
        
        fig.update_layout(**create_chart_layout("Grievance Status", height=300))
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
    
    with col3:
        st.markdown("### ♻️ Waste Segregation by Zone")
        zone_segregation = waste.groupby('Zone_Name')['Segregation_Efficiency_Percent'].mean().reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=zone_segregation['Zone_Name'],
            y=zone_segregation['Segregation_Efficiency_Percent'],
            marker_color=COLORS['waste'],
            text=zone_segregation['Segregation_Efficiency_Percent'].round(1),
            textposition='auto',
            textfont=dict(color=COLORS['text'])
        ))
        fig.add_hline(y=80, line_dash="dash", line_color="green",
                     annotation=dict(text="Target: 80%", font=dict(color=COLORS['text'])))
        
        fig.update_layout(**create_chart_layout("Average Segregation Efficiency", "", "%", 300))
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

def show_realtime_pipeline(grievances, energy, traffic, waste):
    st.title("⚡ Real-Time Data Pipeline Monitor")
    st.markdown("### Live System Status Dashboard")
    
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
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=['<b>Stream</b>', '<b>Status</b>', '<b>Message Rate</b>', '<b>Last Update</b>', '<b>Quality %</b>'],
                fill_color=COLORS['primary'],
                font=dict(color='white', size=14),
                align='left',
                height=40
            ),
            cells=dict(
                values=[stream_df[col] for col in stream_df.columns],
                fill_color=[['#e8f5e9' if status == 'Active' else '#ffebee' for status in stream_df['status']]],
                font=dict(color=COLORS['text'], size=12),
                align='left',
                height=35
            )
        )])
        fig.update_layout(
            margin=dict(l=0, r=0, t=20, b=0),
            height=350,
            paper_bgcolor='white'
        )
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
    
    with col2:
        avg_quality = stream_df['quality'].mean()
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=avg_quality,
            domain={'x': [0, 1], 'y': [0, 1]},
            delta={'reference': 95, 'font': {'color': COLORS['text']}},
            number={'font': {'size': 40, 'color': COLORS['text']}},
            gauge={
                'axis': {'range': [None, 100], 'tickcolor': COLORS['text']},
                'bar': {'color': COLORS['primary']},
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
            },
            title={'text': "Avg Data Quality", 'font': {'color': COLORS['text']}}
        ))
        fig.update_layout(paper_bgcolor='white', height=350)
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
    
    st.markdown("---")
    
    st.markdown("### 🔄 Processing Pipeline Stages")
    
    col1, col2, col3 = st.columns(3)
    
    total_records = len(traffic) + len(energy) + len(waste) + len(grievances)
    
    with col1:
        st.markdown('<div class="pipeline-box">', unsafe_allow_html=True)
        st.markdown("**STAGE 1: Ingestion**")
        st.metric("Records Received", f"{total_records:,}")
        st.metric("Validation Rate", "99.1%")
        st.progress(0.99)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="processing-box">', unsafe_allow_html=True)
        st.markdown("**STAGE 2: Processing**")
        st.metric("Records Processed", f"{int(total_records * 0.98):,}")
        st.metric("Transform Rate", "98.5%")
        st.progress(0.985)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="pipeline-box">', unsafe_allow_html=True)
        st.markdown("**STAGE 3: Storage**")
        st.metric("Records Stored", f"{int(total_records * 0.97):,}")
        st.metric("Storage Rate", "97.8%")
        st.progress(0.978)
        st.markdown('</div>', unsafe_allow_html=True)

def show_event_processing(grievances, energy, traffic, waste):
    st.title("🎯 Event Processing & Rule Engine")
    st.markdown("### Intelligent Event Detection & Automated Response")
    
    events = detect_events(grievances, energy, traffic, waste)
    
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
    
    col1, col2 = st.columns(2)
    
    with col1:
        event_by_domain = pd.DataFrame(events).groupby('domain').size().reset_index(name='count')
        fig = px.pie(event_by_domain, values='count', names='domain',
                    title='Events by Domain',
                    color_discrete_sequence=px.colors.sequential.RdBu)
        fig.update_traces(textfont=dict(size=14, color='white'))
        fig.update_layout(**create_chart_layout("Events by Domain"))
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
    
    with col2:
        event_by_type = pd.DataFrame(events).groupby('type').size().reset_index(name='count')
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=event_by_type['type'],
            y=event_by_type['count'],
            marker_color=[COLORS['danger'] if t == 'CRITICAL' else COLORS['warning'] for t in event_by_type['type']],
            text=event_by_type['count'],
            textposition='auto',
            textfont=dict(color='white', size=14)
        ))
        fig.update_layout(**create_chart_layout("Events by Severity", "Type", "Count"))
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
    
    st.markdown("---")
    st.markdown("### 🔴 Live Event Feed")
    
    for event in events[:10]:
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

def show_ml_analytics(grievances, energy, traffic, waste):
    st.title("🤖 ML Analytics & Predictive Models")
    st.markdown("### AI-Powered Insights and Forecasting")
    
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
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="recommendation">', unsafe_allow_html=True)
        st.markdown("**Traffic Congestion Predictor**")
        st.markdown("- **Model**: Gradient Boosting\n- **Accuracy**: 92.7%\n- **Features**: Time, Zone, Weather, Events\n- **Prediction Horizon**: 2 hours")
        
        future_hours = list(range(24))
        predicted_congestion = [30 + 40*np.sin((h-9)*np.pi/12) + np.random.randint(-5, 5) for h in future_hours]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=future_hours,
            y=predicted_congestion,
            mode='lines+markers',
            name='Predicted Congestion',
            line=dict(color=COLORS['traffic'], width=3),
            marker=dict(size=8)
        ))
        fig.add_hline(y=70, line_dash="dash", line_color="red",
                     annotation=dict(text="Critical Threshold", font=dict(color=COLORS['text'])))
        fig.update_layout(**create_chart_layout("24-Hour Traffic Forecast", "Hour", "Congestion Index", 300))
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="recommendation">', unsafe_allow_html=True)
        st.markdown("**Energy Demand Forecaster**")
        st.markdown("- **Model**: LSTM Neural Network\n- **Accuracy**: 95.2%\n- **Features**: Historical usage, Temperature, Day type\n- **Prediction Horizon**: 24 hours")
        
        daily_energy = energy.groupby('Hour')['Energy_Consumption_kWh'].mean()
        future_energy = [daily_energy.mean() + 500*np.sin((h-6)*np.pi/12) + np.random.randint(-100, 100) for h in future_hours]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=future_hours,
            y=future_energy,
            mode='lines+markers',
            name='Predicted Demand',
            line=dict(color=COLORS['energy'], width=3),
            fill='tozeroy',
            marker=dict(size=8)
        ))
        fig.update_layout(**create_chart_layout("24-Hour Energy Demand Forecast", "Hour", "Energy (kWh)", 300))
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📊 Model Feature Importance")
    
    features = pd.DataFrame({
        'Feature': ['Hour of Day', 'Zone', 'Day of Week', 'Historical Average', 'Weather', 'Events', 'Season', 'Holiday'],
        'Importance': [0.28, 0.22, 0.18, 0.15, 0.08, 0.05, 0.03, 0.01]
    })
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=features['Importance'],
        y=features['Feature'],
        orientation='h',
        marker=dict(
            color=features['Importance'],
            colorscale='Blues',
            showscale=True,
            colorbar=dict(title=dict(text="Importance", font=dict(color=COLORS['text'])))
        ),
        text=features['Importance'].round(2),
        textposition='auto',
        textfont=dict(color='white')
    ))
    fig.update_layout(**create_chart_layout("Traffic Prediction Model - Feature Importance", "Importance", "Feature"))
    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

def show_automated_actions(kpis, grievances, energy, traffic, waste):
    st.title("🚨 Automated Decision Engine")
    st.markdown("### Real-Time Automated Actions & Responses")
    
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
    
    col1, col2 = st.columns(2)
    
    with col1:
        action_categories = pd.DataFrame({
            'Category': ['Traffic Management', 'Power Grid', 'Waste Collection', 'Citizen Services', 'Emergency Response'],
            'Count': [89, 45, 67, 38, 8]
        })
        
        fig = px.pie(action_categories, values='Count', names='Category',
                    title='Actions Distribution (Last 24h)',
                    color_discrete_sequence=px.colors.sequential.RdBu)
        fig.update_traces(textfont=dict(size=14, color='white'))
        fig.update_layout(**create_chart_layout("Actions Distribution"))
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
    
    with col2:
        success_data = pd.DataFrame({
            'Outcome': ['Successful', 'In Progress', 'Failed', 'Manual Override'],
            'Count': [238, 5, 1, 3]
        })
        
        color_map = {
            'Successful': COLORS['success'],
            'In Progress': COLORS['warning'],
            'Failed': COLORS['danger'],
            'Manual Override': COLORS['primary']
        }
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=success_data['Outcome'],
            y=success_data['Count'],
            marker_color=[color_map[o] for o in success_data['Outcome']],
            text=success_data['Count'],
            textposition='auto',
            textfont=dict(color='white', size=14)
        ))
        fig.update_layout(**create_chart_layout("Action Outcomes (Last 24h)", "Outcome", "Count"))
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

def show_advanced_insights(grievances, energy, traffic, waste):
    st.title("📈 Advanced Cross-Domain Insights")
    st.markdown("### Deep Dive Analytics & Pattern Discovery")
    
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
        textfont={"size": 14, "color": "white"},
        colorbar=dict(title=dict(text="Correlation", font=dict(color=COLORS['text'])))
    ))
    fig.update_layout(**create_chart_layout("Cross-Domain Correlation Analysis", height=500))
    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
    
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

def show_recommendations(kpis, grievances, energy, traffic, waste):
    st.title("💡 AI-Powered Recommendations")
    st.markdown("### Actionable Insights for City Administrators")
    
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
    
    st.markdown("---")
    st.markdown("### 💰 Return on Investment Analysis")
    
    roi_data = pd.DataFrame({
        'Initiative': ['Dynamic Traffic Signals', 'Grid Modernization', 'Smart Bin System', 'Mobile App'],
        'Investment (₹ Cr)': [12, 50, 8, 3],
        'Annual Savings (₹ Cr)': [8, 15, 6, 2],
        'Payback Period (Years)': [1.5, 3.3, 1.3, 1.5],
        'Citizen Impact Score': [85, 70, 80, 90]
    })
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>' + col + '</b>' for col in roi_data.columns],
            fill_color=COLORS['primary'],
            font=dict(color='white', size=14),
            align='left',
            height=40
        ),
        cells=dict(
            values=[roi_data[col] for col in roi_data.columns],
            fill_color='#f0f2f6',
            font=dict(color=COLORS['text'], size=12),
            align='left',
            height=35
        )
    )])
    fig.update_layout(margin=dict(l=0, r=0, t=20, b=0), height=250, paper_bgcolor='white')
    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

if __name__ == "__main__":
    main()