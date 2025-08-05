"""
Monte Carlo Investment Simulator - Main Application
Refactored modular version with separate components
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
    
    # Disclaimers section
    UIComponents.render_disclaimers(lang)
    st.markdown("---")
    
    # Sidebar for parameters
    with st.sidebar:
        st.header(get_text('simulation_parameters', lang))
        
        # General parameters
        params = UIComponents.render_general_parameters(lang)
    
    # Main area divided into columns
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader(get_text('portfolio_config', lang))
        
        # Investment profile selector
        selected_profile = UIComponents.render_profile_selector(config_manager.asset_profiles, lang)
        
        # Handle profile loading
        PortfolioManager.load_profile(config_manager, selected_profile)
        PortfolioManager.initialize_default_profile(config_manager, selected_profile)
        
        # Asset editor
        assets_data = UIComponents.render_asset_editor(st.session_state.current_assets, lang)
        
        # Update session state with UI changes
        PortfolioManager.update_assets_from_ui(assets_data)
        
        # Allocation controls
        reset_clicked, balance_clicked = UIComponents.render_allocation_controls(lang)
        
        if reset_clicked:
            PortfolioManager.reset_allocations()
        
        if balance_clicked:
            PortfolioManager.balance_allocations()
        
        # Show allocation status
        total_allocation = PortfolioManager.get_total_allocation(assets_data)
        allocation_valid = UIComponents.render_allocation_status(total_allocation, lang)
    
    with col2:
        # Allocation chart
        UIComponents.render_allocation_chart(assets_data, lang)
        
        # Asset summary
        UIComponents.render_asset_summary(assets_data, lang)
    
    st.markdown("---")
    
    # Run simulation button and logic
    if UIComponents.render_run_simulation_button(lang):
        # Validate inputs
        is_valid, active_assets = PortfolioManager.validate_simulation_inputs(assets_data, lang)
        
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
            
            # Run simulation
            with st.spinner(get_text('simulation_progress', lang)):
                results = simulator.run_simulation(
                    active_assets, 
                    params['initial_amount'], 
                    params['years_to_retirement'], 
                    params['years_retired'],
                    params['annual_contribution'], 
                    params['adjust_contribution_inflation'], 
                    params['inflation'] / 100, 
                    params['withdrawal'], 
                    params['n_simulations'],
                    progress_bar, 
                    status_text, 
                    lang
                )
            
            # Display results
            ResultsDisplay.show_results(
                results, 
                total_deposited, 
                params['n_simulations'], 
                params['years_to_retirement'], 
                params['years_retired'], 
                lang
            )
    
    # Footer
    UIComponents.render_footer(lang)


if __name__ == "__main__":
    main()
