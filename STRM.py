"""
Monte Carlo Investment Simulator - Bootstrap Theme Version
Main Application with Bootstrap-style CSS
"""

import streamlit as st
from config_manager import ConfigManager
from simulation_engine import MonteCarloSimulator
from ui_components import UIComponents
from results_display import ResultsDisplay
from portfolio_manager import PortfolioManager
from translations import get_text  # Usa la versione professionale

# Import optional correlation modules if available
try:
    from enhanced_config_manager import EnhancedConfigManager
    from correlation_engine import CorrelatedMonteCarloSimulator
    from correlation_ui import CorrelationUIComponents
    CORRELATION_AVAILABLE = True
except ImportError:
    CORRELATION_AVAILABLE = False

def load_css():
    """Load professional Bootstrap-style CSS"""
    css = """
    <style>
    /* Professional Bootstrap-inspired Theme */
    :root {
        --primary-color: #0066cc;
        --secondary-color: #6c757d;
        --success-color: #28a745;
        --warning-color: #ffc107;
        --danger-color: #dc3545;
        --info-color: #17a2b8;
        --light-bg: #f8f9fa;
        --dark-text: #212529;
        --border-color: #dee2e6;
    }

    .main {
        background-color: white;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    }

    h1, h2, h3, h4 {
        font-weight: 600;
        color: var(--dark-text);
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }

    h1 {
        border-bottom: 3px solid var(--primary-color);
        padding-bottom: 0.5rem;
    }

    h2 {
        border-bottom: 2px solid var(--border-color);
        padding-bottom: 0.5rem;
    }

    .stButton button {
        border-radius: 4px;
        font-weight: 500;
        padding: 0.5rem 1.5rem;
        border: 1px solid transparent;
        transition: all 0.2s ease;
    }

    .stButton button[kind="primary"] {
        background-color: var(--primary-color);
        color: white;
    }

    .stButton button[kind="primary"]:hover {
        background-color: #0052a3;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .stMetric {
        background-color: var(--light-bg);
        padding: 1rem;
        border-radius: 4px;
        border: 1px solid var(--border-color);
    }

    .stMetric label {
        font-weight: 600;
        color: var(--secondary-color);
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .stMetric [data-testid="stMetricValue"] {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--primary-color);
    }

    .stAlert {
        border-radius: 4px;
        border-left: 4px solid;
    }

    .streamlit-expanderHeader {
        background-color: var(--light-bg);
        border-radius: 4px;
        font-weight: 600;
        border: 1px solid var(--border-color);
    }

    .streamlit-expanderHeader:hover {
        background-color: #e9ecef;
    }

    section[data-testid="stSidebar"] {
        background-color: var(--light-bg);
        border-right: 1px solid var(--border-color);
    }

    .stProgress > div > div {
        background-color: var(--primary-color);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: var(--light-bg);
        padding: 0.5rem;
        border-radius: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border: 1px solid var(--border-color);
        border-radius: 4px;
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color);
        color: white;
    }

    .footer {
        text-align: center;
        color: var(--secondary-color);
        font-size: 0.875rem;
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid var(--border-color);
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def main():
    """Main application function with professional theme"""
    # Initialize session state
    PortfolioManager.initialize_session_state()
    
    # Load professional CSS
    load_css()
    
    # Initialize correlation settings
    if 'use_correlation' not in st.session_state:
        st.session_state.use_correlation = False
    if 'correlation_scenario' not in st.session_state:
        st.session_state.correlation_scenario = 'normal_times'
    if 'show_correlation_settings' not in st.session_state:
        st.session_state.show_correlation_settings = False
    
    lang = st.session_state.language
    
    # Page configuration
    st.set_page_config(
        page_title=get_text('page_title', lang),
        page_icon="📊",  # Usa un'icona neutra invece di emoticon
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Language selector
    UIComponents.render_language_selector(lang)
    
    # Initialize config manager
    try:
        if CORRELATION_AVAILABLE:
            try:
                config_manager = EnhancedConfigManager()
                enhanced_features = True
            except Exception as e:
                st.warning(f"Enhanced config manager failed, using legacy: {str(e)}")
                config_manager = ConfigManager()
                enhanced_features = False
        else:
            config_manager = ConfigManager()
            enhanced_features = False
    except Exception as e:
        st.error(f"Failed to initialize config manager: {str(e)}")
        st.stop()
    
    # Initialize simulator
    try:
        if CORRELATION_AVAILABLE and enhanced_features and st.session_state.use_correlation:
            try:
                simulator = CorrelatedMonteCarloSimulator()
                correlation_enabled = True
            except Exception as e:
                st.warning(f"Correlation simulator failed, using standard: {str(e)}")
                simulator = MonteCarloSimulator()
                correlation_enabled = False
        else:
            simulator = MonteCarloSimulator()
            correlation_enabled = False
    except Exception as e:
        st.error(f"Failed to initialize simulator: {str(e)}")
        st.stop()
    
    # Main header
    st.title(get_text('main_title', lang))
    
    # Enhanced disclaimers section
    UIComponents.render_disclaimers(lang)
    
    # Feature announcements
    st.info("**" + ("Nuove Funzionalità" if lang == 'it' else "New Features") + "**: " + 
            ("Questa versione include prelievi REALI che mantengono il potere d'acquisto e analisi VaR/CVaR integrata!" 
             if lang == 'it' else 
             "This version includes REAL withdrawals that maintain purchasing power and integrated VaR/CVaR analysis!"))
    
    st.success("**" + ("Analisi del Rischio Integrata" if lang == 'it' else "Integrated Risk Analysis") + "**: " + 
              ("VaR e CVaR al 5% ora integrati direttamente nell'app per valutare i rischi estremi!" 
               if lang == 'it' else 
               "VaR and CVaR at 5% now integrated directly in the app to assess extreme risks!"))
    
    st.markdown("---")
    
    # Sidebar for parameters
    with st.sidebar:
        st.header(get_text('simulation_parameters', lang))
        
        # General parameters
        params = UIComponents.render_general_parameters(lang)
        
        # CORRELATION SETTINGS (if available)
        if CORRELATION_AVAILABLE and enhanced_features:
            st.markdown("---")
            st.subheader(("Correlazione Asset" if lang == 'it' else "Asset Correlation"))
            
            try:
                use_correlation = CorrelationUIComponents.render_correlation_toggle(lang)
                st.session_state.use_correlation = use_correlation
            except Exception as e:
                use_correlation = False
                st.session_state.use_correlation = False
            
            if use_correlation:
                correlation_scenarios = ['normal_times', 'crisis_times', 'independent', 'defensive', 'high_inflation']
                scenario_names = {
                    'normal_times': 'Mercati Normali' if lang == 'it' else 'Normal Markets',
                    'crisis_times': 'Crisi Finanziaria' if lang == 'it' else 'Financial Crisis', 
                    'independent': 'Asset Indipendenti' if lang == 'it' else 'Independent Assets',
                    'defensive': 'Scenario Difensivo' if lang == 'it' else 'Defensive Scenario',
                    'high_inflation': 'Alta Inflazione' if lang == 'it' else 'High Inflation'
                }
                
                selected_scenario = st.selectbox(
                    ("Scenario:" if lang == 'it' else "Scenario:"),
                    correlation_scenarios,
                    format_func=lambda x: scenario_names.get(x, x),
                    index=0,
                    key='correlation_scenario_sidebar'
                )
                
                st.session_state.correlation_scenario = selected_scenario
                
                if st.button(("Impostazioni Avanzate" if lang == 'it' else "Advanced Settings")):
                    st.session_state.show_correlation_settings = True
        
        # Initialize default profiles
        st.markdown("---")
        st.subheader(get_text('portfolio_config', lang))
        
        if not st.session_state.current_accumulation_assets:
            try:
                PortfolioManager.initialize_default_profiles(
                    config_manager, 
                    'Moderate',
                    'Conservative'
                )
            except Exception as e:
                st.error(f"Failed to initialize default profiles: {str(e)}")
        
        # Portfolio toggle
        use_same_portfolio = UIComponents.render_same_portfolio_toggle(lang)
        
        # Profile selectors
        st.markdown("---")
        accumulation_profile = UIComponents.render_profile_selector(
            config_manager.asset_profiles, lang, 'accumulation'
        )
        
        if st.button(get_text('load_profile', lang), key='load_acc_profile'):
            PortfolioManager.load_accumulation_profile(config_manager, accumulation_profile)
        
        if not use_same_portfolio:
            st.markdown("---")
            retirement_profile = UIComponents.render_profile_selector(
                config_manager.asset_profiles, lang, 'retirement'
            )
            
            if st.button(get_text('load_profile', lang), key='load_ret_profile'):
                PortfolioManager.load_retirement_profile(config_manager, retirement_profile)
    
    # Main area - Portfolio Configuration
    st.subheader(get_text('portfolio_config', lang))
    
    accumulation_assets = st.session_state.current_accumulation_assets
    retirement_assets = st.session_state.current_retirement_assets
    
    # Portfolio configuration UI
    if use_same_portfolio:
        st.subheader(get_text('accumulation_portfolio', lang))
        
        if accumulation_assets:
            updated_assets = UIComponents.render_asset_editor(
                accumulation_assets, lang, 'accumulation'
            )
            
            st.session_state.current_accumulation_assets = updated_assets
            
            if st.session_state.use_same_portfolio:
                st.session_state.current_retirement_assets = [asset.copy() for asset in updated_assets]
            
            reset_clicked, balance_clicked = UIComponents.render_allocation_controls(lang, 'accumulation')
            
            if reset_clicked:
                PortfolioManager.reset_allocations('accumulation')
            
            if balance_clicked:
                PortfolioManager.balance_allocations('accumulation')
            
            total_allocation = PortfolioManager.get_total_allocation(st.session_state.current_accumulation_assets)
            UIComponents.render_allocation_status(total_allocation, lang)
            
            UIComponents.render_allocation_chart(st.session_state.current_accumulation_assets, lang, 'accumulation')
            UIComponents.render_asset_summary(st.session_state.current_accumulation_assets, lang, 'accumulation')
        else:
            st.warning(get_text('select_profile', lang))
    
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(get_text('accumulation_portfolio', lang))
            
            if accumulation_assets:
                updated_acc_assets = UIComponents.render_asset_editor(
                    accumulation_assets, lang, 'accumulation'
                )
                
                st.session_state.current_accumulation_assets = updated_acc_assets
                
                reset_acc, balance_acc = UIComponents.render_allocation_controls(lang, 'accumulation')
                
                if reset_acc:
                    PortfolioManager.reset_allocations('accumulation')
                
                if balance_acc:
                    PortfolioManager.balance_allocations('accumulation')
                
                total_acc_allocation = PortfolioManager.get_total_allocation(st.session_state.current_accumulation_assets)
                UIComponents.render_allocation_status(total_acc_allocation, lang)
                
                UIComponents.render_allocation_chart(st.session_state.current_accumulation_assets, lang, 'accumulation')
                UIComponents.render_asset_summary(st.session_state.current_accumulation_assets, lang, 'accumulation')
            else:
                st.warning(get_text('select_profile', lang))
        
        with col2:
            st.subheader(get_text('retirement_portfolio', lang))
            
            if retirement_assets:
                updated_ret_assets = UIComponents.render_asset_editor(
                    retirement_assets, lang, 'retirement'
                )
                
                st.session_state.current_retirement_assets = updated_ret_assets
                
                reset_ret, balance_ret = UIComponents.render_allocation_controls(lang, 'retirement')
                
                if reset_ret:
                    PortfolioManager.reset_allocations('retirement')
                
                if balance_ret:
                    PortfolioManager.balance_allocations('retirement')
                
                total_ret_allocation = PortfolioManager.get_total_allocation(st.session_state.current_retirement_assets)
                UIComponents.render_allocation_status(total_ret_allocation, lang)
                
                UIComponents.render_allocation_chart(st.session_state.current_retirement_assets, lang, 'retirement')
                UIComponents.render_asset_summary(st.session_state.current_retirement_assets, lang, 'retirement')
            else:
                st.warning(get_text('select_profile', lang))
    
    st.markdown("---")
    
    # Run simulation button
    if UIComponents.render_run_simulation_button(lang):
        final_accumulation_assets = st.session_state.current_accumulation_assets
        final_retirement_assets = st.session_state.current_retirement_assets
        
        is_valid, active_accumulation_assets, active_retirement_assets = (
            PortfolioManager.validate_simulation_inputs(
                final_accumulation_assets, final_retirement_assets, lang
            )
        )
        
        if is_valid:
            total_deposited = ResultsDisplay.calculate_total_deposited(
                params['initial_amount'],
                params['annual_contribution'],
                params['years_to_retirement'],
                params['adjust_contribution_inflation'],
                params['inflation'] / 100
            )
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            with st.spinner(get_text('simulation_progress', lang)):
                try:
                    # Run simulation
                    results = simulator.run_simulation(
                        active_accumulation_assets,
                        active_retirement_assets,
                        params['initial_amount'], 
                        params['years_to_retirement'], 
                        params['years_retired'],
                        params['annual_contribution'], 
                        params['adjust_contribution_inflation'], 
                        params['inflation'] / 100, 
                        params['withdrawal'],
                        params['capital_gains_tax_rate'],
                        params['n_simulations'],
                        params['use_real_withdrawal'],
                        progress_bar, 
                        status_text, 
                        lang
                    )
                    
                    st.markdown("---")
                    
                    # Show completion messages
                    st.success(("Simulazione completata" if lang == 'it' else "Simulation completed"))
                    
                    if params['use_real_withdrawal']:
                        st.success(("Utilizzato prelievo REALE (aggiustato per inflazione)" if lang == 'it' else "Used REAL withdrawal (inflation-adjusted)"))
                    else:
                        st.info(("Utilizzato prelievo NOMINALE (importo fisso)" if lang == 'it' else "Used NOMINAL withdrawal (fixed amount)"))
                    
                    st.success(("Analisi VaR/CVaR integrata nei risultati" if lang == 'it' else "VaR/CVaR analysis integrated in results"))
                    
                    # Display results
                    ResultsDisplay.show_results(
                        results, 
                        simulator,
                        total_deposited, 
                        params['n_simulations'], 
                        params['years_to_retirement'], 
                        params['years_retired'],
                        params['capital_gains_tax_rate'],
                        params['withdrawal'],
                        params['inflation'],
                        params['use_real_withdrawal'],
                        lang
                    )
                    
                except Exception as e:
                    st.error(f"Simulation error: {str(e)}")
                    import traceback
                    st.text(traceback.format_exc())
    
    # Footer
    UIComponents.render_footer(lang)


if __name__ == "__main__":
    main()
