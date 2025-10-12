#!/usr/bin/env python3
"""
Streamlit Dashboard Application
Professional Trading Bot Dashboard with Enterprise Design
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import asyncio
import sys
from pathlib import Path
import logging

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="🤖 Professional Trading Bot Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo',
        'Report a bug': "https://github.com/your-repo/issues",
        'About': "# Professional Trading Bot Dashboard\nEnterprise-grade trading system with ML-powered insights"
    }
)

# Custom CSS for enterprise design
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #1f2937;
        --secondary-color: #3b82f6;
        --accent-color: #10b981;
        --danger-color: #ef4444;
        --warning-color: #f59e0b;
        --background-color: #f8fafc;
        --card-background: #ffffff;
        --text-primary: #1f2937;
        --text-secondary: #6b7280;
    }

    /* Global styles */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }

    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }

    /* Metric cards */
    .metric-card {
        background: var(--card-background);
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        border-left: 4px solid var(--accent-color);
        margin-bottom: 1rem;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
    }

    .metric-label {
        font-size: 0.875rem;
        color: var(--text-secondary);
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Status indicators */
    .status-running {
        color: var(--accent-color);
        font-weight: 600;
    }

    .status-stopped {
        color: var(--danger-color);
        font-weight: 600;
    }

    /* Sidebar styling */
    .css-1d391kg {
        background-color: var(--primary-color);
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: var(--card-background);
        border-radius: 5px;
        border: 1px solid #e5e7eb;
    }

    .stTabs [aria-selected="true"] {
        background-color: var(--secondary-color);
        color: white;
    }

    /* Chart containers */
    .chart-container {
        background: var(--card-background);
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
    }

    /* Button styling */
    .stButton > button {
        background-color: var(--secondary-color);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.2s;
    }

    .stButton > button:hover {
        background-color: #2563eb;
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    /* Success/Error messages */
    .stSuccess {
        background-color: #d1fae5;
        border: 1px solid #10b981;
        border-radius: 5px;
        padding: 1rem;
    }

    .stError {
        background-color: #fee2e2;
        border: 1px solid #ef4444;
        border-radius: 5px;
        padding: 1rem;
    }

    .stWarning {
        background-color: #fef3c7;
        border: 1px solid #f59e0b;
        border-radius: 5px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Mock data for demonstration
@st.cache_data
def get_mock_data():
    """Generate mock data for the dashboard"""
    # Portfolio history
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='H')
    portfolio_values = [10000 + i * 10 + (i % 7) * 50 for i in range(len(dates))]
    
    portfolio_history = pd.DataFrame({
        'timestamp': dates,
        'total_value': portfolio_values
    })
    
    # Recent trades
    recent_trades = pd.DataFrame({
        'symbol': ['BTC/USDT', 'ETH/USDT', 'ADA/USDT', 'SOL/USDT', 'DOT/USDT'],
        'side': ['BUY', 'SELL', 'BUY', 'SELL', 'BUY'],
        'amount': [0.1, 2.5, 1000, 5.2, 50],
        'price': [42150.0, 2650.0, 0.45, 95.0, 6.8],
        'pnl': [150.0, -75.0, 25.0, 200.0, -30.0],
        'timestamp': [datetime.now() - timedelta(hours=i) for i in range(5)]
    })
    
    # Active positions
    active_positions = pd.DataFrame({
        'symbol': ['BTC/USDT', 'ETH/USDT', 'ADA/USDT'],
        'size': [0.15, 3.2, 2000],
        'entry_price': [42000.0, 2600.0, 0.44],
        'current_price': [42150.0, 2650.0, 0.45],
        'unrealized_pnl': [22.5, 160.0, 200.0],
        'pnl_pct': [0.54, 1.92, 2.27]
    })
    
    return portfolio_history, recent_trades, active_positions

def render_header():
    """Render the main header"""
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Professional Trading Bot Dashboard</h1>
        <p>Enterprise-grade AI-powered trading system with real-time monitoring and risk management</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render the sidebar with controls"""
    with st.sidebar:
        st.markdown("## 🎛️ Bot Controls")
        
        # Bot status
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown("**Status:**")
        with col2:
            st.markdown('<span class="status-running">🟢 Running</span>', unsafe_allow_html=True)
        
        # Key metrics
        st.markdown("### 📊 Key Metrics")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Portfolio Value", "$12,500.00", "2.5%")
        with col2:
            st.metric("Open Positions", "3", "1")
        
        st.metric("Available Capital", "$5,000.00")
        st.metric("Total P&L", "$382.50", "3.1%")
        
        st.markdown("---")
        
        # Bot controls
        st.markdown("### 🤖 Bot Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶️ Start", use_container_width=True):
                st.success("Bot started!")
        
        with col2:
            if st.button("⏸️ Pause", use_container_width=True):
                st.warning("Bot paused!")
        
        if st.button("🛑 Emergency Stop", use_container_width=True):
            st.error("Bot stopped!")
        
        st.markdown("---")
        
        # Settings
        st.markdown("### ⚙️ Settings")
        
        refresh_rate = st.selectbox(
            "Refresh Rate",
            ["5 seconds", "10 seconds", "30 seconds", "1 minute"],
            index=0
        )
        
        auto_trading = st.checkbox("Auto Trading", value=True)
        risk_management = st.checkbox("Risk Management", value=True)
        
        st.markdown("---")
        
        # System info
        st.markdown("### ℹ️ System Info")
        st.text(f"Version: 2.1.0")
        st.text(f"Uptime: 2d 14h 32m")
        st.text(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")

def render_portfolio_tab():
    """Render the portfolio overview tab"""
    st.markdown("## 📊 Portfolio Overview")
    
    # Get mock data
    portfolio_history, recent_trades, active_positions = get_mock_data()
    
    # Portfolio value chart
    with st.container():
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=portfolio_history['timestamp'],
            y=portfolio_history['total_value'],
            mode='lines',
            name='Portfolio Value',
            line=dict(color='#10b981', width=3),
            fill='tonexty'
        ))
        
        fig.update_layout(
            title="Portfolio Value Over Time",
            xaxis_title="Time",
            yaxis_title="Value ($)",
            template="plotly_white",
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Performance metrics
    st.markdown("### 📈 Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <p class="metric-value">$12,500.00</p>
            <p class="metric-label">Current Value</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <p class="metric-value">+3.1%</p>
            <p class="metric-label">Total Return</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <p class="metric-value">68.5%</p>
            <p class="metric-label">Win Rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <p class="metric-value">47</p>
            <p class="metric-label">Total Trades</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent trades
    st.markdown("### 📋 Recent Trades")
    st.dataframe(
        recent_trades,
        use_container_width=True,
        hide_index=True
    )

def render_positions_tab():
    """Render the positions tab"""
    st.markdown("## 📈 Open Positions")
    
    _, recent_trades, active_positions = get_mock_data()
    
    if not active_positions.empty:
        # Positions table
        st.markdown("### Current Positions")
        st.dataframe(
            active_positions,
            use_container_width=True,
            hide_index=True
        )
        
        # Position distribution chart
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                active_positions,
                values='size',
                names='symbol',
                title="Position Distribution by Size",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # P&L summary
            total_pnl = active_positions['unrealized_pnl'].sum()
            avg_pnl = active_positions['unrealized_pnl'].mean()
            
            st.markdown("### P&L Summary")
            st.markdown(f"""
            <div class="metric-card">
                <p class="metric-value">${total_pnl:.2f}</p>
                <p class="metric-label">Total Unrealized P&L</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <p class="metric-value">${avg_pnl:.2f}</p>
                <p class="metric-label">Average P&L per Position</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No open positions")

def render_ml_models_tab():
    """Render the ML models tab"""
    st.markdown("## 🤖 Machine Learning Models")
    
    # Model performance
    st.markdown("### Model Performance")
    
    models_data = {
        'LSTM Neural Network': {'accuracy': 0.78, 'status': 'Active', 'last_trained': '2 hours ago'},
        'Random Forest': {'accuracy': 0.82, 'status': 'Active', 'last_trained': '1 hour ago'},
        'Gradient Boosting': {'accuracy': 0.80, 'status': 'Active', 'last_trained': '1 hour ago'},
        'Support Vector Machine': {'accuracy': 0.75, 'status': 'Training', 'last_trained': '30 minutes ago'},
    }
    
    for model_name, metrics in models_data.items():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <p class="metric-value">{metrics['accuracy']:.1%}</p>
                <p class="metric-label">{model_name} Accuracy</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            status_color = "var(--accent-color)" if metrics['status'] == 'Active' else "var(--warning-color)"
            st.markdown(f"""
            <div class="metric-card">
                <p class="metric-value" style="color: {status_color}">{metrics['status']}</p>
                <p class="metric-label">Status</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <p class="metric-value">{metrics['last_trained']}</p>
                <p class="metric-label">Last Trained</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
    
    # Feature importance
    st.markdown("### Feature Importance")
    
    feature_importance = {
        'RSI': 0.25,
        'MACD': 0.20,
        'Volume': 0.18,
        'Price Momentum': 0.15,
        'Bollinger Bands': 0.12,
        'Moving Averages': 0.10,
    }
    
    fig = px.bar(
        x=list(feature_importance.values()),
        y=list(feature_importance.keys()),
        orientation='h',
        title="Feature Importance (Random Forest)",
        color=list(feature_importance.values()),
        color_continuous_scale='Viridis'
    )
    fig.update_layout(
        height=400,
        template="plotly_white",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Model controls
    st.markdown("### Model Controls")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Retrain All Models", use_container_width=True):
            st.success("Model retraining initiated!")
    
    with col2:
        if st.button("📊 Update Performance", use_container_width=True):
            st.success("Performance metrics updated!")
    
    with col3:
        if st.button("💾 Save Models", use_container_width=True):
            st.success("Models saved successfully!")

def render_risk_tab():
    """Render the risk management tab"""
    st.markdown("## ⚠️ Risk Management")
    
    # Risk metrics
    st.markdown("### Risk Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <p class="metric-value">45%</p>
            <p class="metric-label">Total Exposure</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="metric-card">
            <p class="metric-value">8%</p>
            <p class="metric-label">Max Drawdown</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <p class="metric-value">3%</p>
            <p class="metric-label">VaR (95%)</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="metric-card">
            <p class="metric-value">1.2</p>
            <p class="metric-label">Sharpe Ratio</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <p class="metric-value">25%</p>
            <p class="metric-label">Volatility</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="metric-card">
            <p class="metric-value">15%</p>
            <p class="metric-label">Concentration Risk</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Risk limits
    st.markdown("### Risk Limits")
    
    risk_limits = {
        'Max Position Size': '10%',
        'Max Total Exposure': '80%',
        'Max Drawdown': '15%',
        'Max VaR': '5%',
        'Max Concentration': '30%',
    }
    
    for limit_name, limit_value in risk_limits.items():
        col1, col2 = st.columns([2, 1])
        with col1:
            st.text(limit_name)
        with col2:
            st.text(limit_value)
    
    # Risk alerts
    st.markdown("### Risk Alerts")
    
    alerts = [
        {"level": "INFO", "message": "All risk metrics within normal limits"},
        {"level": "WARNING", "message": "Portfolio volatility approaching limit"},
    ]
    
    for alert in alerts:
        if alert['level'] == 'WARNING':
            st.warning(f"⚠️ {alert['message']}")
        else:
            st.info(f"ℹ️ {alert['message']}")

def render_logs_tab():
    """Render the logs tab"""
    st.markdown("## 📋 System Logs")
    
    # Log level filter
    log_level = st.selectbox(
        "Filter by Log Level",
        ["ALL", "INFO", "WARNING", "ERROR", "CRITICAL", "SUCCESS"]
    )
    
    # Mock logs
    logs = [
        {"timestamp": "2024-01-15 10:30:15", "level": "INFO", "message": "Trading bot started successfully"},
        {"timestamp": "2024-01-15 10:30:20", "level": "INFO", "message": "Connected to Binance exchange"},
        {"timestamp": "2024-01-15 10:31:05", "level": "INFO", "message": "Generated BUY signal for BTC/USDT (confidence: 0.85)"},
        {"timestamp": "2024-01-15 10:31:10", "level": "SUCCESS", "message": "Executed BUY order for BTC/USDT at $42,150"},
        {"timestamp": "2024-01-15 10:32:00", "level": "WARNING", "message": "Portfolio exposure approaching limit"},
        {"timestamp": "2024-01-15 10:33:15", "level": "INFO", "message": "Risk management check passed"},
        {"timestamp": "2024-01-15 10:34:30", "level": "SUCCESS", "message": "Position closed with 2.5% profit"},
        {"timestamp": "2024-01-15 10:35:45", "level": "INFO", "message": "ML model retrained successfully"},
    ]
    
    # Filter logs
    if log_level != "ALL":
        logs = [log for log in logs if log['level'] == log_level]
    
    # Display logs
    for log in logs[-20:]:  # Show last 20 logs
        timestamp = log['timestamp']
        level = log['level']
        message = log['message']
        
        if level == "ERROR" or level == "CRITICAL":
            st.error(f"🔴 {timestamp} | {level} | {message}")
        elif level == "WARNING":
            st.warning(f"🟡 {timestamp} | {level} | {message}")
        elif level == "SUCCESS":
            st.success(f"🟢 {timestamp} | {level} | {message}")
        else:
            st.info(f"🔵 {timestamp} | {level} | {message}")
    
    # Auto-refresh
    if st.checkbox("Auto-refresh logs"):
        st.markdown("Logs will refresh automatically every 5 seconds")
        st.rerun()

def main():
    """Main Streamlit application"""
    try:
        # Render header
        render_header()
        
        # Render sidebar
        render_sidebar()
        
        # Main content tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Portfolio", 
            "📈 Positions", 
            "🤖 ML Models", 
            "⚠️ Risk", 
            "📋 Logs"
        ])
        
        with tab1:
            render_portfolio_tab()
        
        with tab2:
            render_positions_tab()
        
        with tab3:
            render_ml_models_tab()
        
        with tab4:
            render_risk_tab()
        
        with tab5:
            render_logs_tab()
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #6b7280; padding: 1rem;">
            <p>🤖 Professional Trading Bot Dashboard v2.1.0 | Powered by AI & Machine Learning</p>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        logger.error(f"Error in main application: {e}")
        st.error(f"Application error: {e}")

if __name__ == "__main__":
    main()