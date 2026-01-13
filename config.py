"""
Configuration file for Smart Cities Analytics Platform
Contains all constants, thresholds, and configuration parameters
"""

# File paths
DATA_FILES = {
    'grievances': 'pune_citizen_grievances.csv',
    'energy': 'pune_energy_consumption.csv',
    'traffic': 'pune_traffic_flow.csv',
    'waste': 'pune_waste_management.csv'
}

# Zones
ZONES = ['Hinjewadi', 'Kothrud', 'Swargate', 'Koregaon Park', 'Hadapsar', 'Viman Nagar']

# Thresholds for alerts
THRESHOLDS = {
    'traffic': {
        'high_congestion': 80,
        'moderate_congestion': 50,
        'low_speed': 20  # km/h
    },
    'energy': {
        'low_voltage': 220,  # Volts
        'critical_voltage': 200,
        'high_consumption': 5000  # kWh
    },
    'waste': {
        'bin_full': 85,  # percentage
        'bin_warning': 70,
        'max_missed_pickups': 2,
        'min_segregation': 75  # percentage
    },
    'grievances': {
        'sla_critical': 1,  # days
        'sla_warning': 2,
        'target_resolution_rate': 0.70
    }
}

# KPI targets
TARGETS = {
    'traffic_flow_efficiency': 0.70,
    'grievance_resolution_rate': 0.75,
    'waste_segregation': 0.80,
    'energy_reliability': 0.95  # (1 - power_cut_rate)
}

# Weights for zone stress calculation
STRESS_WEIGHTS = {
    'traffic': 1.0,
    'energy': 20.0,  # multiplier for power cuts
    'waste': 10.0,  # multiplier for missed pickups
    'grievances': 5.0  # multiplier for open grievances
}

# Color schemes for visualizations
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
    'grievances': '#f093fb'
}

# Chart configurations
CHART_CONFIG = {
    'height': 400,
    'template': 'plotly_white',
    'font_family': 'Arial, sans-serif'
}

# Department categories for grievances
DEPARTMENTS = {
    'Traffic': ['Traffic Signal Not Working', 'Potholes', 'Illegal Parking'],
    'Energy': ['Frequent Power Cut', 'Voltage Fluctuation', 'Meter Fault'],
    'Waste': ['Garbage Dumped on Road', 'Bin Overflowing', 'Dead Animal'],
    'Water': ['No Water Supply', 'Contaminated Water']
}

# ROI data for recommendations
ROI_INITIATIVES = {
    'Dynamic Traffic Signals': {
        'investment': 12,  # Crores
        'annual_savings': 8,
        'impact_score': 85
    },
    'Grid Modernization': {
        'investment': 50,
        'annual_savings': 15,
        'impact_score': 70
    },
    'Smart Bin System': {
        'investment': 8,
        'annual_savings': 6,
        'impact_score': 80
    },
    'Mobile App for Grievances': {
        'investment': 3,
        'annual_savings': 2,
        'impact_score': 90
    }
}

# Recommendation templates
RECOMMENDATION_TEMPLATES = {
    'high_congestion': {
        'priority': 'HIGH',
        'category': 'Traffic',
        'title': 'Implement Dynamic Traffic Signal Management',
        'impact': 'Potential 15-20% reduction in congestion',
        'cost': 'Medium',
        'timeline': '3-6 months'
    },
    'power_reliability': {
        'priority': 'HIGH',
        'category': 'Energy',
        'title': 'Strengthen Grid Infrastructure in Vulnerable Zones',
        'impact': 'Improve service reliability by 30%',
        'cost': 'High',
        'timeline': '6-12 months'
    },
    'waste_optimization': {
        'priority': 'MEDIUM',
        'category': 'Waste',
        'title': 'Optimize Waste Collection Routes',
        'impact': '25% reduction in operational costs',
        'cost': 'Low',
        'timeline': '1-3 months'
    },
    'grievance_improvement': {
        'priority': 'HIGH',
        'category': 'Citizen Services',
        'title': 'Enhance Grievance Resolution Process',
        'impact': 'Improve citizen satisfaction by 40%',
        'cost': 'Low',
        'timeline': 'Immediate'
    },
    'segregation_campaign': {
        'priority': 'MEDIUM',
        'category': 'Waste',
        'title': 'Launch Waste Segregation Awareness Campaign',
        'impact': 'Increase recycling rate by 20%',
        'cost': 'Low',
        'timeline': '1-2 months'
    }
}

# Budget allocation recommendations
BUDGET_ALLOCATION = {
    'Traffic': 30,  # percentage
    'Energy': 40,
    'Waste': 20,
    'Digital Infrastructure': 10
}

# Implementation roadmap
IMPLEMENTATION_ROADMAP = [
    {
        'month': 'Month 1',
        'actions': 'Deploy mobile app, Start traffic signal pilot',
        'impact': 'Quick wins in grievances'
    },
    {
        'month': 'Month 2',
        'actions': 'Expand traffic signals, IoT bin sensors pilot',
        'impact': '10% traffic improvement'
    },
    {
        'month': 'Month 3',
        'actions': 'Grid assessment, Citizen awareness campaign',
        'impact': '15% waste efficiency gain'
    },
    {
        'month': 'Month 4',
        'actions': 'Full IoT bin deployment, Grid upgrades begin',
        'impact': '20% traffic & waste improvement'
    },
    {
        'month': 'Month 5',
        'actions': 'Traffic system citywide, Continue grid work',
        'impact': '25% overall improvement'
    },
    {
        'month': 'Month 6',
        'actions': 'Review & optimize all systems',
        'impact': 'Full system optimization'
    }
]

# Alert messages
ALERT_MESSAGES = {
    'critical': "⚠️ {count} CRITICAL ISSUES REQUIRE IMMEDIATE ATTENTION",
    'warning': "⚠️ {count} {type} detected",
    'success': "✅ {message}",
    'info': "ℹ️ {message}"
}

# Moving average window for trend analysis
TREND_WINDOW = 7  # days

# Day of week order
DAY_ORDER = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Peak hours definition
PEAK_HOURS = {
    'morning': (9, 11),  # 9 AM to 11 AM
    'evening': (18, 21)  # 6 PM to 9 PM
}