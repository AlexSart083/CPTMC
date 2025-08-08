"""
Monte Carlo Investment Simulator - Main Application
Modified version with simplified tax analysis and enhanced charts
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
        
        # REMOVED: Advanced tax options section completely
        # The enhanced tax calculation is always enabled, no comparison scenarios
        simulator.use_enhanced_tax = True
    
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
            
            if reset_clicked:
                PortfolioManager.reset_allocations('accumulation')
            
            if balance_clicked:
                PortfolioManager.balance_allocations('accumulation')
            
            # Show allocation status
            total_allocation = PortfolioManager.get_total_allocation(accumulation_assets_data)
            allocation_valid = UIComponents.render_allocation_status(total_allocation, lang)
        
        with col2:
            # Allocation chart and summary for accumulation (same for both phases)
            UIComponents.render_allocation_chart(accumulation_assets_data, lang, 'accumulation')
            UIComponents.render_asset_summary(accumulation_assets_data, lang, 'accumulation')
            
            # Info about retirement phase using same portfolio
            st.info(f"🏖️ {get_text('retirement_portfolio', lang)}: {get_text('use_same_portfolio', lang)}")
        
        # Use same data for retirement
        retirement_assets_data = accumulation_assets_data
        
    else:
        # Separate portfolio configurations
        tab1, tab2 = st.tabs([
            f"📈 {get_text('accumulation_portfolio', lang)}", 
            f"🏖️ {get_text('retirement_portfolio', lang)}"
        ])
        
        with tab1:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Investment profile selector for accumulation
                selected_accumulation_profile = UIComponents.render_profile_selector(
                    config_manager.asset_profiles, lang, 'accumulation'
                )
                
                # Handle profile loading
                PortfolioManager.load_accumulation_profile(config_manager, selected_accumulation_profile)
                PortfolioManager.initialize_default_profiles(
                    config_manager, selected_accumulation_profile, 'Conservative'
                )
                
                # Asset editor for accumulation
                accumulation_assets_data = UIComponents.render_asset_editor(
                    st.session_state.current_accumulation_assets, lang, 'accumulation'
                )
                
                # Update session state with UI changes
                PortfolioManager.update_assets_from_ui(accumulation_assets_data, 'accumulation')
                
                # Allocation controls
                reset_clicked_acc, balance_clicked_acc = UIComponents.render_allocation_controls(lang, 'accumulation')
                
                if reset_clicked_acc:
                    PortfolioManager.reset_allocations('accumulation')
                
                if balance_clicked_acc:
                    PortfolioManager.balance_allocations('accumulation')
                
                # Show allocation status
                total_allocation_acc = PortfolioManager.get_total_allocation(accumulation_assets_data)
                allocation_valid_acc = UIComponents.render_allocation_status(total_allocation_acc, lang)
            
            with col2:
                # Allocation chart and summary for accumulation
                UIComponents.render_allocation_chart(accumulation_assets_data, lang, 'accumulation')
                UIComponents.render_asset_summary(accumulation_assets_data, lang, 'accumulation')
        
        with tab2:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Investment profile selector for retirement
                selected_retirement_profile = UIComponents.render_profile_selector(
                    config_manager.asset_profiles, lang, 'retirement'
                )
                
                # Handle profile loading
                PortfolioManager.load_retirement_profile(config_manager, selected_retirement_profile)
                
                # Asset editor for retirement
                retirement_assets_data = UIComponents.render_asset_editor(
                    st.session_state.current_retirement_assets, lang, 'retirement'
                )
                
                # Update session state with UI changes
                PortfolioManager.update_assets_from_ui(retirement_assets_data, 'retirement')
                
                # Allocation controls
                reset_clicked_ret, balance_clicked_ret = UIComponents.render_allocation_controls(lang, 'retirement')
                
                if reset_clicked_ret:
                    PortfolioManager.reset_allocations('retirement')
                
                if balance_clicked_ret:
                    PortfolioManager.balance_allocations('retirement')
                
                # Show allocation status
                total_allocation_ret = PortfolioManager.get_total_allocation(retirement_assets_data)
                allocation_valid_ret = UIComponents.render_allocation_status(total_allocation_ret, lang)
            
            with col2:
                # Allocation chart and summary for retirement
                UIComponents.render_allocation_chart(retirement_assets_data, lang, 'retirement')
                UIComponents.render_asset_summary(retirement_assets_data, lang, 'retirement')
    
    st.markdown("---")
    
    # Run simulation button and simplified simulation logic
    if UIComponents.render_run_simulation_button(lang):
        # Get the correct data based on portfolio configuration
        if use_same_portfolio:
            final_accumulation_data = accumulation_assets_data
            final_retirement_data = accumulation_assets_data  # Same as accumulation
        else:
            final_accumulation_data = accumulation_assets_data
            final_retirement_data = retirement_assets_data
        
        # Validate inputs
        is_valid, active_accumulation_assets, active_retirement_assets = PortfolioManager.validate_simulation_inputs(
            final_accumulation_data, final_retirement_data, lang
        )
        
        if is_valid:
            # Calculate total deposited
            total_deposited = ResultsDisplay.calculate_total_deposited(
                params['initial_amount'], 
                params['annual_contribution'], 
                params['years_to_retirement'],
                params['adjust_contribution_inflation'], 
                params['inflation']
            )
            
            # Setup progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Run simplified simulation (no tax comparison scenarios)
            with st.spinner(get_text('simulation_progress', lang)):
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
                    progress_bar, 
                    status_text, 
                    lang
                )
            
            # Display simplified results (no detailed tax statistics, no tax comparison)
            ResultsDisplay.show_results(
                results, 
                simulator,
                total_deposited, 
                params['n_simulations'], 
                params['years_to_retirement'], 
                params['years_retired'],
                params['capital_gains_tax_rate'],
                params['withdrawal'],
                params['inflation'],  # Added inflation parameter
                lang
            )
    
    # Footer
    UIComponents.render_footer(lang)


if __name__ == "__main__":
    main()
