"""
Monte Carlo Investment Simulator - Main Application
Updated with enhanced capital gains tax support
"""

import streamlit as st
from config_manager import ConfigManager
from simulation_engine import MonteCarloSimulator
from ui_components import UIComponents
from results_display import ResultsDisplay
from portfolio_manager import PortfolioManager
from translations import get_text


def main():
    """Main application function"""
    # Initialize session state
    PortfolioManager.initialize_session_state()
    
    lang = st.session_state.language
    
    # Page configuration
    st.set_page_config(
        page_title=get_text('page_title', lang),
        page_icon="🏗️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Language selector
    UIComponents.render_language_selector(lang)
    
    # Initialize components
    config_manager = ConfigManager()
    simulator = MonteCarloSimulator()
    
    # Main header
    st.title(get_text('main_title', lang))
    
    # Enhanced disclaimers section
    UIComponents.render_disclaimers(lang)
    
    # Add tax methodology explanation
    with st.expander("💰 Metodologia di Calcolo Tasse" if lang == 'it' else "💰 Tax Calculation Methodology"):
        if lang == 'it':
            st.markdown("""
            **🔍 Come vengono calcolate le tasse sui capital gains:**
            
            1. **Tracciamento Accurato**: Sistema avanzato che traccia ogni contributo con la sua base di costo
            2. **Calcolo Proporzionale**: I prelievi vengono allocati proporzionalmente tra tutti i lotti fiscali
            3. **Tassazione Realizzata**: Le tasse si applicano solo sui capital gains realizzati durante i prelievi
            4. **Simulazione Anno per Anno**: Ogni anno di pensione viene calcolato individualmente
            
            **📊 Vantaggi del sistema migliorato:**
            - ✅ Precisione fiscale quasi professionale
            - ✅ Analisi dettagliata della distribuzione del carico fiscale
            - ✅ Calcolo automatico dell'importo lordo necessario per i prelievi netti
            - ✅ Insights avanzati sull'efficienza fiscale del portafoglio
            """)
        else:
            st.markdown("""
            **🔍 How capital gains taxes are calculated:**
            
            1. **Accurate Tracking**: Advanced system that tracks each contribution with its cost basis
            2. **Proportional Calculation**: Withdrawals are allocated proportionally across all tax lots
            3. **Realized Taxation**: Taxes apply only on capital gains realized during withdrawals
            4. **Year-by-Year Simulation**: Each retirement year is calculated individually
            
            **📊 Advantages of the improved system:**
            - ✅ Near-professional tax precision
            - ✅ Detailed tax burden distribution analysis
            - ✅ Automatic calculation of gross amount needed for net withdrawals
            - ✅ Advanced insights on portfolio tax efficiency
            """)
    
    st.markdown("---")
    
    # Sidebar for parameters
    with st.sidebar:
        st.header(get_text('simulation_parameters', lang))
        
        # General parameters (now includes capital gains tax rate)
        params = UIComponents.render_general_parameters(lang)
        
        # Add advanced tax options
        with st.expander("⚙️ Opzioni Fiscali Avanzate" if lang == 'it' else "⚙️ Advanced Tax Options"):
            
            # Enable/disable enhanced tax calculation
            use_enhanced_tax = st.checkbox(
                "Usa Calcolo Fiscale Avanzato" if lang == 'it' else "Use Enhanced Tax Calculation",
                value=True,
                help="Attiva il sistema di calcolo fiscale dettagliato con tracciamento dei lotti" if lang == 'it'
                     else "Enable detailed tax calculation system with lot tracking"
            )
            
            # Update simulator setting
            simulator.use_enhanced_tax = use_enhanced_tax
            
            if use_enhanced_tax:
                st.success("✅ Sistema fiscale avanzato attivo" if lang == 'it' else "✅ Advanced tax system enabled")
                
                # Multiple tax scenarios comparison
                enable_tax_scenarios = st.checkbox(
                    "Confronta Scenari Fiscali" if lang == 'it' else "Compare Tax Scenarios",
                    value=False,
                    help="Confronta risultati con diverse aliquote fiscali" if lang == 'it'
                         else "Compare results with different tax rates"
                )
                
                if enable_tax_scenarios:
                    tax_rates_to_compare = st.multiselect(
                        "Aliquote da Confrontare (%)" if lang == 'it' else "Tax Rates to Compare (%)",
                        [0, 12.5, 20, 26, 30, 35],
                        default=[20, 26],
                        help="Seleziona diverse aliquote per il confronto" if lang == 'it'
                             else "Select different rates for comparison"
                    )
            else:
                st.info("ℹ️ Utilizzo del sistema fiscale semplificato" if lang == 'it' else "ℹ️ Using simplified tax system")
    
    # Main area - Portfolio Configuration
    st.subheader(get_text('portfolio_config', lang))
    
    # Toggle for using same portfolio for both phases
    use_same_portfolio = UIComponents.render_same_portfolio_toggle(lang)
    
    if use_same_portfolio:
        # Single portfolio configuration
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader(get_text('accumulation_portfolio', lang))
            
            # Investment profile selector for accumulation (which will be used for both)
            selected_accumulation_profile = UIComponents.render_profile_selector(
                config_manager.asset_profiles, lang, 'accumulation'
            )
            
            # Handle profile loading
            PortfolioManager.load_accumulation_profile(config_manager, selected_accumulation_profile)
            PortfolioManager.initialize_default_profiles(
                config_manager, selected_accumulation_profile, selected_accumulation_profile
            )
            
            # Asset editor for accumulation
            accumulation_assets_data = UIComponents.render_asset_editor(
                st.session_state.current_accumulation_assets, lang, 'accumulation'
            )
            
            # Update session state with UI changes
            PortfolioManager.update_assets_from_ui(accumulation_assets_data, 'accumulation')
            
            # Allocation controls
            reset_clicked, balance_clicked = UIComponents.render_allocation_controls(lang, 'accumulation')
