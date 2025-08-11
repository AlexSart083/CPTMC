"""
Safe UI Components for Correlation Management with backward compatibility
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from translations import get_text, get_asset_names


class CorrelationUIComponents:
    """UI components for managing asset correlations with safety checks"""
    
    @staticmethod
    def render_correlation_settings(config_manager, lang):
        """Render correlation settings section with backward compatibility"""
        st.subheader("🔗 " + ("Impostazioni Correlazione Asset" if lang == 'it' else "Asset Correlation Settings"))
        
        # Check if config_manager has correlation capabilities
        has_correlation_scenarios = hasattr(config_manager, 'correlation_scenarios') and config_manager.correlation_scenarios
        
        if not has_correlation_scenarios:
            st.warning("⚠️ " + ("Config manager non supporta correlazioni - usando fallback" if lang == 'it' else "Config manager doesn't support correlations - using fallback"))
            # Create fallback correlation matrix
            asset_names = list(config_manager.asset_characteristics.keys())
            correlation_matrix = np.eye(len(asset_names))  # Identity matrix as fallback
            return 'independent', correlation_matrix
        
        # Correlation scenario selector
        correlation_scenarios = ['normal_times', 'crisis_times', 'independent', 'custom']
        scenario_names = {
            'normal_times': 'Condizioni Normali' if lang == 'it' else 'Normal Times',
            'crisis_times': 'Crisi Finanziaria' if lang == 'it' else 'Financial Crisis',
            'independent': 'Asset Indipendenti' if lang == 'it' else 'Independent Assets',
            'custom': 'Personalizzata' if lang == 'it' else 'Custom'
        }
        
        selected_scenario = st.selectbox(
            "Scenario di Correlazione:" if lang == 'it' else "Correlation Scenario:",
            correlation_scenarios,
            format_func=lambda x: scenario_names[x],
            index=0,
            key='correlation_scenario'
        )
        
        # Load correlation matrix based on scenario
        try:
            if hasattr(config_manager, 'correlation_scenarios'):
                correlation_config = config_manager.correlation_scenarios.get(selected_scenario)
            else:
                correlation_config = None
        except Exception as e:
            st.error(f"Error accessing correlation scenarios: {str(e)}")
            correlation_config = None
        
        if selected_scenario == 'custom' or correlation_config is None:
            # Custom correlation matrix editor
            st.info("⚠️ " + ("Modalità personalizzata - modifica la matrice di correlazione manualmente" 
                           if lang == 'it' else "Custom mode - edit correlation matrix manually"))
            correlation_matrix = CorrelationUIComponents._render_correlation_matrix_editor(config_manager, lang)
        else:
            # Show predefined scenario info
            if correlation_config:
                description = correlation_config.get('description', 'Scenario predefinito')
                st.info(f"📋 {description}")
                try:
                    correlation_matrix = np.array(correlation_config['matrix'])
                except Exception as e:
                    st.error(f"Error loading correlation matrix: {str(e)}")
                    # Fallback to identity matrix
                    asset_names = list(config_manager.asset_characteristics.keys())
                    correlation_matrix = np.eye(len(asset_names))
            else:
                # Fallback to identity matrix
                asset_names = list(config_manager.asset_characteristics.keys())
                correlation_matrix = np.eye(len(asset_names))
        
        return selected_scenario, correlation_matrix
    
    @staticmethod
    def _render_correlation_matrix_editor(config_manager, lang):
        """Render editable correlation matrix with error handling"""
        try:
            asset_names = list(config_manager.asset_characteristics.keys())
            translated_names = get_asset_names(lang)
            display_names = [translated_names.get(name, name) for name in asset_names]
            
            n_assets = len(asset_names)
            
            # Initialize correlation matrix in session state
            if 'custom_correlation_matrix' not in st.session_state:
                st.session_state.custom_correlation_matrix = np.eye(n_assets)
            
            correlation_matrix = st.session_state.custom_correlation_matrix
            
            # Ensure matrix has correct dimensions
            if correlation_matrix.shape != (n_assets, n_assets):
                st.warning("Resetting correlation matrix due to dimension mismatch")
                correlation_matrix = np.eye(n_assets)
                st.session_state.custom_correlation_matrix = correlation_matrix
            
            st.markdown("**" + ("Matrice di Correlazione Personalizzata:" if lang == 'it' else "Custom Correlation Matrix:") + "**")
            
            # Simplified matrix editor for small number of assets
            if n_assets <= 6:  # Full matrix editor only for small matrices
                CorrelationUIComponents._render_full_matrix_editor(correlation_matrix, display_names, lang)
            else:
                # Simplified editor for larger matrices
                st.info("Matrice troppo grande per editor completo - usando editor semplificato")
                CorrelationUIComponents._render_simplified_matrix_editor(correlation_matrix, display_names, lang)
            
            # Validation and reset buttons
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔄 " + ("Reset Identità" if lang == 'it' else "Reset Identity")):
                    st.session_state.custom_correlation_matrix = np.eye(n_assets)
                    st.rerun()
            
            with col2:
                if st.button("⚖️ " + ("Validazione" if lang == 'it' else "Validate")):
                    CorrelationUIComponents._validate_correlation_matrix(correlation_matrix, lang)
            
            return correlation_matrix
            
        except Exception as e:
            st.error(f"Error in correlation matrix editor: {str(e)}")
            # Return identity matrix as safe fallback
            n_assets = len(list(config_manager.asset_characteristics.keys()))
            return np.eye(n_assets)
    
    @staticmethod
    def _render_full_matrix_editor(correlation_matrix, display_names, lang):
        """Render full matrix editor for small matrices"""
        n_assets = len(display_names)
        
        # Create correlation matrix input
        cols = st.columns(n_assets + 1)
        
        # Header row
        cols[0].markdown("**Asset**")
        for i, display_name in enumerate(display_names):
            cols[i + 1].markdown(f"**{display_name[:8]}**")  # Truncate long names
        
        # Matrix input rows
        for i in range(n_assets):
            cols[0].markdown(f"**{display_names[i][:12]}**")
            
            for j in range(n_assets):
                if i == j:
                    # Diagonal elements are always 1
                    cols[j + 1].markdown("1.00")
                    correlation_matrix[i, j] = 1.0
                elif i < j:
                    # Upper triangle - editable
                    try:
                        corr_value = cols[j + 1].number_input(
                            f"",
                            value=float(correlation_matrix[i, j]),
                            min_value=-1.0,
                            max_value=1.0,
                            step=0.01,
                            format="%.2f",
                            key=f"corr_{i}_{j}",
                            label_visibility="collapsed"
                        )
                        correlation_matrix[i, j] = corr_value
                        correlation_matrix[j, i] = corr_value  # Symmetric
                    except Exception as e:
                        cols[j + 1].error(f"Error: {str(e)}")
                        correlation_matrix[i, j] = 0.0
                        correlation_matrix[j, i] = 0.0
                else:
                    # Lower triangle - show symmetric value
                    cols[j + 1].markdown(f"{correlation_matrix[i, j]:.2f}")
        
        # Update session state
        st.session_state.custom_correlation_matrix = correlation_matrix
    
    @staticmethod
    def _render_simplified_matrix_editor(correlation_matrix, display_names, lang):
        """Render simplified matrix editor for large matrices"""
        st.info("Editor semplificato - modifica solo le correlazioni principali")
        
        # Show current matrix as dataframe
        df = pd.DataFrame(correlation_matrix, index=display_names, columns=display_names)
        st.dataframe(df.round(2))
        
        # Allow editing of specific pairs
        st.markdown("**Modifica correlazioni specifiche:**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            asset1 = st.selectbox("Asset 1:", display_names, key="asset1_select")
        
        with col2:
            asset2 = st.selectbox("Asset 2:", display_names, key="asset2_select")
        
        with col3:
            if asset1 != asset2:
                current_corr = correlation_matrix[display_names.index(asset1), display_names.index(asset2)]
                new_corr = st.number_input(
                    "Correlazione:",
                    value=float(current_corr),
                    min_value=-1.0,
                    max_value=1.0,
                    step=0.01,
                    format="%.2f"
                )
                
                if st.button("Aggiorna"):
                    i = display_names.index(asset1)
                    j = display_names.index(asset2)
                    correlation_matrix[i, j] = new_corr
                    correlation_matrix[j, i] = new_corr
                    st.session_state.custom_correlation_matrix = correlation_matrix
                    st.rerun()
    
    @staticmethod
    def _validate_correlation_matrix(matrix, lang):
        """Validate correlation matrix properties with error handling"""
        try:
            # Check if symmetric
            is_symmetric = np.allclose(matrix, matrix.T, rtol=1e-10, atol=1e-10)
            
            # Check if positive semi-definite
            eigenvals = np.linalg.eigvals(matrix)
            is_psd = np.all(eigenvals >= -1e-8)
            
            # Check diagonal elements
            diagonal_ones = np.allclose(np.diag(matrix), 1.0, rtol=1e-10, atol=1e-10)
            
            # Check correlation bounds
            valid_bounds = np.all((matrix >= -1.0) & (matrix <= 1.0))
            
            if is_symmetric and is_psd and diagonal_ones and valid_bounds:
                st.success("✅ " + ("Matrice di correlazione valida!" if lang == 'it' else "Valid correlation matrix!"))
            else:
                errors = []
                if not is_symmetric:
                    errors.append("Non simmetrica" if lang == 'it' else "Not symmetric")
                if not is_psd:
                    errors.append("Non semi-definita positiva" if lang == 'it' else "Not positive semi-definite")
                if not diagonal_ones:
                    errors.append("Diagonale non unitaria" if lang == 'it' else "Diagonal not unity")
                if not valid_bounds:
                    errors.append("Valori fuori range [-1,1]" if lang == 'it' else "Values outside [-1,1] range")
                
                st.error("❌ " + ("Errori nella matrice: " if lang == 'it' else "Matrix errors: ") + ", ".join(errors))
        
        except Exception as e:
            st.error("❌ " + ("Errore di validazione: " if lang == 'it' else "Validation error: ") + str(e))
    
    @staticmethod
    def render_correlation_visualization(correlation_matrix, asset_names, lang):
        """Render correlation matrix visualization with error handling"""
        try:
            st.subheader("📈 " + ("Visualizzazione Matrice di Correlazione" if lang == 'it' else "Correlation Matrix Visualization"))
            
            translated_names = get_asset_names(lang)
            display_names = [translated_names.get(name, name) for name in asset_names]
            
            # Ensure matrix and names match
            if correlation_matrix.shape[0] != len(display_names):
                st.error("Dimension mismatch between correlation matrix and asset names")
                return
            
            # Create heatmap
            fig = px.imshow(
                correlation_matrix,
                x=display_names,
                y=display_names,
                color_continuous_scale='RdBu',
                aspect='auto',
                title="Matrice di Correlazione Asset" if lang == 'it' else "Asset Correlation Matrix",
                zmin=-1,
                zmax=1
            )
            
            # Add correlation values as text
            fig.update_traces(
                text=np.around(correlation_matrix, decimals=2),
                texttemplate="%{text}",
                textfont={"size": 10}
            )
            
            fig.update_layout(
                width=600,
                height=500,
                xaxis_title="Asset",
                yaxis_title="Asset"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Correlation statistics
            CorrelationUIComponents._show_correlation_statistics(correlation_matrix, display_names, lang)
            
        except Exception as e:
            st.error(f"Error in correlation visualization: {str(e)}")
            st.info("Correlation visualization not available")
    
    @staticmethod
    def _show_correlation_statistics(correlation_matrix, display_names, lang):
        """Show correlation matrix statistics with error handling"""
        try:
            st.subheader("📊 " + ("Statistiche di Correlazione" if lang == 'it' else "Correlation Statistics"))
            
            # Extract upper triangle (excluding diagonal)
            upper_triangle = np.triu(correlation_matrix, k=1)
            correlations = upper_triangle[upper_triangle != 0]
            
            if len(correlations) > 0:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Media" if lang == 'it' else "Average",
                        f"{np.mean(correlations):.3f}"
                    )
                
                with col2:
                    st.metric(
                        "Minimo" if lang == 'it' else "Minimum",
                        f"{np.min(correlations):.3f}"
                    )
                
                with col3:
                    st.metric(
                        "Massimo" if lang == 'it' else "Maximum",
                        f"{np.max(correlations):.3f}"
                    )
        
        except Exception as e:
            st.error(f"Error in correlation statistics: {str(e)}")
    
    @staticmethod
    def render_correlation_impact_analysis(lang):
        """Render analysis of correlation impact on portfolio with error handling"""
        try:
            st.subheader("🎯 " + ("Analisi Impatto Correlazione" if lang == 'it' else "Correlation Impact Analysis"))
            
            # Explanation of correlation effects
            if lang == 'it':
                st.markdown("""
                **Come la correlazione influenza il portafoglio:**
                
                📈 **Correlazione Positiva (0 < r < 1):**
                - Gli asset si muovono nella stessa direzione
                - Riduce l'efficacia della diversificazione
                - Aumenta il rischio durante le crisi
                
                📉 **Correlazione Negativa (-1 < r < 0):**
                - Gli asset si muovono in direzioni opposte
                - Migliora la diversificazione
                - Fornisce protezione naturale
                
                🔄 **Correlazione Zero (r = 0):**
                - Movimenti completamente indipendenti
                - Massima efficacia della diversificazione teorica
                - Raramente osservato nella realtà
                """)
            else:
                st.markdown("""
                **How correlation affects your portfolio:**
                
                📈 **Positive Correlation (0 < r < 1):**
                - Assets move in the same direction
                - Reduces diversification effectiveness
                - Increases risk during crises
                
                📉 **Negative Correlation (-1 < r < 0):**
                - Assets move in opposite directions
                - Improves diversification
                - Provides natural protection
                
                🔄 **Zero Correlation (r = 0):**
                - Completely independent movements
                - Maximum theoretical diversification benefit
                - Rarely observed in reality
                """)
        
        except Exception as e:
            st.error(f"Error in correlation impact analysis: {str(e)}")
    
    @staticmethod
    def render_correlation_toggle(lang):
        """Render toggle to enable/disable correlation in simulation with error handling"""
        try:
            st.subheader("⚙️ " + ("Impostazioni Simulazione" if lang == 'it' else "Simulation Settings"))
            
            use_correlation = st.checkbox(
                "🔗 " + ("Abilita correlazione tra asset" if lang == 'it' else "Enable asset correlation"),
                value=st.session_state.get('use_correlation', False),  # Default to False for safety
                help=("Se disabilitato, gli asset verranno simulati indipendentemente (comportamento attuale dell'app)" 
                      if lang == 'it' else 
                      "If disabled, assets will be simulated independently (current app behavior)"),
                key='correlation_enabled'
            )
            
            if use_correlation:
                st.info("✅ " + ("La correlazione è abilitata - simulazione più realistica" 
                               if lang == 'it' else "Correlation enabled - more realistic simulation"))
            else:
                st.warning("⚠️ " + ("Correlazione disabilitata - asset indipendenti" 
                                  if lang == 'it' else "Correlation disabled - independent assets"))
            
            return use_correlation
            
        except Exception as e:
            st.error(f"Error in correlation toggle: {str(e)}")
            return False  # Safe default
