"""
Backward compatible fix for correlation integration
Modifica il tuo STRM.py esistente con queste correzioni
"""

import streamlit as st
from config_manager import ConfigManager
from simulation_engine import MonteCarloSimulator
from ui_components import UIComponents
from results_display import ResultsDisplay
from portfolio_manager import PortfolioManager
from translations import get_text

# Importa i nuovi componenti solo se disponibili
try:
    from enhanced_config_manager import EnhancedConfigManager
    from correlation_engine import CorrelatedMonteCarloSimulator
    from correlation_ui import CorrelationUIComponents
    CORRELATION_AVAILABLE = True
except ImportError:
    CORRELATION_AVAILABLE = False
    print("Correlation modules not available - running in legacy mode")

def main():
    """Main application function with backward compatibility"""
    # Initialize session state
    PortfolioManager.initialize_session_state()
    
    # Initialize correlation settings in session state (safe)
    if 'use_correlation' not in st.session_state:
        st.session_state.use_correlation = False  # Default to False for safety
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
    
    # Initialize components with backward compatibility
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
    
    # Choose simulator based on correlation setting and availability
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
    
    # Main header
    st.title(get_text('main_title', lang))
    
    # Enhanced disclaimers section
    UIComponents.render_disclaimers(lang)
    
    # NUOVO: Correlation methodology explanation (solo se disponibile)
    if CORRELATION_AVAILABLE and enhanced_features:
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
                """)
    
    st.markdown("---")
    
    # Sidebar for parameters
    with st.sidebar:
        st.header(get_text('simulation_parameters', lang))
        
        # General parameters (unchanged)
        params = UIComponents.render_general_parameters(lang)
        
        # NUOVO: Correlation settings section (solo se disponibile)
        if CORRELATION_AVAILABLE and enhanced_features:
            st.markdown("---")
            
            # Correlation toggle con check di sicurezza
            try:
                use_correlation = CorrelationUIComponents.render_correlation_toggle(lang)
                st.session_state.use_correlation = use_correlation
            except Exception as e:
                st.error(f"Correlation UI error: {str(e)}")
                use_correlation = False
                st.session_state.use_correlation = False
            
            if use_correlation:
                # Correlation scenario selector (simplified for sidebar)
                correlation_scenarios = ['normal_times', 'crisis_times', 'independent']
                scenario_names = {
                    'normal_times': 'Mercati Normali' if lang == 'it' else 'Normal Markets',
                    'crisis_times': 'Crisi Finanziaria' if lang == 'it' else 'Financial Crisis', 
                    'independent': 'Asset Indipendenti' if lang == 'it' else 'Independent Assets'
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
        else:
            # Show info about correlation not being available
            st.info("🔗 " + ("Funzionalità correlazione non disponibile" if lang == 'it' else "Correlation features not available"))
    
    # NUOVO: Advanced correlation settings (conditional display)
    if (CORRELATION_AVAILABLE and enhanced_features and 
        st.session_state.get('show_correlation_settings', False)):
        st.markdown("---")
        
        # Detailed correlation settings con error handling
        with st.expander("🔗 " + ("Impostazioni Correlazione Avanzate" if lang == 'it' else "Advanced Correlation Settings"), expanded=True):
            try:
                scenario, correlation_matrix = CorrelationUIComponents.render_correlation_settings(config_manager, lang)
                
                # If using correlation, set up the simulator
                if (st.session_state.use_correlation and 
                    isinstance(simulator, CorrelatedMonteCarloSimulator)):
                    # Get asset names for correlation matrix setup
                    all_asset_names = list(config_manager.asset_characteristics.keys())
                    simulator.set_correlation_matrix(all_asset_names, correlation_matrix)
                    
                    # Show correlation visualization
                    CorrelationUIComponents.render_correlation_visualization(
                        correlation_matrix, all_asset_names, lang
                    )
                    
                    # Show correlation impact analysis
                    CorrelationUIComponents.render_correlation_impact_analysis(lang)
                
            except Exception as e:
                st.error(f"Correlation settings error: {str(e)}")
                st.info("Using default correlation settings")
            
            # Button to hide correlation settings
            if st.button("❌ " + ("Chiudi Impostazioni" if lang == 'it' else "Close Settings")):
                st.session_state.show_correlation_settings = False
                st.rerun()
        
        st.markdown("---")
    
    # Main area - Portfolio Configuration (UNCHANGED from original)
    st.subheader(get_text('portfolio_config', lang))
    
    # [Il resto del codice rimane identico al tuo STRM.py originale]
    # ... tutto il codice di portfolio configuration ...
    
    # Run simulation button with enhanced logic
    if UIComponents.render_run_simulation_button(lang):
        # [Validation code unchanged]
        
        # Setup progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # NUOVO: Choose simulation method based on correlation setting
        with st.spinner(get_text('simulation_progress', lang)):
            if (CORRELATION_AVAILABLE and enhanced_features and 
                st.session_state.use_correlation and correlation_enabled and
                isinstance(simulator, CorrelatedMonteCarloSimulator)):
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
        
        # Display results with correlation info
        st.markdown("---")
        
        # NUOVO: Show simulation method used
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
        
        # Display results (UNCHANGED)
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
    
    # Footer (UNCHANGED)
    UIComponents.render_footer(lang)


if __name__ == "__main__":
    main()
