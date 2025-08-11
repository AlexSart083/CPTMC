"""
Monte Carlo Investment Simulator - Main Application with Correlation Support
Enhanced version with asset correlation capabilities
"""

import streamlit as st
from enhanced_config_manager import EnhancedConfigManager  # Updated import
from correlation_engine import CorrelatedMonteCarloSimulator  # New import
from correlation_ui import CorrelationUIComponents  # New import
from ui_components import UIComponents
from results_display import ResultsDisplay
from portfolio_manager import PortfolioManager
from translations import get_text


def main():
    """Main application function with correlation support"""
    # Initialize session state
    PortfolioManager.initialize_session_state()
    
    # Initialize correlation settings in session state
    if 'use_correlation' not in st.session_state:
        st.session_state.use_correlation = True
    if 'correlation_scenario' not in st.session_state:
        st.session_state.correlation_scenario = 'normal_times'
    
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
    
    # Initialize components with enhanced config manager
    config_manager = EnhancedConfigManager()
    
    # Choose simulator based on correlation setting
    if st.session_state.use_correlation:
        simulator = CorrelatedMonteCarloSimulator()
    else:
        # Fallback to original simulator
        from simulation_engine import MonteCarloSimulator
        simulator = MonteCarloSimulator()
    
    # Main header
    st.title(get_text('main_title', lang))
    
    # Enhanced disclaimers section
    UIComponents.render_disclaimers(lang)
    
    # NEW: Correlation methodology explanation
    with st.expander("🔗 Metodologia Correlazione Asset" if lang == 'it' else "🔗 Asset Correlation Methodology"):
        if lang == 'it':
            st.markdown("""
            **🔍 Come vengono gestite le correlazioni tra asset:**
            
            1. **Distribuzione Normale Multivariata**: Utilizziamo distribuzioni normali multivariate per generare rendimenti correlati
            2. **Matrice di Correlazione**: Ogni scenario ha una matrice di correlazione specifica che definisce le relazioni tra asset
            3. **Scenari Multipli**: Supportiamo diversi scenari (mercati normali, crisi, asset indipendenti)
            4. **Validazione Matematica**: Le matrici vengono validate per assicurare proprietà matematiche corrette
            
            **📊 Vantaggi del sistema con correlazione:**
            - ✅ Simulazioni più realistiche dei mercati finanziari
            - ✅ Migliore stima del rischio di portafoglio durante le crisi
            - ✅ Analisi dell'efficacia della diversificazione
            - ✅ Stress testing con scenari di alta correlazione
            
            **⚠️ Limitazioni:**
            - Le correlazioni sono assunte costanti nel tempo
            - I rendimenti seguono distribuzioni normali
            - Eventi estremi potrebbero non essere completamente catturati
            """)
        else:
            st.markdown("""
            **🔍 How asset correlations are managed:**
            
            1. **Multivariate Normal Distribution**: We use multivariate normal distributions to generate correlated returns
            2. **Correlation Matrix**: Each scenario has a specific correlation matrix defining asset relationships
            3. **Multiple Scenarios**: Support for different scenarios (normal markets, crises, independent assets)
            4. **Mathematical Validation**: Matrices are validated to ensure correct mathematical properties
            
            **📊 Advantages of correlation system:**
            - ✅ More realistic financial market simulations
            - ✅ Better portfolio risk estimation during crises
            - ✅ Analysis of diversification effectiveness
            - ✅ Stress testing with high correlation scenarios
            
            **⚠️ Limitations:**
            - Correlations are assumed constant over time
            - Returns follow normal distributions
            - Extreme events might not be fully captured
            """)
    
    st.markdown("---")
    
    # Sidebar for parameters
    with st.sidebar:
        st.header(get_text('simulation_parameters', lang))
        
        # General parameters
        params = UIComponents.render_general_parameters(lang)
        
        # NEW: Correlation settings section
        st.markdown("---")
        
        # Correlation toggle
        use_correlation = CorrelationUIComponents.render_correlation_toggle(lang)
        
        if use_correlation:
            # Correlation scenario selector (simplified for sidebar)
            correlation_scenarios = ['normal_times', 'crisis_times', 'independent', 'custom']
            scenario_names = {
                'normal_times': 'Mercati Normali' if lang == 'it' else 'Normal Markets',
                'crisis_times': 'Crisi Finanziaria' if lang == 'it' else 'Financial Crisis', 
                'independent': 'Asset Indipendenti' if lang == 'it' else 'Independent Assets',
                'custom': 'Personalizzata' if lang == 'it' else 'Custom'
            }
            
            selected_scenario = st.selectbox(
                "Scenario Correlazione:" if lang == 'it' else "Correlation Scenario:",
                correlation_scenarios,
                format_func=lambda x: scenario_names[x],
                index=0,
                key='correlation_scenario_sidebar'
            )
            
            st.session_state.correlation_scenario = selected_scenario
            
            # Link to detailed correlation settings
            if st.button("⚙️ " + ("Impostazioni Avanzate" if lang == 'it' else "Advanced Settings")):
                st.session_state.show_correlation_settings = True
    
    # NEW: Advanced correlation settings (conditional display)
    if st.session_state.get('show_correlation_settings', False):
        st.markdown("---")
        
        # Detailed correlation settings
        with st.expander("🔗 " + ("Impostazioni Correlazione Avanzate" if lang == 'it' else "Advanced Correlation Settings"), expanded=True):
            scenario, correlation_matrix = CorrelationUIComponents.render_correlation_settings(config_manager, lang)
            
            # If using correlation, set up the simulator
            if use_correlation and isinstance(simulator, CorrelatedMonteCarloSimulator):
                # Get asset names for correlation matrix setup
                all_asset_names = list(config_manager.asset_characteristics.keys())
                simulator.set_correlation_matrix(all_asset_names, correlation_matrix)
                
                # Show correlation visualization
                CorrelationUIComponents.render_correlation_visualization(
                    correlation_matrix, all_asset_names, lang
                )
                
                # Show correlation impact analysis
                CorrelationUIComponents.render_correlation_impact_analysis(lang)
            
            # Button to hide correlation settings
            if st.button("❌ " + ("Chiudi Impostazioni" if lang == 'it' else "Close Settings")):
                st.session_state.show_correlation_settings = False
                st.rerun()
        
        st.markdown("---")
    
    # Main area - Portfolio Configuration (unchanged)
    st.subheader(get_text('portfolio_config', lang))
    
    # Toggle for using same portfolio for both phases
    use_same_portfolio = UIComponents.render_same_portfolio_toggle(lang)
    
    if use_same_portfolio:
        # Single portfolio configuration
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader(get_text('accumulation_portfolio', lang))
            
            # Investment profile selector for accumulation
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
            # Allocation chart and summary for accumulation
            UIComponents.render_allocation_chart(accumulation_assets_data, lang, 'accumulation')
            UIComponents.render_asset_summary(accumulation_assets_data, lang, 'accumulation')
            
            # Info about retirement phase using same portfolio
            st.info(f"🏖️ {get_text('retirement_portfolio', lang)}: {get_text('use_same_portfolio', lang)}")
        
        # Use same data for retirement
        retirement_assets_data = accumulation_assets_data
        
    else:
        # Separate portfolio configurations (same as original code)
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
    
    # Run simulation button with enhanced logic
    if UIComponents.render_run_simulation_button(lang):
        # Get the correct data based on portfolio configuration
        if use_same_portfolio:
            final_accumulation_data = accumulation_assets_data
            final_retirement_data = accumulation_assets_data
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
            
            # NEW: Choose simulation method based on correlation setting
            with st.spinner(get_text('simulation_progress', lang)):
                if use_correlation and isinstance(simulator, CorrelatedMonteCarloSimulator):
                    # Enhanced simulation with correlation
                    results = simulator.run_simulation_with_correlation(
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
                else:
                    # Standard simulation without correlation
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
            
            # Display results with correlation info
            st.markdown("---")
            
            # NEW: Show simulation method used
            if use_correlation:
                scenario_name = scenario_names.get(st.session_state.correlation_scenario, st.session_state.correlation_scenario)
                st.success(f"✅ " + ("Simulazione completata con correlazione" if lang == 'it' else "Simulation completed with correlation") + f" ({scenario_name})")
            else:
                st.info("ℹ️ " + ("Simulazione completata senza correlazione (asset indipendenti)" if lang == 'it' else "Simulation completed without correlation (independent assets)"))
            
            # Display results (same as original)
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
                lang
            )
    
    # Footer
    UIComponents.render_footer(lang)


if __name__ == "__main__":
    main()
