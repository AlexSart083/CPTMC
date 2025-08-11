"""
Monte Carlo Investment Simulator - Main Application
Fixed version with proper error handling and portfolio management
"""

import streamlit as st
from config_manager import ConfigManager
from simulation_engine import MonteCarloSimulator
from ui_components import UIComponents
from results_display import ResultsDisplay
from portfolio_manager import PortfolioManager
from translations import get_text

# Import optional correlation modules if available
try:
    from enhanced_config_manager import EnhancedConfigManager
    from correlation_engine import CorrelatedMonteCarloSimulator
    from correlation_ui import CorrelationUIComponents
    CORRELATION_AVAILABLE = True
except ImportError:
    CORRELATION_AVAILABLE = False
    print("Correlation modules not available - running in legacy mode")

def main():
    """Main application function with proper error handling"""
    # Initialize session state
    PortfolioManager.initialize_session_state()
    
    # Initialize correlation settings in session state
    if 'use_correlation' not in st.session_state:
        st.session_state.use_correlation = False
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
    
    # Correlation methodology explanation (if available)
    if CORRELATION_AVAILABLE and enhanced_features:
        with st.expander("🔗 Metodologia Correlazione Asset" if lang == 'it' else "🔗 Asset Correlation Methodology"):
            if lang == 'it':
                st.markdown("""
                **🔍 Come vengono gestite le correlazioni tra asset:**
                
                1. **Distribuzione Normale Multivariata**: Utilizziamo distribuzioni normali multivariate per generare rendimenti correlati
                2. **Matrice di Correlazione**: Ogni scenario ha una matrice di correlazione specifica che definisce le relazioni tra asset
                3. **Scenari Multipli**: Supportiamo diversi scenari (mercati normali, crisi, asset indipendenti)
                4. **Validazione Matematica**: Le matrici vengono validate per assicurare proprietà matematiche corrette
                """)
            else:
                st.markdown("""
                **🔍 How asset correlations are managed:**
                
                1. **Multivariate Normal Distribution**: We use multivariate normal distributions to generate correlated returns
                2. **Correlation Matrix**: Each scenario has a specific correlation matrix defining asset relationships
                3. **Multiple Scenarios**: Support for different scenarios (normal markets, crises, independent assets)
                4. **Mathematical Validation**: Matrices are validated to ensure correct mathematical properties
                """)
    
    st.markdown("---")
    
    # Sidebar for parameters
    with st.sidebar:
        st.header(get_text('simulation_parameters', lang))
        
        # General parameters
        params = UIComponents.render_general_parameters(lang)
        
        # Initialize default profiles
        try:
            PortfolioManager.initialize_default_profiles(
                config_manager, 
                'Moderate',  # Default accumulation profile
                'Conservative'  # Default retirement profile
            )
        except Exception as e:
            st.error(f"Failed to initialize default profiles: {str(e)}")
        
        st.markdown("---")
        st.subheader(get_text('portfolio_config', lang))
        
        # Toggle for using same portfolio
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
    
    # Create two columns for portfolios
    if use_same_portfolio:
        # Single portfolio configuration
        st.subheader(get_text('accumulation_portfolio', lang))
        
        # Get current assets
        accumulation_assets = st.session_state.get('current_accumulation_assets', [])
        
        if accumulation_assets:
            # Asset editor
            updated_assets = UIComponents.render_asset_editor(
                accumulation_assets, lang, 'accumulation'
            )
            
            # Update session state with modified assets
            PortfolioManager.update_assets_from_ui(updated_assets, 'accumulation')
            
            # Allocation controls
            reset_clicked, balance_clicked = UIComponents.render_allocation_controls(lang, 'accumulation')
            
            if reset_clicked:
                PortfolioManager.reset_allocations('accumulation')
            
            if balance_clicked:
                PortfolioManager.balance_allocations('accumulation')
            
            # Show allocation status
            total_allocation = PortfolioManager.get_total_allocation(updated_assets)
            UIComponents.render_allocation_status(total_allocation, lang)
            
            # Show allocation chart
            UIComponents.render_allocation_chart(updated_assets, lang, 'accumulation')
            
            # Asset summary
            UIComponents.render_asset_summary(updated_assets, lang, 'accumulation')
        else:
            st.warning(get_text('select_profile', lang))
    
    else:
        # Separate portfolio configurations
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(get_text('accumulation_portfolio', lang))
            
            accumulation_assets = st.session_state.get('current_accumulation_assets', [])
            
            if accumulation_assets:
                updated_acc_assets = UIComponents.render_asset_editor(
                    accumulation_assets, lang, 'accumulation'
                )
                
                PortfolioManager.update_assets_from_ui(updated_acc_assets, 'accumulation')
                
                reset_acc, balance_acc = UIComponents.render_allocation_controls(lang, 'accumulation')
                
                if reset_acc:
                    PortfolioManager.reset_allocations('accumulation')
                
                if balance_acc:
                    PortfolioManager.balance_allocations('accumulation')
                
                total_acc_allocation = PortfolioManager.get_total_allocation(updated_acc_assets)
                UIComponents.render_allocation_status(total_acc_allocation, lang)
                
                UIComponents.render_allocation_chart(updated_acc_assets, lang, 'accumulation')
                UIComponents.render_asset_summary(updated_acc_assets, lang, 'accumulation')
            else:
                st.warning(get_text('select_profile', lang))
        
        with col2:
            st.subheader(get_text('retirement_portfolio', lang))
            
            retirement_assets = st.session_state.get('current_retirement_assets', [])
            
            if retirement_assets:
                updated_ret_assets = UIComponents.render_asset_editor(
                    retirement_assets, lang, 'retirement'
                )
                
                PortfolioManager.update_assets_from_ui(updated_ret_assets, 'retirement')
                
                reset_ret, balance_ret = UIComponents.render_allocation_controls(lang, 'retirement')
                
                if reset_ret:
                    PortfolioManager.reset_allocations('retirement')
                
                if balance_ret:
                    PortfolioManager.balance_allocations('retirement')
                
                total_ret_allocation = PortfolioManager.get_total_allocation(updated_ret_assets)
                UIComponents.render_allocation_status(total_ret_allocation, lang)
                
                UIComponents.render_allocation_chart(updated_ret_assets, lang, 'retirement')
                UIComponents.render_asset_summary(updated_ret_assets, lang, 'retirement')
            else:
                st.warning(get_text('select_profile', lang))
    
    st.markdown("---")
    
    # Run simulation button
    if UIComponents.render_run_simulation_button(lang):
        # Get current assets
        accumulation_assets = st.session_state.get('current_accumulation_assets', [])
        retirement_assets = st.session_state.get('current_retirement_assets', [])
        
        # Validate inputs
        is_valid, active_accumulation_assets, active_retirement_assets = (
            PortfolioManager.validate_simulation_inputs(
                accumulation_assets, retirement_assets, lang
            )
        )
        
        if is_valid:
            # Calculate total deposited
            total_deposited = ResultsDisplay.calculate_total_deposited(
                params['initial_amount'],
                params['annual_contribution'],
                params['years_to_retirement'],
                params['adjust_contribution_inflation'],
                params['inflation'] / 100
            )
            
            # Setup progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Run simulation
            with st.spinner(get_text('simulation_progress', lang)):
                try:
                    # Choose simulation method based on correlation setting
                    if (CORRELATION_AVAILABLE and enhanced_features and 
                        st.session_state.use_correlation and correlation_enabled and
                        hasattr(simulator, 'run_simulation_with_correlation')):
                        # Enhanced simulation with correlation
                        try:
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
                            simulation_method = "correlation"
                        except Exception as e:
                            st.warning(f"Correlation simulation failed: {str(e)}. Using standard simulation.")
                            # Fallback to standard simulation
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
                            simulation_method = "standard"
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
                        simulation_method = "standard"
                    
                    # Display results
                    st.markdown("---")
                    
                    # Show simulation method used
                    if simulation_method == "correlation":
                        scenario_names = {
                            'normal_times': 'Mercati Normali' if lang == 'it' else 'Normal Markets',
                            'crisis_times': 'Crisi Finanziaria' if lang == 'it' else 'Financial Crisis', 
                            'independent': 'Asset Indipendenti' if lang == 'it' else 'Independent Assets'
                        }
                        scenario_name = scenario_names.get(st.session_state.correlation_scenario, st.session_state.correlation_scenario)
                        st.success(f"✅ " + ("Simulazione completata con correlazione" if lang == 'it' else "Simulation completed with correlation") + f" ({scenario_name})")
                    else:
                        st.info("ℹ️ " + ("Simulazione completata senza correlazione (asset indipendenti)" if lang == 'it' else "Simulation completed without correlation (independent assets)"))
                    
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
                        lang
                    )
                    
                except Exception as e:
                    st.error(f"Simulation error: {str(e)}")
                    st.exception(e)
    
    # Footer
    UIComponents.render_footer(lang)


if __name__ == "__main__":
    main()
