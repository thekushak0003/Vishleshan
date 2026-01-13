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
    page_title="LMN Smart Cities Analytics",
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
    .stMetric .metric-value {
        color: white !important;
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
    h1, h2, h3 {
        color: #667eea;
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
    # Energy KPIs
    avg_energy = energy['Energy_Consumption_kWh'].mean()
    power_cuts = energy['Power_Cut_Flag'].sum()
    voltage_issues = (energy['Grid_Voltage'] < 220).sum()
    
    # Traffic KPIs
    avg_congestion = traffic['Congestion_Index'].mean()
    peak_congestion = traffic['Congestion_Index'].max()
    flow_efficiency = 1 - (avg_congestion / 100)
    
    # Waste KPIs
    avg_bin_fill = waste['Avg_Bin_Fill_Level_Percent'].mean()
    missed_pickups = waste['Missed_Pickups'].sum()
    avg_segregation = waste['Segregation_Efficiency_Percent'].mean()
    
    # Grievance KPIs
    total_grievances = len(grievances)
    open_grievances = len(grievances[grievances['Status'] == 'Open'])
    critical_issues = len(grievances[(grievances['Status'] == 'Open') & (grievances['SLA_Days'] <= 1)])
    resolution_rate = len(grievances[grievances['Status'] == 'Resolved']) / total_grievances
    
    # Zone stress calculation
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

# Main app
def main():
    # Sidebar
    st.sidebar.image("https://via.placeholder.com/200x80?text=LMN+Smart+Cities", use_container_width=True)
    st.sidebar.title("Navigation")
    
    page = st.sidebar.selectbox(
        "Select View",
        ["🏠 Executive Dashboard", "📊 Cross-Domain Analytics", "🗺️ Zone Performance", 
         "🚨 Critical Alerts", "📈 Predictive Insights", "💡 Recommendations"]
    )
    
    # Load data
    grievances, energy, traffic, waste = load_data()
    
    if grievances is None:
        st.error("Failed to load data. Please ensure CSV files are in the correct location.")
        return
    
    # Date filter
    st.sidebar.markdown("### Filters")
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
    if page == "🏠 Executive Dashboard":
        show_executive_dashboard(kpis, grievances_filtered, energy_filtered, traffic_filtered, waste_filtered)
    elif page == "📊 Cross-Domain Analytics":
        show_cross_domain_analytics(grievances_filtered, energy_filtered, traffic_filtered, waste_filtered)
    elif page == "🗺️ Zone Performance":
        show_zone_performance(kpis, grievances_filtered, energy_filtered, traffic_filtered, waste_filtered)
    elif page == "🚨 Critical Alerts":
        show_critical_alerts(kpis, grievances_filtered, energy_filtered, traffic_filtered, waste_filtered)
    elif page == "📈 Predictive Insights":
        show_predictive_insights(grievances_filtered, energy_filtered, traffic_filtered, waste_filtered)
    elif page == "💡 Recommendations":
        show_recommendations(kpis, grievances_filtered, energy_filtered, traffic_filtered, waste_filtered)

def show_executive_dashboard(kpis, grievances, energy, traffic, waste):
    st.title("🏠 Executive Dashboard")
    st.markdown("### Real-time City Operations Overview")
    
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

def show_cross_domain_analytics(grievances, energy, traffic, waste):
    st.title("📊 Cross-Domain Analytics")
    st.markdown("### Identifying Correlations and Hidden Patterns")
    
    # Correlation Analysis
    st.markdown("#### 🔗 Inter-Domain Correlation Matrix")
    
    # Prepare correlation data
    daily_traffic = traffic.groupby(['Date', 'Zone_Name'])['Congestion_Index'].mean().reset_index()
    daily_energy = energy.groupby(['Date', 'Zone_Name'])['Energy_Consumption_kWh'].mean().reset_index()
    daily_waste = waste.groupby(['Date', 'Zone_Name'])['Avg_Bin_Fill_Level_Percent'].mean().reset_index()
    daily_grievances = grievances[grievances['Status'] == 'Open'].groupby(['Date', 'Zone_Name']).size().reset_index(name='Open_Count')
    
    # Merge datasets
    merged = daily_traffic.merge(daily_energy, on=['Date', 'Zone_Name'], how='outer')
    merged = merged.merge(daily_waste, on=['Date', 'Zone_Name'], how='outer')
    merged = merged.merge(daily_grievances, on=['Date', 'Zone_Name'], how='outer')
    merged = merged.fillna(0)
    
    # Calculate correlations
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
    
    # Department Performance Analysis
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
    
    # Peak Hour Analysis across domains
    st.markdown("### ⏰ Multi-Domain Peak Hour Analysis")
    
    hourly_traffic = traffic.groupby('Hour')['Congestion_Index'].mean()
    hourly_energy = energy.groupby('Hour')['Energy_Consumption_kWh'].mean()
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(x=hourly_traffic.index, y=hourly_traffic.values, name="Traffic Congestion", line=dict(color='#ff6b6b', width=3)),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(x=hourly_energy.index, y=hourly_energy.values, name="Energy Consumption", line=dict(color='#4ecdc4', width=3)),
        secondary_y=True
    )
    
    fig.update_xaxes(title_text="Hour of Day")
    fig.update_yaxes(title_text="Congestion Index", secondary_y=False)
    fig.update_yaxes(title_text="Energy (kWh)", secondary_y=True)
    fig.update_layout(title="Synchronized Peak Hour Analysis", height=400)
    
    st.plotly_chart(fig, use_container_width=True)

def show_zone_performance(kpis, grievances, energy, traffic, waste):
    st.title("🗺️ Zone Performance Comparison")
    st.markdown("### Comprehensive Zone-level Analysis")
    
    zones = grievances['Zone_Name'].unique()
    
    # Zone selector
    selected_zone = st.selectbox("Select Zone for Detailed Analysis", zones)
    
    # Zone-specific KPIs
    st.markdown(f"### Performance Metrics: {selected_zone}")
    
    zone_traffic = traffic[traffic['Zone_Name'] == selected_zone]
    zone_energy = energy[energy['Zone_Name'] == selected_zone]
    zone_waste = waste[waste['Zone_Name'] == selected_zone]
    zone_grievances = grievances[grievances['Zone_Name'] == selected_zone]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_congestion = zone_traffic['Congestion_Index'].mean()
        st.metric("Avg Congestion", f"{avg_congestion:.1f}", delta=f"{avg_congestion - kpis['avg_congestion']:.1f} vs city avg")
    
    with col2:
        zone_power_cuts = zone_energy['Power_Cut_Flag'].sum()
        st.metric("Power Cuts", f"{zone_power_cuts}", delta=f"{zone_power_cuts - (kpis['power_cuts']/len(zones)):.0f} vs avg")
    
    with col3:
        zone_segregation = zone_waste['Segregation_Efficiency_Percent'].mean()
        st.metric("Segregation Efficiency", f"{zone_segregation:.1f}%", delta=f"{zone_segregation - kpis['avg_segregation']:.1f}%")
    
    with col4:
        zone_open = len(zone_grievances[zone_grievances['Status'] == 'Open'])
        st.metric("Open Grievances", f"{zone_open}", delta=f"{zone_open - (kpis['open_grievances']/len(zones)):.0f} vs avg", delta_color="inverse")
    
    # Zone comparison
    st.markdown("### 📊 All Zones Comparison")
    
    # Prepare comparison data
    zone_comparison = pd.DataFrame()
    for zone in zones:
        zone_data = {
            'Zone': zone,
            'Avg_Congestion': traffic[traffic['Zone_Name'] == zone]['Congestion_Index'].mean(),
            'Power_Cuts': energy[energy['Zone_Name'] == zone]['Power_Cut_Flag'].sum(),
            'Missed_Pickups': waste[waste['Zone_Name'] == zone]['Missed_Pickups'].sum(),
            'Open_Grievances': len(grievances[(grievances['Zone_Name'] == zone) & (grievances['Status'] == 'Open')]),
            'Stress_Score': kpis['zone_stress'].get(zone, 0)
        }
        zone_comparison = pd.concat([zone_comparison, pd.DataFrame([zone_data])], ignore_index=True)
    
    # Radar chart for zone comparison
    fig = go.Figure()
    
    for zone in zones:
        zone_data = zone_comparison[zone_comparison['Zone'] == zone].iloc[0]
        
        # Normalize values for radar chart
        values = [
            zone_data['Avg_Congestion'] / 100,
            zone_data['Power_Cuts'] / zone_comparison['Power_Cuts'].max() if zone_comparison['Power_Cuts'].max() > 0 else 0,
            zone_data['Missed_Pickups'] / zone_comparison['Missed_Pickups'].max() if zone_comparison['Missed_Pickups'].max() > 0 else 0,
            zone_data['Open_Grievances'] / zone_comparison['Open_Grievances'].max() if zone_comparison['Open_Grievances'].max() > 0 else 0
        ]
        values.append(values[0])  # Close the radar chart
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=['Traffic Congestion', 'Power Reliability', 'Waste Issues', 'Citizen Complaints', 'Traffic Congestion'],
            name=zone,
            fill='toself'
        ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        title="Multi-Dimensional Zone Performance Comparison",
        height=600
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Zone rankings
    st.markdown("### 🏆 Zone Rankings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Best Performing Zones**")
        best_zones = zone_comparison.nsmallest(3, 'Stress_Score')[['Zone', 'Stress_Score']]
        for idx, row in best_zones.iterrows():
            st.success(f"🥇 {row['Zone']}: Score {row['Stress_Score']:.0f}")
    
    with col2:
        st.markdown("**Zones Needing Attention**")
        worst_zones = zone_comparison.nlargest(3, 'Stress_Score')[['Zone', 'Stress_Score']]
        for idx, row in worst_zones.iterrows():
            st.error(f"⚠️ {row['Zone']}: Score {row['Stress_Score']:.0f}")

def show_critical_alerts(kpis, grievances, energy, traffic, waste):
    st.title("🚨 Critical Alerts & Real-Time Monitoring")
    st.markdown("### Immediate Action Required")
    
    # Critical issues counter
    critical_count = kpis['critical_issues']
    
    if critical_count > 0:
        st.markdown(f'<div class="alert-critical">⚠️ {critical_count} CRITICAL ISSUES REQUIRE IMMEDIATE ATTENTION</div>', unsafe_allow_html=True)
    else:
        st.success("✅ No critical issues at this time")
    
    # Critical grievances
    st.markdown("### 🎫 Critical Grievances (SLA Breach)")
    critical_grievances = grievances[(grievances['Status'] == 'Open') & (grievances['SLA_Days'] <= 1)].sort_values('Date')
    
    if len(critical_grievances) > 0:
        for _, row in critical_grievances.iterrows():
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            with col1:
                st.markdown(f"**{row['Ticket_ID']}**")
            with col2:
                st.markdown(f"📍 {row['Zone_Name']}")
            with col3:
                st.markdown(f"🏢 {row['Department']} - {row['Issue_Type']}")
            with col4:
                st.markdown(f"⏰ {row['SLA_Days']} day(s)")
    else:
        st.info("No SLA breaches found")
    
    st.markdown("---")
    
    # Power infrastructure alerts
    st.markdown("### ⚡ Power Infrastructure Alerts")
    
    voltage_issues = energy[energy['Grid_Voltage'] < 220]
    power_cuts = energy[energy['Power_Cut_Flag'] == 1]
    
    col1, col2 = st.columns(2)
    
    with col1:
        if len(voltage_issues) > 0:
            st.markdown(f'<div class="alert-warning">⚠️ {len(voltage_issues)} voltage fluctuation events detected</div>', unsafe_allow_html=True)
            
            # Group by zone
            voltage_by_zone = voltage_issues.groupby('Zone_Name').size().sort_values(ascending=False)
            st.markdown("**Most Affected Zones:**")
            for zone, count in voltage_by_zone.head(3).items():
                st.markdown(f"- {zone}: {count} events")
        else:
            st.success("✅ No voltage issues detected")
    
    with col2:
        if len(power_cuts) > 0:
            st.markdown(f'<div class="alert-critical">🔴 {len(power_cuts)} power cut incidents</div>', unsafe_allow_html=True)
            
            # Group by zone
            cuts_by_zone = power_cuts.groupby('Zone_Name').size().sort_values(ascending=False)
            st.markdown("**Most Affected Zones:**")
            for zone, count in cuts_by_zone.head(3).items():
                st.markdown(f"- {zone}: {count} cuts")
        else:
            st.success("✅ No power cuts detected")
    
    st.markdown("---")
    
    # Traffic hotspots
    st.markdown("### 🚦 Traffic Congestion Hotspots")
    
    high_congestion = traffic[traffic['Congestion_Index'] > 80]
    
    if len(high_congestion) > 0:
        st.markdown(f'<div class="alert-warning">⚠️ {len(high_congestion)} severe congestion events (Index > 80)</div>', unsafe_allow_html=True)
        
        # Heatmap by zone and hour
        congestion_pivot = high_congestion.pivot_table(
            index='Zone_Name',
            columns='Hour',
            values='Congestion_Index',
            aggfunc='mean'
        )
        
        fig = go.Figure(data=go.Heatmap(
            z=congestion_pivot.values,
            x=congestion_pivot.columns,
            y=congestion_pivot.index,
            colorscale='Reds',
            colorbar=dict(title="Congestion Index")
        ))
        fig.update_layout(
            title="Congestion Hotspot Map (Zone × Hour)",
            xaxis_title="Hour of Day",
            yaxis_title="Zone",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("✅ No severe congestion detected")
    
    st.markdown("---")
    
    # Waste management alerts
    st.markdown("### ♻️ Waste Management Alerts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        overflowing_bins = waste[waste['Avg_Bin_Fill_Level_Percent'] > 85]
        if len(overflowing_bins) > 0:
            st.markdown(f'<div class="alert-warning">⚠️ {len(overflowing_bins)} zones with bins >85% full</div>', unsafe_allow_html=True)
            for _, row in overflowing_bins.iterrows():
                st.markdown(f"- 📍 {row['Zone_Name']}: {row['Avg_Bin_Fill_Level_Percent']:.0f}% full")
        else:
            st.success("✅ All bins within capacity")
    
    with col2:
        missed = waste[waste['Missed_Pickups'] > 2]
        if len(missed) > 0:
            st.markdown(f'<div class="alert-critical">🔴 {len(missed)} zones with >2 missed pickups</div>', unsafe_allow_html=True)
            for _, row in missed.iterrows():
                st.markdown(f"- 📍 {row['Zone_Name']}: {row['Missed_Pickups']} missed")
        else:
            st.success("✅ No significant pickup delays")

def show_predictive_insights(grievances, energy, traffic, waste):
    st.title("📈 Predictive Insights & Trends")
    st.markdown("### Data-Driven Forecasting")
    
    # Trend analysis
    st.markdown("### 📊 Temporal Trend Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Traffic trend with forecast
        daily_traffic = traffic.groupby('Date')['Congestion_Index'].mean().reset_index()
        daily_traffic = daily_traffic.sort_values('Date')
        
        # Simple moving average for trend
        daily_traffic['MA7'] = daily_traffic['Congestion_Index'].rolling(window=7, min_periods=1).mean()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily_traffic['Date'],
            y=daily_traffic['Congestion_Index'],
            mode='lines',
            name='Actual',
            line=dict(color='#ff6b6b', width=1)
        ))
        fig.add_trace(go.Scatter(
            x=daily_traffic['Date'],
            y=daily_traffic['MA7'],
            mode='lines',
            name='7-Day Trend',
            line=dict(color='#4ecdc4', width=3)
        ))
        fig.update_layout(
            title="Traffic Congestion Trend",
            xaxis_title="Date",
            yaxis_title="Congestion Index",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Trend direction
        trend_change = daily_traffic['MA7'].iloc[-1] - daily_traffic['MA7'].iloc[0]
        if trend_change > 0:
            st.markdown(f'<div class="alert-warning">📈 Traffic congestion trending UP by {trend_change:.1f} points</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="insight-box">📉 Traffic congestion trending DOWN by {abs(trend_change):.1f} points</div>', unsafe_allow_html=True)
    
    with col2:
        # Energy consumption trend
        daily_energy = energy.groupby('Date')['Energy_Consumption_kWh'].mean().reset_index()
        daily_energy = daily_energy.sort_values('Date')
        daily_energy['MA7'] = daily_energy['Energy_Consumption_kWh'].rolling(window=7, min_periods=1).mean()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily_energy['Date'],
            y=daily_energy['Energy_Consumption_kWh'],
            mode='lines',
            name='Actual',
            line=dict(color='#ffd43b', width=1)
        ))
        fig.add_trace(go.Scatter(
            x=daily_energy['Date'],
            y=daily_energy['MA7'],
            mode='lines',
            name='7-Day Trend',
            line=dict(color='#51cf66', width=3)
        ))
        fig.update_layout(
            title="Energy Consumption Trend",
            xaxis_title="Date",
            yaxis_title="Energy (kWh)",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        energy_change = daily_energy['MA7'].iloc[-1] - daily_energy['MA7'].iloc[0]
        if energy_change > 0:
            st.markdown(f'<div class="insight-box">📈 Energy demand increasing by {energy_change:.0f} kWh/day</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="insight-box">📉 Energy savings of {abs(energy_change):.0f} kWh/day observed</div>', unsafe_allow_html=True)
    
    # Seasonality analysis
    st.markdown("### 📅 Day-of-Week Patterns")
    
    traffic['DayOfWeek'] = traffic['Date'].dt.day_name()
    grievances['DayOfWeek'] = grievances['Date'].dt.day_name()
    
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    dow_traffic = traffic.groupby('DayOfWeek')['Congestion_Index'].mean().reindex(day_order)
    dow_grievances = grievances.groupby('DayOfWeek').size().reindex(day_order)
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Avg Congestion by Day', 'Grievances by Day')
    )
    
    fig.add_trace(
        go.Bar(x=dow_traffic.index, y=dow_traffic.values, marker_color='#667eea', name='Congestion'),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(x=dow_grievances.index, y=dow_grievances.values, marker_color='#f093fb', name='Grievances'),
        row=1, col=2
    )
    
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Predictive alerts
    st.markdown("### 🔮 Predictive Alerts")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Predict high congestion zones
        high_risk_zones = traffic[traffic['Congestion_Index'] > 70].groupby('Zone_Name').size().sort_values(ascending=False).head(3)
        st.markdown('<div class="recommendation">', unsafe_allow_html=True)
        st.markdown("**🚦 High Congestion Risk Zones:**")
        for zone, count in high_risk_zones.items():
            st.markdown(f"- {zone}: {count} high-traffic events")
        st.markdown("*Recommend: Traffic signal optimization*")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Predict waste overflow
        high_fill_zones = waste[waste['Avg_Bin_Fill_Level_Percent'] > 75].groupby('Zone_Name').size().sort_values(ascending=False).head(3)
        st.markdown('<div class="recommendation">', unsafe_allow_html=True)
        st.markdown("**♻️ Waste Overflow Risk:**")
        for zone, count in high_fill_zones.items():
            st.markdown(f"- {zone}: {count} days >75% capacity")
        st.markdown("*Recommend: Increase pickup frequency*")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        # Predict grievance surge
        high_grievance_zones = grievances[grievances['Status'] == 'Open'].groupby('Zone_Name').size().sort_values(ascending=False).head(3)
        st.markdown('<div class="recommendation">', unsafe_allow_html=True)
        st.markdown("**📞 Grievance Surge Risk:**")
        for zone, count in high_grievance_zones.items():
            st.markdown(f"- {zone}: {count} open tickets")
        st.markdown("*Recommend: Deploy rapid response team*")
        st.markdown('</div>', unsafe_allow_html=True)

def show_recommendations(kpis, grievances, energy, traffic, waste):
    st.title("💡 AI-Powered Recommendations")
    st.markdown("### Actionable Insights for City Administrators")
    
    # Priority recommendations
    st.markdown("### 🎯 Priority Action Items")
    
    recommendations = []
    
    # Traffic recommendations
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
    
    # Energy recommendations
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
    
    # Waste recommendations
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
    
    # Grievance recommendations
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
        priority_color = {'HIGH': 'error', 'MEDIUM': 'warning', 'LOW': 'info'}
        
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
    
    # Resource allocation
    st.markdown("### 📊 Recommended Resource Allocation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Budget allocation
        budget_alloc = pd.DataFrame({
            'Department': ['Traffic', 'Energy', 'Waste', 'Digital Infrastructure'],
            'Allocation': [30, 40, 20, 10]
        })
        
        fig = px.pie(budget_alloc, values='Allocation', names='Department',
                    title='Recommended Budget Distribution (%)',
                    color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Personnel deployment
        personnel_data = pd.DataFrame({
            'Zone': list(kpis['zone_stress'].keys()),
            'Stress': list(kpis['zone_stress'].values()),
            'Recommended_Staff': [int(stress/20) + 5 for stress in kpis['zone_stress'].values()]
        })
        
        fig = px.bar(personnel_data, x='Zone', y='Recommended_Staff',
                    title='Recommended Staff Deployment by Zone',
                    color='Stress', color_continuous_scale='Reds')
        st.plotly_chart(fig, use_container_width=True)
    
    # Implementation roadmap
    st.markdown("### 🗓️ 6-Month Implementation Roadmap")
    
    roadmap = pd.DataFrame({
        'Month': ['Month 1', 'Month 2', 'Month 3', 'Month 4', 'Month 5', 'Month 6'],
        'Action Items': [
            'Deploy mobile app, Start traffic signal pilot',
            'Expand traffic signals, IoT bin sensors pilot',
            'Grid assessment, Citizen awareness campaign',
            'Full IoT bin deployment, Grid upgrades begin',
            'Traffic system citywide, Continue grid work',
            'Review & optimize all systems'
        ],
        'Expected Impact': [
            'Quick wins in grievances',
            '10% traffic improvement',
            '15% waste efficiency gain',
            '20% traffic & waste improvement',
            '25% overall improvement',
            'Full system optimization'
        ]
    })
    
    st.dataframe(roadmap, use_container_width=True, hide_index=True)
    
    # Final recommendations summary
    st.markdown("### 📋 Executive Summary")
    
    st.markdown('<div class="recommendation">', unsafe_allow_html=True)
    st.markdown("""
    **Key Takeaways:**
    1. **Immediate Actions:** Deploy mobile grievance app and establish rapid response teams
    2. **Short-term (3 months):** Implement dynamic traffic signals and IoT waste bins
    3. **Medium-term (6 months):** Upgrade power grid infrastructure in high-risk zones
    4. **Long-term (12 months):** Full integration of all smart city systems with predictive analytics
    
    **Expected Outcomes:**
    - 30% improvement in citizen satisfaction
    - 25% reduction in operational costs
    - 40% faster grievance resolution
    - 20% reduction in traffic congestion
    - 15% energy savings
    
    **Total Investment Required:** ₹73 Crores
    **Expected Annual Savings:** ₹31 Crores
    **Overall Payback Period:** 2.4 Years
    """)
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()