"""
Main Streamlit application for Credit Insurance and Rating System Simulation.
Replicates the NetLogo CIES 9.1 model as a Python web application.
"""
import streamlit as st
import sys
import os
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Add nlogo directory to path
# This allows importing simulation modules from the nlogo directory
nlogo_path = os.path.join(os.path.dirname(__file__), 'nlogo')
sys.path.insert(0, nlogo_path)

# Import simulation world (linter may show warnings, but these are false positives)
from simulation.world import World

# Page configuration
st.set_page_config(
    page_title="Smart Credit Management System - Simulation",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional, minimal dashboard styling
st.markdown("""
<style>
    /* Main content area - tighter spacing */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
        max-width: 100%;
    }
    
    /* Metric cards - refined typography */
    [data-testid="stMetricValue"] {
        font-size: 1.75rem;
        font-weight: 600;
        color: #111827;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.8125rem;
        font-weight: 500;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.8125rem;
        font-weight: 500;
    }
    
    /* Section headers - minimal, professional */
    .dashboard-section {
        background: #f8fafc;
        padding: 0.75rem 1.25rem;
        border-radius: 6px;
        margin-bottom: 1rem;
        border-left: 3px solid #3b82f6;
        box-shadow: none;
    }
    
    .dashboard-section h2 {
        color: #1e293b;
        font-size: 1.125rem;
        font-weight: 600;
        margin: 0;
        letter-spacing: -0.01em;
    }
    
    .dashboard-section h3 {
        color: #1e293b;
        font-size: 1rem;
        font-weight: 600;
        margin: 0;
    }
    
    /* Rating badges - subtle, professional */
    .rating-badge {
        flex: 1;
        padding: 1.25rem;
        border-radius: 6px;
        text-align: center;
        background: white;
        border: 2px solid #e5e7eb;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }
    
    .rating-badge-a {
        border-color: #10b981;
        background: linear-gradient(to bottom, #ffffff 0%, #f0fdf4 100%);
    }
    
    .rating-badge-b {
        border-color: #f59e0b;
        background: linear-gradient(to bottom, #ffffff 0%, #fffbeb 100%);
    }
    
    .rating-badge-c {
        border-color: #ef4444;
        background: linear-gradient(to bottom, #ffffff 0%, #fef2f2 100%);
    }
    
    .rating-value {
        font-size: 2rem;
        font-weight: 600;
        display: block;
        margin-bottom: 0.25rem;
        color: #111827;
    }
    
    .rating-label {
        font-size: 0.8125rem;
        font-weight: 500;
        color: #6b7280;
    }
    
    /* Sidebar - clean and minimal */
    [data-testid="stSidebar"] {
        background: #fafafa;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2 {
        color: #1e293b;
        font-weight: 600;
        font-size: 1rem;
    }
    
    /* Button styling - subtle */
    .stButton button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s ease;
        font-size: 0.875rem;
    }
    
    .stButton button:hover {
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: white;
        border-radius: 6px;
        font-weight: 500;
        font-size: 0.9375rem;
        color: #1e293b;
    }
    
    /* Info box styling */
    .stAlert {
        border-radius: 6px;
        border: 1px solid #e5e7eb;
        box-shadow: none;
    }
    
    /* Plot styling - minimal */
    .js-plotly-plot {
        border-radius: 6px;
        box-shadow: none;
        border: 1px solid #e5e7eb;
    }
    
    /* Divider - subtle */
    hr {
        margin: 1.5rem 0;
        border: none;
        border-top: 1px solid #e5e7eb;
    }
    
    /* Tab styling - professional */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #f8fafc;
        padding: 4px;
        border-radius: 6px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 4px;
        padding: 10px 20px;
        font-weight: 500;
        font-size: 0.875rem;
        color: #64748b;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white;
        color: #1e293b;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }
    
    /* Headers - reduced sizing */
    h1 {
        font-size: 1.875rem !important;
        font-weight: 600 !important;
        color: #1e293b !important;
        letter-spacing: -0.02em !important;
    }
    
    h2 {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: #1e293b !important;
    }
    
    h3 {
        font-size: 1.125rem !important;
        font-weight: 600 !important;
        color: #475569 !important;
    }
    
    /* Markdown text */
    .markdown-text-container {
        font-size: 0.9375rem;
    }
    
    /* Remove excessive spacing */
    .element-container {
        margin-bottom: 0.5rem;
    }
    
    /* Compact metrics */
    [data-testid="metric-container"] {
        background: white;
        padding: 1rem;
        border-radius: 6px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'world' not in st.session_state:
    st.session_state.world = None
if 'history' not in st.session_state:
    st.session_state.history = []
if 'running' not in st.session_state:
    st.session_state.running = False
if 'seed_input' not in st.session_state:
    st.session_state.seed_input = None

def initialize_simulation(params):
    """Initialize the simulation with given parameters."""
    world = World()
    
    # Set all parameters
    world.world_size = int(params['world_size'])
    world.base_rate = params['base_rate']
    world.premium_increment = params['premium_increment']
    world.min_installment = params['min_installment']
    world.max_installment = params['max_installment']
    world.min_periods = int(params['min_periods'])
    world.max_periods = int(params['max_periods'])
    world.no_of_periods = int(params['no_of_periods'])
    world.insolvency_risk = params['insolvency_risk']
    world.unpaid_fraction = params['unpaid_fraction']
    world.max_day = int(params['max_day'])
    world.p_day_response = params['p_day_response']
    world.premium_response = params['premium_response']
    world.peer_effect = params['peer_effect']
    world.reserve_ratio = params['reserve_ratio']
    world.compensation_ratio = params['compensation_ratio']
    world.randomness = params['randomness']
    world.renew_financing = params['renew_financing']
    world.incentive_system = params['incentive_system']
    world.adjust_compensation = params['adjust_compensation']
    world.fix_random_seed = params['fix_random_seed']
    
    # Handle random seed
    if params['fix_random_seed'] and st.session_state.seed_input:
        try:
            seed = int(st.session_state.seed_input)
            world.set_random_seed(seed)
        except ValueError:
            st.error("Invalid seed number. Using random seed.")
            world.set_random_seed()
    else:
        world.set_random_seed()
    
    # Setup simulation
    world.setup()
    
    return world

def run_step(world):
    """Run one simulation step."""
    if world is None:
        return False
    return world.step()

def run_multiple_steps(world, num_steps):
    """Run multiple simulation steps."""
    for _ in range(num_steps):
        if not run_step(world):
            return False
        # Collect state after each step
        state = world.get_state()
        st.session_state.history.append(state)
    return True

# Main title
st.title("🏦 Smart Credit Management System - Simulation")
st.markdown("**Replication of NetLogo CIES 9.1 Model**")

# ============================================================================
# SIDEBAR - Controls and Parameters
# ============================================================================
with st.sidebar:
    st.header("🎮 Simulation Controls")
    
    # Control buttons in sidebar
    if st.button("Setup", type="primary", use_container_width=True):
        st.session_state.running = False
        
        # Collect all parameters
        params = {
            'world_size': st.session_state.get('world_size', 1225.0),
            'base_rate': st.session_state.get('base_rate', 0.2),
            'premium_increment': st.session_state.get('premium_increment', 0.1),
            'min_installment': st.session_state.get('min_installment', 4200.0),
            'max_installment': st.session_state.get('max_installment', 5400.0),
            'min_periods': st.session_state.get('min_periods', 20.0),
            'max_periods': st.session_state.get('max_periods', 60.0),
            'no_of_periods': st.session_state.get('no_of_periods', 90.0),
            'insolvency_risk': st.session_state.get('insolvency_risk', 3.0),
            'unpaid_fraction': st.session_state.get('unpaid_fraction', 70.0),
            'max_day': st.session_state.get('max_day', 25.0),
            'p_day_response': st.session_state.get('p_day_response', 1.0),
            'premium_response': st.session_state.get('premium_response', 1.0),
            'peer_effect': st.session_state.get('peer_effect', 40.0),
            'reserve_ratio': st.session_state.get('reserve_ratio', 0.0),
            'compensation_ratio': st.session_state.get('compensation_ratio', 70.0),
            'randomness': st.session_state.get('randomness', 25.0),
            'renew_financing': st.session_state.get('renew_financing', True),
            'incentive_system': st.session_state.get('incentive_system', True),
            'adjust_compensation': st.session_state.get('adjust_compensation', True),
            'fix_random_seed': st.session_state.get('fix_random_seed', False),
        }
        
        st.session_state.world = initialize_simulation(params)
        st.session_state.history = []
        st.success("Simulation initialized!")
        st.rerun()
    
    if st.button("Go", use_container_width=True):
        if st.session_state.world is None:
            st.error("Please click 'Setup' first!")
        else:
            st.session_state.running = True
            if run_step(st.session_state.world):
                state = st.session_state.world.get_state()
                st.session_state.history.append(state)
                st.rerun()
            else:
                st.session_state.running = False
                st.warning("Simulation stopped (reached max periods)")
    
    if st.button("Stop", use_container_width=True):
        st.session_state.running = False
    
    if st.button("Step", use_container_width=True):
        if st.session_state.world is None:
            st.error("Please click 'Setup' first!")
        else:
            st.session_state.running = False
            if run_step(st.session_state.world):
                state = st.session_state.world.get_state()
                st.session_state.history.append(state)
                st.rerun()
            else:
                st.warning("Simulation stopped (reached max periods)")
    
    if st.button("Run 10 Steps", use_container_width=True):
        if st.session_state.world is None:
            st.error("Please click 'Setup' first!")
        else:
            st.session_state.running = False
            with st.spinner("Running 10 steps..."):
                if run_multiple_steps(st.session_state.world, 10):
                    st.success("Completed 10 steps!")
                else:
                    st.warning("Simulation stopped (reached max periods)")
            st.rerun()
    
    if st.button("Run 50 Steps", use_container_width=True):
        if st.session_state.world is None:
            st.error("Please click 'Setup' first!")
        else:
            st.session_state.running = False
            with st.spinner("Running 50 steps..."):
                if run_multiple_steps(st.session_state.world, 50):
                    st.success("Completed 50 steps!")
                else:
                    st.warning("Simulation stopped (reached max periods)")
            st.rerun()
    
    st.divider()
    
    # Parameters in sidebar - matching NetLogo interface order
    st.header("📊 Parameters")
    with st.expander("Basic Parameters", expanded=True):
        st.session_state.world_size = st.slider(
            "world-size",
            min_value=100,
            max_value=5000,
            value=int(st.session_state.get('world_size', 1225)),
            step=25,
            help="Number of customers in the simulation"
        )
        
        st.session_state.base_rate = st.slider(
            "base-rate (%)",
            min_value=0.0,
            max_value=0.5,
            value=st.session_state.get('base_rate', 0.2),
            step=0.01,
            format="%.2f",
            help="Base fee for contribution to mutual insurance fund"
        )
        
        st.session_state.premium_increment = st.slider(
            "premium-increment (%)",
            min_value=0.0,
            max_value=0.15,
            value=st.session_state.get('premium_increment', 0.1),
            step=0.05,
            format="%.2f",
            help="Amount to add to contribution for each extra day of payment delay"
        )
        
        st.session_state.max_day = st.slider(
            "max-day",
            min_value=5,
            max_value=30,
            value=int(st.session_state.get('max_day', 25)),
            step=1,
            help="First payment day considered unacceptably late"
        )
    
    with st.expander("💰 Loan Parameters"):
        st.session_state.min_installment = st.slider(
            "min-installment ($)",
            min_value=0,
            max_value=10000,
            value=int(st.session_state.get('min_installment', 4200)),
            step=100,
            help="Lower bound on installment amounts"
        )
        
        st.session_state.max_installment = st.slider(
            "max-installment ($)",
            min_value=500,
            max_value=10000,
            value=int(st.session_state.get('max_installment', 5400)),
            step=100,
            help="Upper bound on installment amounts"
        )
        
        st.session_state.min_periods = st.slider(
            "min-periods",
            min_value=12,
            max_value=60,
            value=int(st.session_state.get('min_periods', 20)),
            step=1,
            help="Lower bound on number of repayment periods"
        )
        
        st.session_state.max_periods = st.slider(
            "max-periods",
            min_value=12,
            max_value=90,
            value=int(st.session_state.get('max_periods', 60)),
            step=1,
            help="Upper bound on number of repayment periods"
        )
        
        st.session_state.no_of_periods = st.slider(
            "No-of-periods",
            min_value=0,
            max_value=1000,
            value=int(st.session_state.get('no_of_periods', 90)),
            step=10,
            help="Number of periods after which to stop if renew-financing is true"
        )
    
    with st.expander("Risk Parameters"):
        st.session_state.insolvency_risk = st.slider(
            "insolvency-risk (%)",
            min_value=0.0,
            max_value=25.0,
            value=st.session_state.get('insolvency_risk', 3.0),
            step=0.5,
            format="%.1f",
            help="Probability of customer being able to repay any given installment in full"
        )
        
        st.session_state.unpaid_fraction = st.slider(
            "unpaid-fraction (%)",
            min_value=50,
            max_value=100,
            value=int(st.session_state.get('unpaid_fraction', 70)),
            step=1,
            help="Average fraction of installment which will go as unpaid deficit"
        )
    
    with st.expander("Incentive Parameters"):
        st.session_state.peer_effect = st.slider(
            "peer-effect (%)",
            min_value=0,
            max_value=100,
            value=int(st.session_state.get('peer_effect', 40)),
            step=1,
            help="Weighting factor for peer pressure effect"
        )
        
        st.session_state.p_day_response = st.slider(
            "p-day-response",
            min_value=0.5,
            max_value=1.5,
            value=st.session_state.get('p_day_response', 1.0),
            step=0.1,
            format="%.1f",
            help="Weighting factor for adherence to original preferred payment day"
        )
        
        st.session_state.premium_response = st.slider(
            "premium-response",
            min_value=0.5,
            max_value=1.5,
            value=st.session_state.get('premium_response', 1.0),
            step=0.1,
            format="%.1f",
            help="Weighting factor for aversion to paying increased premium"
        )
        
        st.session_state.randomness = st.slider(
            "randomness (%)",
            min_value=5,
            max_value=95,
            value=int(st.session_state.get('randomness', 25)),
            step=1,
            help="Percentage used to determine bounds of random distribution"
        )
    
    with st.expander("Fund Parameters"):
        st.session_state.reserve_ratio = st.slider(
            "reserve-ratio (%)",
            min_value=0,
            max_value=100,
            value=int(st.session_state.get('reserve_ratio', 0)),
            step=1,
            help="Percentage of fund assets to set aside before compensation"
        )
        
        st.session_state.compensation_ratio = st.slider(
            "compensation-ratio (%)",
            min_value=0,
            max_value=100,
            value=int(st.session_state.get('compensation_ratio', 70)),
            step=5,
            help="Percentage threshold for compensation calculation"
        )
    
    with st.expander("Options & Switches"):
        st.session_state.adjust_compensation = st.toggle(
            "adjust-compensation",
            value=st.session_state.get('adjust_compensation', True),
            help="If true, pay accumulated deficits when fund net assets exceed total deficits"
        )
        
        st.session_state.fix_random_seed = st.toggle(
            "fix-random-seed",
            value=st.session_state.get('fix_random_seed', False),
            help="If true, use a fixed random seed for reproducible runs"
        )
        
        if st.session_state.fix_random_seed:
            seed_input = st.text_input(
                "Seed number",
                value=str(st.session_state.get('seed_input', '')),
                help="Enter a seed number for reproducible runs"
            )
            st.session_state.seed_input = seed_input
        
        st.session_state.renew_financing = st.toggle(
            "renew-financing",
            value=st.session_state.get('renew_financing', True),
            help="If true, renew customers with new loans when they pay off their debt"
        )
        
        st.session_state.incentive_system = st.toggle(
            "incentive-system",
            value=st.session_state.get('incentive_system', True),
            help="Enable/disable rating and incentive system"
        )

# ============================================================================
# MAIN CONTENT AREA
# ============================================================================
if st.session_state.world is None:
    st.info("👈 Click 'Setup' in the sidebar to initialize the simulation.")
else:
    world = st.session_state.world
    state = world.get_state()
    
    # Auto-run if running flag is set
    if st.session_state.running:
        if run_step(world):
            state = world.get_state()
            st.session_state.history.append(state)
            st.rerun()
        else:
            st.session_state.running = False
            st.warning("Simulation stopped (reached max periods)")
    
    # ========================================================================
    # METRICS DASHBOARD
    # ========================================================================
    
    st.markdown("""
        <div class="dashboard-section">
            <h2>Key Metrics</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Key Overview Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Current Month",
            value=state['month'],
            help="Current simulation month"
        )
    
    with col2:
        st.metric(
            label="Total Customers",
            value=f"{state['customers']['total']:,}",
            delta=f"{state['customers']['active']:,} active",
            help="Total customers in the system"
        )
    
    with col3:
        st.metric(
            label="Financing Rounds",
            value=state['metrics']['rounds'],
            help="Number of financing rounds completed"
        )
    
    with col4:
        st.metric(
            label="Random Seed",
            value=state['seed_number'],
            help="Random seed for reproducibility"
        )
    
    st.markdown("---")
    
    # Credit Ratings Section
    st.markdown("""
        <div class="dashboard-section">
            <h2>Credit Ratings Distribution</h2>
        </div>
    """, unsafe_allow_html=True)
    
    rating_col1, rating_col2, rating_col3, rating_col4 = st.columns(4)
    
    with rating_col1:
        total_active = state['customers']['active']
        a_percentage = (state['customers']['a_rated'] / total_active * 100) if total_active > 0 else 0
        st.markdown(f"""
            <div class="rating-badge rating-badge-a">
                <span class="rating-value">{state['customers']['a_rated']:,}</span>
                <span class="rating-label">Grade A ({a_percentage:.1f}%)</span><br>
                <span class="rating-label">Days 1-10</span>
            </div>
        """, unsafe_allow_html=True)
    
    with rating_col2:
        b_percentage = (state['customers']['b_rated'] / total_active * 100) if total_active > 0 else 0
        st.markdown(f"""
            <div class="rating-badge rating-badge-b">
                <span class="rating-value">{state['customers']['b_rated']:,}</span>
                <span class="rating-label">Grade B ({b_percentage:.1f}%)</span><br>
                <span class="rating-label">Days 11-19</span>
            </div>
        """, unsafe_allow_html=True)
    
    with rating_col3:
        c_percentage = (state['customers']['c_rated'] / total_active * 100) if total_active > 0 else 0
        st.markdown(f"""
            <div class="rating-badge rating-badge-c">
                <span class="rating-value">{state['customers']['c_rated']:,}</span>
                <span class="rating-label">Grade C ({c_percentage:.1f}%)</span><br>
                <span class="rating-label">Days 20+</span>
            </div>
        """, unsafe_allow_html=True)
    
    with rating_col4:
        st.metric(
            label="Insolvent",
            value=state['customers']['insolvent'],
            help="Customers experiencing insolvency"
        )
        st.metric(
            label="Expelled",
            value=state['customers']['expelled'],
            delta="Total expelled",
            help="Customers expelled from the system"
        )
    
    st.markdown("---")
    
    # Financial Overview - Bank, Debt, and Fund in tabs
    st.markdown("""
        <div class="dashboard-section">
            <h2>Financial Overview</h2>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["Bank Metrics", "Debt Analysis", "Fund Status", "Payment & Risk"])
    
    with tab1:
        st.markdown("#### Bank Performance (Per Capita)")
        bank_col1, bank_col2, bank_col3 = st.columns(3)
        
        with bank_col1:
            bank_assets_per_capita = state['bank']['assets'] / state['customers']['total'] if state['customers']['total'] > 0 else 0
            st.metric(
                label="Bank Assets",
                value=f"${bank_assets_per_capita:,.2f}",
                help="Total bank assets per customer"
            )
        
        with bank_col2:
            bank_cash_per_capita = state['bank']['cash'] / state['customers']['total'] if state['customers']['total'] > 0 else 0
            st.metric(
                label="Cash Position",
                value=f"${bank_cash_per_capita:,.2f}",
                help="Bank cash reserves per customer"
            )
        
        with bank_col3:
            bank_receivables_per_capita = state['bank']['receivables'] / state['customers']['total'] if state['customers']['total'] > 0 else 0
            st.metric(
                label="Receivables",
                value=f"${bank_receivables_per_capita:,.2f}",
                help="Outstanding receivables per customer"
            )
    
    with tab2:
        st.markdown("#### Debt Portfolio (Per Capita)")
        debt_col1, debt_col2, debt_col3 = st.columns(3)
        
        with debt_col1:
            performing_debt_per_capita = state['metrics']['performing_debt'] / state['customers']['total'] if state['customers']['total'] > 0 else 0
            st.metric(
                label="Performing Debt",
                value=f"${performing_debt_per_capita:,.2f}",
                help="Debt being paid on time per customer"
            )
        
        with debt_col2:
            non_performing_debt_per_capita = state['metrics']['non_performing_debt'] / state['customers']['total'] if state['customers']['total'] > 0 else 0
            st.metric(
                label="Non-Performing Debt",
                value=f"${non_performing_debt_per_capita:,.2f}",
                help="Defaulted debt per customer"
            )
        
        with debt_col3:
            total_debt = performing_debt_per_capita + non_performing_debt_per_capita
            npl_ratio = (non_performing_debt_per_capita / total_debt * 100) if total_debt > 0 else 0
            st.metric(
                label="NPL Ratio",
                value=f"{npl_ratio:.2f}%",
                help="Non-performing loan ratio"
            )
    
    with tab3:
        st.markdown("#### Insurance Fund (Per Capita)")
        fund_col1, fund_col2, fund_col3 = st.columns(3)
        
        with fund_col1:
            fund_assets_per_capita = state['fund']['assets'] / state['customers']['total'] if state['customers']['total'] > 0 else 0
            st.metric(
                label="Total Assets",
                value=f"${fund_assets_per_capita:,.2f}",
                help="Total fund assets per customer"
            )
        
        with fund_col2:
            fund_net_assets_per_capita = state['fund']['net_assets'] / state['customers']['total'] if state['customers']['total'] > 0 else 0
            st.metric(
                label="Net Assets",
                value=f"${fund_net_assets_per_capita:,.2f}",
                help="Available fund assets per customer"
            )
        
        with fund_col3:
            reserves_per_capita = (world.reserve_ratio / 100.0) * state['fund']['assets'] / state['customers']['total'] if state['customers']['total'] > 0 else 0
            st.metric(
                label="Reserves",
                value=f"${reserves_per_capita:,.2f}",
                help="Reserved fund assets per customer"
            )
    
    with tab4:
        st.markdown("#### Payment Behavior & Risk Indicators")
        
        pay_col1, pay_col2, pay_col3 = st.columns(3)
        
        with pay_col1:
            st.metric(
                label="Avg Payment Day",
                value=f"{state['metrics']['avg_payment_day']:.1f}",
                help="Mean payment day across all customers"
            )
            st.metric(
                label="Max Payment Day",
                value=state['metrics']['max_day'],
                help="Latest payment day recorded"
            )
        
        with pay_col2:
            st.metric(
                label="Avg Contribution",
                value=f"{state['metrics']['avg_contribution_pct']:.2f}%",
                help="Mean contribution percentage"
            )
            st.metric(
                label="Avg Points",
                value=f"{state['metrics']['avg_points']:.1f}",
                help="Mean customer rating points"
            )
        
        with pay_col3:
            st.metric(
                label="Zero Risk Period",
                value=state['metrics']['zero_risk_period'],
                help="Months until non-performing debt reaches zero"
            )
            # Calculate mean balance from customers
            balances = []
            for c in world.customers:
                if c.patch_month <= c.duration and c.membership == 1:
                    balance = c.installment - c.paid_installment - c.deficit
                    balances.append(balance)
            mean_balance = sum(balances) / len(balances) if balances else 0
            st.metric(
                label="Balance Check",
                value=f"{mean_balance:.6f}",
                help="Mean balance (consistency check)"
            )
    
    st.markdown("---")
    
    # ========================================================================
    # VISUALIZATIONS & CHARTS
    # ========================================================================
    st.markdown("""
        <div class="dashboard-section">
            <h2>Data Visualizations</h2>
        </div>
    """, unsafe_allow_html=True)
    
    if len(st.session_state.history) > 0:
        # Prepare data for plots
        history_df = pd.DataFrame(st.session_state.history)
        
        # Create two columns for charts
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.markdown("#### Compensation Analysis")
            with st.expander("ℹ️ How to Interpret Compensation Analysis", expanded=False):
                st.markdown("""
                **The Compensation Analysis** chart tracks three key metrics over time: **Deficit** (red line) shows the average unpaid amount 
                per customer when insolvency shocks occur, **Compensation** (blue filled area) represents the average compensation received 
                from the mutual insurance fund to cover these deficits, and **Additional Compensation** (orange line) indicates catch-up 
                payments for past accumulated deficits when the fund has surplus capacity. Compare compensation to deficit to assess fund 
                coverage adequacy—when compensation closely matches deficit, the fund is effectively protecting customers; declining 
                compensation relative to deficit indicates fund depletion and potential system stress.
                """)
            mean_comp = [h['metrics']['mean_compensation_received'] for h in st.session_state.history]
            mean_deficit = [h['metrics']['mean_deficit'] for h in st.session_state.history]
            mean_add_comp = [h['metrics']['mean_additional_compensation'] for h in st.session_state.history]
            
            fig_comp = go.Figure()
            fig_comp.add_trace(go.Scatter(
                x=list(range(len(mean_comp))),
                y=mean_comp,
                mode='lines',
                name='Compensation',
                line=dict(color='#3b82f6', width=2),
                fill='tonexty'
            ))
            fig_comp.add_trace(go.Scatter(
                x=list(range(len(mean_deficit))),
                y=mean_deficit,
                mode='lines',
                name='Deficit',
                line=dict(color='#ef4444', width=3)
            ))
            fig_comp.add_trace(go.Scatter(
                x=list(range(len(mean_add_comp))),
                y=mean_add_comp,
                mode='lines',
                name='Additional Comp',
                line=dict(color='#f59e0b', width=3)
            ))
            fig_comp.update_layout(
                height=350,
                xaxis_title="Month",
                yaxis_title="Amount",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12)
            )
            fig_comp.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e5e7eb')
            fig_comp.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e5e7eb')
            st.plotly_chart(fig_comp, use_container_width=True)
        
        with chart_col2:
            st.markdown("#### Fund Performance (Per Capita)")
            with st.expander("ℹ️ How to Interpret Fund Performance", expanded=False):
                st.markdown("""
                **The Fund Performance chart** displays per-capita metrics showing the mutual insurance fund's financial health over time. 
                **Total Assets** (green) represents all fund contributions collected, **Net Assets** (blue) shows available funds after 
                reserves are set aside, **NPLs** (red) indicates non-performing loans per customer, and **Reserves** (orange) displays 
                the reserve amount per customer. Use this chart to monitor fund sustainability—rising net assets indicate healthy fund 
                growth, while increasing NPLs relative to net assets signal potential fund stress. The gap between total and net assets 
                shows the impact of reserve requirements on fund liquidity.
                """)
            fund_assets_pc = [h['fund']['assets'] / h['customers']['total'] for h in st.session_state.history]
            fund_net_assets_pc = [h['fund']['net_assets'] / h['customers']['total'] for h in st.session_state.history]
            npls_pc = [h['metrics']['non_performing_debt'] / h['customers']['total'] for h in st.session_state.history]
            reserves_pc = [(world.reserve_ratio / 100.0) * h['fund']['assets'] / h['customers']['total'] for h in st.session_state.history]
            
            fig_fund = go.Figure()
            fig_fund.add_trace(go.Scatter(
                x=list(range(len(fund_assets_pc))),
                y=fund_assets_pc,
                mode='lines',
                name='Total Assets',
                line=dict(color='#10b981', width=2)
            ))
            fig_fund.add_trace(go.Scatter(
                x=list(range(len(fund_net_assets_pc))),
                y=fund_net_assets_pc,
                mode='lines',
                name='Net Assets',
                line=dict(color='#3b82f6', width=3)
            ))
            fig_fund.add_trace(go.Scatter(
                x=list(range(len(npls_pc))),
                y=npls_pc,
                mode='lines',
                name='NPLs',
                line=dict(color='#ef4444', width=3)
            ))
            fig_fund.add_trace(go.Scatter(
                x=list(range(len(reserves_pc))),
                y=reserves_pc,
                mode='lines',
                name='Reserves',
                line=dict(color='#f59e0b', width=3)
            ))
            fig_fund.update_layout(
                height=350,
                xaxis_title="Month",
                yaxis_title="Amount (per capita)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12)
            )
            fig_fund.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e5e7eb')
            fig_fund.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e5e7eb')
            st.plotly_chart(fig_fund, use_container_width=True)
        
        # Rating evolution over time
        st.markdown("#### Credit Rating Evolution Over Time")
        with st.expander("ℹ️ How to Interpret Credit Rating Evolution", expanded=False):
            st.markdown("""
            **The Credit Rating Evolution chart** shows how the distribution of customer credit ratings changes over time using a stacked 
            area chart. **A-rated customers** (green, payment days 1-10) represent the healthiest segment, **B-rated** (orange, days 11-19) 
            indicate moderate risk, and **C-rated** (red, days 20+) show high-risk customers. The total height shows the total number of 
            active customers, while the proportion of each color indicates portfolio quality. Use this visualization to track portfolio 
            health trends—increasing green area indicates improving payment behavior, while expanding red area signals deteriorating 
            portfolio quality. Sudden shifts in the distribution may indicate the effectiveness of incentive systems or peer effects.
            """)
        a_rated = [h['customers']['a_rated'] for h in st.session_state.history]
        b_rated = [h['customers']['b_rated'] for h in st.session_state.history]
        c_rated = [h['customers']['c_rated'] for h in st.session_state.history]
        
        fig_rating = go.Figure()
        fig_rating.add_trace(go.Scatter(
            x=list(range(len(a_rated))),
            y=a_rated,
            mode='lines',
            name='A-Rated',
            line=dict(color='#10b981', width=3),
            stackgroup='one'
        ))
        fig_rating.add_trace(go.Scatter(
            x=list(range(len(b_rated))),
            y=b_rated,
            mode='lines',
            name='B-Rated',
            line=dict(color='#f59e0b', width=3),
            stackgroup='one'
        ))
        fig_rating.add_trace(go.Scatter(
            x=list(range(len(c_rated))),
            y=c_rated,
            mode='lines',
            name='C-Rated',
            line=dict(color='#ef4444', width=3),
            stackgroup='one'
        ))
        fig_rating.update_layout(
            height=350,
            xaxis_title="Month",
            yaxis_title="Number of Customers",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12)
        )
        fig_rating.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e5e7eb')
        fig_rating.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e5e7eb')
        st.plotly_chart(fig_rating, use_container_width=True)
    else:
        st.info("📊 Run the simulation to see historical charts and trends.")
    
    st.markdown("---")
    
    # Customer grid visualization
    st.markdown("""
        <div class="dashboard-section">
            <h2>Customer Grid Visualization</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Help information for Customer Grid Visualization
    with st.expander("ℹ️ How to Interpret the Customer Grid", expanded=False):
        st.markdown("""
        **The Customer Grid Visualization** displays customers in a spatial grid layout where each point represents an individual customer, 
        with colors indicating credit status: **green** for A-rated customers (payment days 1-10), **orange** for B-rated (days 11-19), 
        **red** for C-rated or insolvent (days 20+), and **gray** for expelled customers. 
        Hover over any point to view detailed information including payment day, rating, debt, and membership status. 
        Use this visualization to assess portfolio health through color distribution, identify spatial risk clusters where 
        similar-rated customers group together, and evaluate peer effects on payment behavior patterns.
        """)
    
    if world.customers:
        # Create grid visualization
        grid_size = world.grid_size
        grid_data = []
        
        for customer in world.customers[:grid_size * grid_size]:  # Limit to grid size
            color = 'gray'  # Expelled
            if customer.membership == 1:
                if customer.shock == 1:
                    color = 'red'  # Insolvent
                elif 1 <= customer.day < 11:
                    color = 'green'  # A-rated
                elif 11 <= customer.day < 20:
                    color = 'orange'  # B-rated
                else:
                    color = 'red'  # C-rated
            
            grid_data.append({
                'x': customer.x,
                'y': customer.y,
                'color': color,
                'day': customer.day,
                'rating': customer.get_rating(),
                'debt': customer.debt,
                'membership': customer.membership
            })
        
        if grid_data:
            grid_df = pd.DataFrame(grid_data)
            
            fig_grid = px.scatter(
                grid_df,
                x='x',
                y='y',
                color='color',
                color_discrete_map={
                    'green': 'green',
                    'orange': 'orange',
                    'red': 'red',
                    'gray': 'gray'
                },
                hover_data=['day', 'rating', 'debt', 'membership'],
                title="Customer Grid (Green=A-rated, Orange=B-rated, Red=C-rated/Insolvent, Gray=Expelled)"
            )
            fig_grid.update_layout(
                height=500,
                xaxis_title="X Position",
                yaxis_title="Y Position",
                showlegend=False
            )
            st.plotly_chart(fig_grid, use_container_width=True)
    
    st.markdown("---")
    
    # ========================================================================
    # SENSITIVITY ANALYSIS / DATA ANALYTICS
    # ========================================================================
    st.markdown("""
        <div class="dashboard-section">
            <h2>Sensitivity Analysis</h2>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("#### Peer Effect Sensitivity Analysis")
    st.markdown("Run simulations with different peer effect values to analyze their impact on key metrics.")
    
    # Sensitivity analysis controls
    sens_col1, sens_col2, sens_col3 = st.columns(3)
    
    with sens_col1:
        peer_effect_values = st.multiselect(
            "Peer Effect Values (%)",
            options=[0, 25, 40, 60, 80, 90, 100],
            default=[0, 25, 40, 60, 80, 90, 100],
            help="Select peer effect percentages to test"
        )
    
    with sens_col2:
        analysis_periods = st.number_input(
            "Simulation Periods",
            min_value=10,
            max_value=200,
            value=90,
            step=10,
            help="Number of periods to run for each peer effect value"
        )
    
    with sens_col3:
        use_current_params = st.checkbox(
            "Use Current Parameters",
            value=True,
            help="Use current parameter settings (except peer effect)"
        )
    
    if st.button("Run Sensitivity Analysis", type="primary", use_container_width=True):
        if not peer_effect_values:
            st.error("Please select at least one peer effect value.")
        else:
            with st.spinner("Running sensitivity analysis... This may take a few minutes."):
                results = []
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # First, capture initial state (baseline)
                status_text.text("Capturing initial state...")
                initial_world = World()
                if use_current_params:
                    initial_world.world_size = int(st.session_state.get('world_size', 1225))
                    initial_world.base_rate = st.session_state.get('base_rate', 0.2)
                    initial_world.premium_increment = st.session_state.get('premium_increment', 0.1)
                    initial_world.min_installment = st.session_state.get('min_installment', 4200.0)
                    initial_world.max_installment = st.session_state.get('max_installment', 5400.0)
                    initial_world.min_periods = int(st.session_state.get('min_periods', 20))
                    initial_world.max_periods = int(st.session_state.get('max_periods', 60))
                    initial_world.no_of_periods = int(analysis_periods)
                    initial_world.insolvency_risk = st.session_state.get('insolvency_risk', 3.0)
                    initial_world.unpaid_fraction = st.session_state.get('unpaid_fraction', 70.0)
                    initial_world.max_day = int(st.session_state.get('max_day', 25))
                    initial_world.p_day_response = st.session_state.get('p_day_response', 1.0)
                    initial_world.premium_response = st.session_state.get('premium_response', 1.0)
                    initial_world.reserve_ratio = st.session_state.get('reserve_ratio', 0.0)
                    initial_world.compensation_ratio = st.session_state.get('compensation_ratio', 70.0)
                    initial_world.randomness = st.session_state.get('randomness', 25.0)
                    initial_world.renew_financing = st.session_state.get('renew_financing', True)
                    initial_world.incentive_system = st.session_state.get('incentive_system', True)
                    initial_world.adjust_compensation = st.session_state.get('adjust_compensation', True)
                else:
                    initial_world.no_of_periods = int(analysis_periods)
                
                initial_world.peer_effect = st.session_state.get('peer_effect', 40.0)  # Use current or default
                initial_world.set_random_seed()
                initial_world.setup()
                
                # Get initial state
                initial_state = initial_world.get_state()
                initial_a = initial_state['customers']['a_rated']
                initial_b = initial_state['customers']['b_rated']
                initial_c = initial_state['customers']['c_rated']
                initial_total = initial_state['customers']['total']
                initial_zero_risk = initial_state['metrics']['zero_risk_period']
                initial_max_day = initial_state['metrics']['max_day']
                initial_payment_day = initial_state['metrics']['avg_payment_day']
                initial_contribution = initial_state['metrics']['avg_contribution_pct']
                initial_points = initial_state['metrics']['avg_points']
                
                # Add initial row
                results.append({
                    'Peer Effect (%)': 'Initial',
                    'A-rated': initial_a,
                    'B-rated': initial_b,
                    'C-rated': initial_c,
                    'Total Agents': initial_total,
                    'Zero-Risk Period': initial_zero_risk if initial_zero_risk > 0 else 'NA',
                    'Max Day': initial_max_day,
                    'Payment Day': round(initial_payment_day, 2),
                    'Avg Contribution Rate (%)': round(initial_contribution, 3),
                    'Avg Points': round(initial_points, 2)
                })
                
                progress_bar.progress(1 / (len(peer_effect_values) + 1))
                
                # Now run simulations for each peer effect value
                for idx, peer_effect in enumerate(sorted(peer_effect_values)):
                    status_text.text(f"Running simulation with peer effect = {peer_effect}% ({idx+1}/{len(peer_effect_values)})")
                    
                    # Create a new world for this simulation
                    test_world = World()
                    
                    # Use current parameters or defaults
                    if use_current_params:
                        test_world.world_size = int(st.session_state.get('world_size', 1225))
                        test_world.base_rate = st.session_state.get('base_rate', 0.2)
                        test_world.premium_increment = st.session_state.get('premium_increment', 0.1)
                        test_world.min_installment = st.session_state.get('min_installment', 4200.0)
                        test_world.max_installment = st.session_state.get('max_installment', 5400.0)
                        test_world.min_periods = int(st.session_state.get('min_periods', 20))
                        test_world.max_periods = int(st.session_state.get('max_periods', 60))
                        test_world.no_of_periods = int(analysis_periods)
                        test_world.insolvency_risk = st.session_state.get('insolvency_risk', 3.0)
                        test_world.unpaid_fraction = st.session_state.get('unpaid_fraction', 70.0)
                        test_world.max_day = int(st.session_state.get('max_day', 25))
                        test_world.p_day_response = st.session_state.get('p_day_response', 1.0)
                        test_world.premium_response = st.session_state.get('premium_response', 1.0)
                        test_world.reserve_ratio = st.session_state.get('reserve_ratio', 0.0)
                        test_world.compensation_ratio = st.session_state.get('compensation_ratio', 70.0)
                        test_world.randomness = st.session_state.get('randomness', 25.0)
                        test_world.renew_financing = st.session_state.get('renew_financing', True)
                        test_world.incentive_system = st.session_state.get('incentive_system', True)
                        test_world.adjust_compensation = st.session_state.get('adjust_compensation', True)
                    else:
                        test_world.no_of_periods = int(analysis_periods)
                    
                    # Set the peer effect value
                    test_world.peer_effect = float(peer_effect)
                    
                    # Setup and run simulation
                    test_world.set_random_seed()  # Use random seed for each run
                    test_world.setup()
                    
                    # Run simulation for specified periods
                    for _ in range(analysis_periods):
                        if not test_world.step():
                            break
                    
                    # Get final state
                    final_state = test_world.get_state()
                    
                    # Calculate metrics
                    active_customers = final_state['customers']['active']
                    a_rated = final_state['customers']['a_rated']
                    b_rated = final_state['customers']['b_rated']
                    c_rated = final_state['customers']['c_rated']
                    total_agents = final_state['customers']['total']
                    zero_risk = final_state['metrics']['zero_risk_period']
                    max_day = final_state['metrics']['max_day']
                    avg_payment_day = final_state['metrics']['avg_payment_day']
                    avg_contribution = final_state['metrics']['avg_contribution_pct']
                    avg_points = final_state['metrics']['avg_points']
                    
                    # Store results
                    results.append({
                        'Peer Effect (%)': peer_effect,
                        'A-rated': a_rated,
                        'B-rated': b_rated,
                        'C-rated': c_rated,
                        'Total Agents': total_agents,
                        'Zero-Risk Period': zero_risk if zero_risk > 0 else 'NA',
                        'Max Day': max_day,
                        'Payment Day': round(avg_payment_day, 2),
                        'Avg Contribution Rate (%)': round(avg_contribution, 3),
                        'Avg Points': round(avg_points, 2)
                    })
                    
                    progress_bar.progress((idx + 2) / (len(peer_effect_values) + 1))
                
                status_text.empty()
                progress_bar.empty()
                
                # Store results in session state
                st.session_state.sensitivity_results = results
                
                st.success(f"Sensitivity analysis completed! Analyzed {len(peer_effect_values)} peer effect values.")
    
    # Display results table
    if 'sensitivity_results' in st.session_state and st.session_state.sensitivity_results:
        results_df = pd.DataFrame(st.session_state.sensitivity_results)
        
        st.markdown("#### Results Table")
        
        # Format the dataframe for better display
        display_df = results_df.copy()
        # Only add % to numeric peer effect values, not "Initial"
        display_df['Peer Effect (%)'] = display_df['Peer Effect (%)'].apply(
            lambda x: str(x) + '%' if isinstance(x, (int, float)) else str(x)
        )
        
        # Display table with styling
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Peer Effect (%)": st.column_config.TextColumn("Peer Effect", width="small"),
                "A-rated": st.column_config.NumberColumn("A-rated", format="%d"),
                "B-rated": st.column_config.NumberColumn("B-rated", format="%d"),
                "C-rated": st.column_config.NumberColumn("C-rated", format="%d"),
                "Total Agents": st.column_config.NumberColumn("Total Agents", format="%d"),
                "Zero-Risk Period": st.column_config.TextColumn("Zero-Risk Period"),
                "Max Day": st.column_config.NumberColumn("Max Day", format="%d"),
                "Payment Day": st.column_config.NumberColumn("Payment Day", format="%.2f"),
                "Avg Contribution Rate (%)": st.column_config.NumberColumn("Avg Contribution (%)", format="%.3f"),
                "Avg Points": st.column_config.NumberColumn("Avg Points", format="%.2f")
            }
        )
        
        # Download button for results
        csv_results = results_df.to_csv(index=False)
        st.download_button(
            label="Download Results (CSV)",
            data=csv_results,
            file_name=f"sensitivity_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        # Visualization of results
        st.markdown("#### Visualizations")
        
        viz_col1, viz_col2 = st.columns(2)
        
        with viz_col1:
            st.markdown("##### Rating Distribution by Peer Effect")
            with st.expander("ℹ️ How to Interpret Rating Distribution", expanded=False):
                st.markdown("""
                **This chart** shows how customer credit ratings change as peer effect percentage varies, using grouped bars for each peer 
                effect level. **A-rated** (green), **B-rated** (orange), and **C-rated** (red) bars show the number of customers in each 
                rating category. Use this visualization to understand the impact of peer pressure on portfolio quality—higher peer effect 
                typically leads to more uniform behavior, which can either improve ratings (if neighbors pay early) or worsen them (if 
                neighbors pay late). Compare the relative heights of colored bars across different peer effect percentages to identify 
                optimal peer effect settings that maximize A-rated customers and minimize C-rated customers.
                """)
            fig_ratings = go.Figure()
            # Format x-axis labels
            x_labels = results_df['Peer Effect (%)'].apply(
                lambda x: str(x) + '%' if isinstance(x, (int, float)) else str(x)
            )
            
            fig_ratings.add_trace(go.Bar(
                x=x_labels,
                y=results_df['A-rated'],
                name='A-rated',
                marker_color='#10b981'
            ))
            fig_ratings.add_trace(go.Bar(
                x=x_labels,
                y=results_df['B-rated'],
                name='B-rated',
                marker_color='#f59e0b'
            ))
            fig_ratings.add_trace(go.Bar(
                x=x_labels,
                y=results_df['C-rated'],
                name='C-rated',
                marker_color='#ef4444'
            ))
            fig_ratings.update_layout(
                barmode='group',
                height=350,
                xaxis_title="Peer Effect (%)",
                yaxis_title="Number of Customers",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=11)
            )
            fig_ratings.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e5e7eb')
            fig_ratings.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e5e7eb')
            st.plotly_chart(fig_ratings, use_container_width=True)
        
        with viz_col2:
            st.markdown("##### Payment Day & Contribution Rate")
            with st.expander("ℹ️ How to Interpret Payment Day & Contribution Rate", expanded=False):
                st.markdown("""
                **This dual-axis chart** displays two key metrics as peer effect varies: **Payment Day** (blue line, left axis) shows the 
                average payment day across all customers, while **Average Contribution Rate** (green line, right axis) shows the mean 
                contribution percentage to the mutual insurance fund. Lower payment days indicate better payment behavior, while higher 
                contribution rates reflect increased premiums for delayed payments. Use this chart to assess the relationship between 
                peer effects and customer behavior—observe how changes in peer effect influence both payment timing and contribution rates. 
                The correlation between these metrics helps evaluate the effectiveness of the incentive system in encouraging timely payments.
                """)
            fig_metrics = go.Figure()
            
            # Format x-axis labels
            x_labels = results_df['Peer Effect (%)'].apply(
                lambda x: str(x) + '%' if isinstance(x, (int, float)) else str(x)
            )
            
            # Create secondary y-axis
            fig_metrics.add_trace(go.Scatter(
                x=x_labels,
                y=results_df['Payment Day'],
                name='Payment Day',
                line=dict(color='#3b82f6', width=2),
                yaxis='y'
            ))
            
            fig_metrics.add_trace(go.Scatter(
                x=x_labels,
                y=results_df['Avg Contribution Rate (%)'],
                name='Avg Contribution Rate (%)',
                line=dict(color='#10b981', width=2),
                yaxis='y2'
            ))
            
            fig_metrics.update_layout(
                height=350,
                xaxis_title="Peer Effect (%)",
                yaxis=dict(
                    title="Payment Day",
                    side="left",
                    showgrid=True,
                    gridcolor='#e5e7eb'
                ),
                yaxis2=dict(
                    title="Avg Contribution Rate (%)",
                    side="right",
                    overlaying="y",
                    showgrid=False
                ),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=11)
            )
            st.plotly_chart(fig_metrics, use_container_width=True)
    
    st.markdown("---")
    
    # Data export
    st.markdown("""
        <div class="dashboard-section">
            <h2>Data Export</h2>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export Current State (JSON)"):
            json_str = json.dumps(state, indent=2, default=str)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name=f"simulation_state_month_{state['month']}.json",
                mime="application/json"
            )
    
    with col2:
        if len(st.session_state.history) > 0:
            history_df = pd.DataFrame(st.session_state.history)
            csv = history_df.to_csv(index=False)
            st.download_button(
                label="Download History (CSV)",
                data=csv,
                file_name=f"simulation_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
