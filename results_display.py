"""
Enhanced results display components with simplified tax analysis and new chart types
FIXED VERSION - Corrected final real values calculation
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from translations import get_text


class ResultsDisplay:
    """Enhanced display of simulation results with simplified tax analysis"""
    
    @staticmethod
    def calculate_cagr(final_value, initial_value, years):
        """Calculate Compound Annual Growth Rate"""
        if initial_value <= 0 or final_value <= 0 or years <= 0:
            return 0
        return ((final_value / initial_value) ** (1/years) - 1) * 100
    
    @staticmethod
    def calculate_total_deposited(initial_amount, annual_contribution, years_to_retirement, 
                                 adjust_contribution_inflation, inflation):
        """Calculate total amount deposited"""
        if adjust_contribution_inflation:
            # Calculate total with inflation adjustment
            total_deposited = initial_amount
            current_contribution = annual_contribution
            for year in range(int(years_to_retirement)):
                total_deposited += current_contribution
                current_contribution *= (1 + inflation / 100)  # Adjust for next year
        else:
            # Simple calculation without inflation adjustment
            total_deposited = initial_amount + (annual_contribution * years_to_retirement)
        
        return total_deposited
    
    @staticmethod
    def show_results(results, simulator, total_deposited, n_simulations, years_to_retirement, 
                    years_retired, capital_gains_tax_rate, nominal_withdrawal, inflation_rate, lang):
        """Display simplified simulation results with enhanced charts"""
        st.markdown("---")
        st.header(get_text('simulation_results', lang))
        
        accumulation_balances = results['accumulation']
        accumulation_balances_nominal = results['accumulation_nominal']
        final_results = results['final']
        
        # FIXED: Calculate final results in real terms (adjusted for inflation)
        # The inflation_rate is passed as percentage (e.g., 2.5), so we need to divide by 100
        inflation_decimal = inflation_rate / 100 if inflation_rate > 1 else inflation_rate
        
        # Total inflation factor over the entire period (accumulation + retirement)
        total_inflation_factor = (1 + inflation_decimal) ** (years_to_retirement + years_retired)
        
        # Convert final results to real terms
        final_results_real = [value / total_inflation_factor for value in final_results]
        
        # Get statistics
        stats = simulator.get_statistics()
        
        # Add real final values statistics
        stats['final_real'] = {
            'mean': np.mean(final_results_real),
            'median': np.percentile(final_results_real, 50),
            'p25': np.percentile(final_results_real, 25),
            'p75': np.percentile(final_results_real, 75),
            'p10': np.percentile(final_results_real, 10),
            'p90': np.percentile(final_results_real, 90)
        }
        
        # Display key metrics
        ResultsDisplay._show_key_metrics(
            total_deposited, stats['accumulation']['median'], 
            stats['accumulation']['median'], stats['success_rate'], lang
        )
        
        # Display simplified tax impact analysis
        ResultsDisplay._show_simplified_tax_analysis(
            results, total_deposited, nominal_withdrawal, capital_gains_tax_rate, lang
        )
        
        # Display enhanced detailed statistics with nominal and real final values
        ResultsDisplay._show_enhanced_detailed_statistics(
            stats, years_to_retirement, years_retired, total_deposited, inflation_rate, lang
        )
        
        # Display enhanced charts with scatter plots and real/nominal final values
        ResultsDisplay._show_enhanced_charts_with_scatter(
            accumulation_balances_nominal, accumulation_balances, 
            final_results, final_results_real, lang
        )
        
        # Display success message
        ResultsDisplay._show_success_message(stats['success_rate'], lang)
    
    @staticmethod
    def _show_key_metrics(total_deposited, median_accumulation, median_final, success_rate, lang):
        """Display key metrics in columns"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(get_text('total_deposited', lang), f"€{total_deposited:,.0f}")
        with col2:
            st.metric(get_text('median_accumulation', lang), f"€{median_accumulation:,.0f}")
        with col3:
            st.metric(get_text('median_final', lang), f"€{median_final:,.0f}")
        with col4:
            st.metric(get_text('success_rate', lang), f"{success_rate:.1f}%")
    
    @staticmethod
    def _show_simplified_tax_analysis(results, total_deposited, nominal_withdrawal, capital_gains_tax_rate, lang):
        """Display simplified tax impact analysis with only basic metrics"""
        st.subheader("💰 Analisi Impatto Fiscale" if lang == 'it' else "💰 Tax Impact Analysis")
        
        # Create simplified columns - REMOVED Tax Burden Distribution column
        col1, col2 = st.columns(2)  # Changed from 3 to 2 columns
        
        # Get tax analysis if available
        try:
            tax_analysis = results.get('tax_details', [])
            valid_tax_details = [detail for detail in tax_analysis if detail]
            
            if valid_tax_details:
                # Enhanced tax analysis available
                total_taxes = [detail['total_taxes_paid'] for detail in valid_tax_details]
                effective_rates = []
                
                for detail in valid_tax_details:
                    if detail['total_withdrawals'] > 0:
                        rate = (detail['total_taxes_paid'] / detail['total_withdrawals']) * 100
                        effective_rates.append(rate)
                    else:
                        effective_rates.append(0.0)
                
                with col1:
                    st.subheader("📊 Tasse Totali" if lang == 'it' else "📊 Total Taxes")
                    st.metric("Mediana", f"€{np.median(total_taxes):,.0f}")
                    st.metric("Media", f"€{np.mean(total_taxes):,.0f}")
                    st.metric("Min - Max", f"€{np.min(total_taxes):,.0f} - €{np.max(total_taxes):,.0f}")
                
                with col2:
                    st.subheader("📈 Aliquota Effettiva" if lang == 'it' else "📈 Effective Tax Rate")
                    st.metric("Mediana", f"{np.median(effective_rates):.2f}%")
                    st.metric("Media", f"{np.mean(effective_rates):.2f}%")
                    st.metric("Range", f"{np.min(effective_rates):.2f}% - {np.max(effective_rates):.2f}%")
                
                # Tax efficiency insights
                mean_rate = np.mean(effective_rates)
                if mean_rate <= capital_gains_tax_rate:
                    efficiency_savings = max(0, (capital_gains_tax_rate - mean_rate) / capital_gains_tax_rate * 100)
                    st.info(f"""
                    **💡 Insights Fiscali:**
                    - **Aliquota nominale**: {capital_gains_tax_rate:.1f}% sui capital gains
                    - **Aliquota effettiva media**: {mean_rate:.2f}% sui prelievi totali
                    - **Efficienza fiscale**: {efficiency_savings:.1f}% di risparmio rispetto alla tassazione piena
                    - **Spiegazione**: L'aliquota effettiva è più bassa perché le tasse si applicano solo ai capital gains, non all'intero prelievo
                    """ if lang == 'it' else f"""
                    **💡 Tax Insights:**
                    - **Nominal rate**: {capital_gains_tax_rate:.1f}% on capital gains
                    - **Average effective rate**: {mean_rate:.2f}% on total withdrawals
                    - **Tax efficiency**: {efficiency_savings:.1f}% savings compared to full taxation
                    - **Explanation**: The effective rate is lower because taxes apply only to capital gains, not the entire withdrawal
                    """)
                
            else:
                # Fallback to traditional analysis
                ResultsDisplay._show_traditional_tax_analysis(
                    results, total_deposited, nominal_withdrawal, capital_gains_tax_rate, lang
                )
                
        except Exception:
            # Fallback to traditional analysis in case of errors
            ResultsDisplay._show_traditional_tax_analysis(
                results, total_deposited, nominal_withdrawal, capital_gains_tax_rate, lang
            )
    
    @staticmethod
    def _show_traditional_tax_analysis(results, total_deposited, nominal_withdrawal, capital_gains_tax_rate, lang):
        """Display traditional tax analysis (fallback method)"""
        # Calculate median values for traditional analysis
        median_acc_nominal = np.percentile(results['accumulation_nominal'], 50)
        
        if median_acc_nominal > total_deposited:
            capital_gains_nominal = median_acc_nominal - total_deposited
            capital_gains_percentage = capital_gains_nominal / median_acc_nominal
            effective_tax_rate = (capital_gains_tax_rate / 100) * capital_gains_percentage
            gross_withdrawal_needed = nominal_withdrawal / (1 - effective_tax_rate)
            tax_impact_percent = ((gross_withdrawal_needed - nominal_withdrawal) / nominal_withdrawal) * 100
            
            st.info(f"""
            **📊 Analisi Impatto Fiscale (Caso Mediano):**
            - Totale Depositato (Nominale): €{total_deposited:,.0f}
            - Valore Portafoglio (Nominale): €{median_acc_nominal:,.0f}
            - Capital Gains: €{capital_gains_nominal:,.0f} ({capital_gains_percentage:.1%})
            - Aliquota Capital Gains: {capital_gains_tax_rate:.1f}%
            - Aliquota Effettiva sui Prelievi: {effective_tax_rate:.2%}
            - **Prelievo Annuale Target (Netto)**: €{nominal_withdrawal:,.0f}
            - **Prelievo Lordo Necessario**: €{gross_withdrawal_needed:,.0f}
            - **Importo Aggiuntivo per Tasse**: {tax_impact_percent:.2f}% in più
            """ if lang == 'it' else f"""
            **📊 Tax Impact Analysis (Median Case):**
            - Total Deposited (Nominal): €{total_deposited:,.0f}
            - Portfolio Value (Nominal): €{median_acc_nominal:,.0f}
            - Capital Gains: €{capital_gains_nominal:,.0f} ({capital_gains_percentage:.1%})
            - Capital Gains Tax Rate: {capital_gains_tax_rate:.1f}%
            - Effective Tax Rate on Withdrawals: {effective_tax_rate:.2%}
            - **Target Annual Withdrawal (Net)**: €{nominal_withdrawal:,.0f}
            - **Required Gross Withdrawal**: €{gross_withdrawal_needed:,.0f}
            - **Additional Amount for Taxes**: {tax_impact_percent:.2f}% more
            """)
        else:
            st.info(f"""
            **📊 Analisi Impatto Fiscale (Caso Mediano):**
            - Totale Depositato (Nominale): €{total_deposited:,.0f}
            - Valore Portafoglio (Nominale): €{median_acc_nominal:,.0f}
            - **Nessun capital gain** (Portafoglio ≤ Importo Depositato)
            - **Nessuna tassa sui capital gains applicata** ✅
            - Prelievo Annuale: €{nominal_withdrawal:,.0f} (nessun importo aggiuntivo necessario)
            """ if lang == 'it' else f"""
            **📊 Tax Impact Analysis (Median Case):**
            - Total Deposited (Nominal): €{total_deposited:,.0f}
            - Portfolio Value (Nominal): €{median_acc_nominal:,.0f}
            - **No capital gains** (Portfolio ≤ Amount Deposited)
            - **No capital gains tax applied** ✅
            - Annual Withdrawal: €{nominal_withdrawal:,.0f} (no additional amount needed)
            """)
    
    @staticmethod
    def _show_enhanced_detailed_statistics(stats, years_to_retirement, years_retired, total_deposited, inflation_rate, lang):
        """Display enhanced detailed statistics with nominal and real final values"""
        st.subheader("📊 Statistiche Dettagliate" if lang == 'it' else "📊 Detailed Statistics")
        
        # Changed to 4 columns to include both nominal and real final values
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.subheader("💰 Accumulo (Nominale)" if lang == 'it' else "💰 Accumulation (Nominal)")
            acc_nominal = stats['accumulation_nominal']
            
            data = {
                ('Percentile' if lang == 'en' else 'Percentile'): ['Mediana', '25°', '75°', 'Media'],
                ('Valore (€)' if lang == 'it' else 'Value (€)'): [
                    f"{acc_nominal['median']:,.0f}", f"{acc_nominal['p25']:,.0f}", 
                    f"{acc_nominal['p75']:,.0f}", f"{acc_nominal['mean']:,.0f}"
                ],
                'CAGR (%)': [
                    f"{ResultsDisplay.calculate_cagr(acc_nominal['median'], total_deposited, years_to_retirement):.2f}%",
                    f"{ResultsDisplay.calculate_cagr(acc_nominal['p25'], total_deposited, years_to_retirement):.2f}%",
                    f"{ResultsDisplay.calculate_cagr(acc_nominal['p75'], total_deposited, years_to_retirement):.2f}%",
                    f"{ResultsDisplay.calculate_cagr(acc_nominal['mean'], total_deposited, years_to_retirement):.2f}%"
                ]
            }
            st.table(pd.DataFrame(data))
        
        with col2:
            st.subheader("📈 Accumulo (Reale)" if lang == 'it' else "📈 Accumulation (Real)")
            acc_real = stats['accumulation']
            
            data = {
                ('Percentile' if lang == 'en' else 'Percentile'): ['Mediana', '25°', '75°', 'Media'],
                ('Valore (€)' if lang == 'it' else 'Value (€)'): [
                    f"{acc_real['median']:,.0f}", f"{acc_real['p25']:,.0f}", 
                    f"{acc_real['p75']:,.0f}", f"{acc_real['mean']:,.0f}"
                ],
                'CAGR (%)': [
                    f"{ResultsDisplay.calculate_cagr(acc_real['median'], total_deposited, years_to_retirement):.2f}%",
                    f"{ResultsDisplay.calculate_cagr(acc_real['p25'], total_deposited, years_to_retirement):.2f}%",
                    f"{ResultsDisplay.calculate_cagr(acc_real['p75'], total_deposited, years_to_retirement):.2f}%",
                    f"{ResultsDisplay.calculate_cagr(acc_real['mean'], total_deposited, years_to_retirement):.2f}%"
                ]
            }
            st.table(pd.DataFrame(data))
        
        with col3:
            st.subheader("🏁 Finali (Nominali)" if lang == 'it' else "🏁 Final (Nominal)")
            final_nominal = stats['final']
            
            data = {
                ('Percentile' if lang == 'en' else 'Percentile'): ['Mediana', '25°', '75°', 'Media'],
                ('Valore (€)' if lang == 'it' else 'Value (€)'): [
                    f"{final_nominal['median']:,.0f}", f"{final_nominal['p25']:,.0f}", 
                    f"{final_nominal['p75']:,.0f}", f"{final_nominal['mean']:,.0f}"
                ]
            }
            st.table(pd.DataFrame(data))
        
        with col4:
            st.subheader("🏁 Finali (Reali)" if lang == 'it' else "🏁 Final (Real)")
            
            # Check if final_real exists in stats, if not create it
            if 'final_real' not in stats:
                st.warning("⚠️ Dati valori finali reali non disponibili" if lang == 'it' else "⚠️ Real final values data not available")
                return
                
            final_real = stats['final_real']
                        
            data = {
                ('Percentile' if lang == 'en' else 'Percentile'): ['Mediana', '25°', '75°', 'Media'],
                ('Valore (€)' if lang == 'it' else 'Value (€)'): [
                    f"{final_real['median']:,.0f}", f"{final_real['p25']:,.0f}", 
                    f"{final_real['p75']:,.0f}", f"{final_real['mean']:,.0f}"
                ]
            }
            st.table(pd.DataFrame(data))
    
    @staticmethod
    def _show_enhanced_charts_with_scatter(accumulation_nominal, accumulation_real, final_nominal, final_real, lang):
        """Display enhanced charts with scatter plots and histogram distributions"""
        st.subheader("📈 Grafici di Distribuzione e Correlazione" if lang == 'it' else "📈 Distribution and Correlation Charts")
        
        # Create tabs for different chart types
        tab1, tab2, tab3 = st.tabs([
            "📊 Distribuzioni" if lang == 'it' else "📊 Distributions", 
            "🔗 Correlazioni (Nominali)" if lang == 'it' else "🔗 Correlations (Nominal)",
            "📈 Confronto Nominali vs Reali" if lang == 'it' else "📈 Nominal vs Real Comparison"
        ])
        
        with tab1:
            # Distribution histograms
            col1, col2 = st.columns(2)
            
            with col1:
                # Accumulation distributions
                fig_acc_nominal = px.histogram(
                    x=accumulation_nominal, 
                    nbins=50, 
                    title="Distribuzione Valori Accumulo (Nominale)" if lang == 'it' else "Accumulation Values Distribution (Nominal)"
                )
                fig_acc_nominal.update_xaxes(title="Valore (€)" if lang == 'it' else "Value (€)")
                fig_acc_nominal.update_yaxes(title="Frequenza" if lang == 'it' else "Frequency")
                st.plotly_chart(fig_acc_nominal, use_container_width=True)
                
                fig_acc_real = px.histogram(
                    x=accumulation_real, 
                    nbins=50, 
                    title="Distribuzione Valori Accumulo (Reale)" if lang == 'it' else "Accumulation Values Distribution (Real)"
                )
                fig_acc_real.update_xaxes(title="Valore (€)" if lang == 'it' else "Value (€)")
                fig_acc_real.update_yaxes(title="Frequenza" if lang == 'it' else "Frequency")
                st.plotly_chart(fig_acc_real, use_container_width=True)
            
            with col2:
                # Final value distributions
                fig_final_nominal = px.histogram(
                    x=final_nominal, 
                    nbins=50, 
                    title="Distribuzione Valori Finali (Nominali)" if lang == 'it' else "Final Values Distribution (Nominal)"
                )
                fig_final_nominal.update_xaxes(title="Valore (€)" if lang == 'it' else "Value (€)")
                fig_final_nominal.update_yaxes(title="Frequenza" if lang == 'it' else "Frequency")
                st.plotly_chart(fig_final_nominal, use_container_width=True)
                
                fig_final_real = px.histogram(
                    x=final_real, 
                    nbins=50, 
                    title="Distribuzione Valori Finali (Reali)" if lang == 'it' else "Final Values Distribution (Real)"
                )
                fig_final_real.update_xaxes(title="Valore (€)" if lang == 'it' else "Value (€)")
                fig_final_real.update_yaxes(title="Frequenza" if lang == 'it' else "Frequency")
                st.plotly_chart(fig_final_real, use_container_width=True)
        
        with tab2:
            # Scatter plots for nominal values only - with data validation
            if len(accumulation_nominal) == 0 or len(final_nominal) == 0:
                st.warning("⚠️ Dati insufficienti per i grafici di correlazione" if lang == 'it' else "⚠️ Insufficient data for correlation charts")
                return
                
            col1, col2 = st.columns(2)
            
            with col1:
                # Scatter plot: Accumulation vs Final (Nominal)
                fig_scatter_acc_final = px.scatter(
                    x=accumulation_nominal,
                    y=final_nominal,
                    title="Correlazione Accumulo vs Finale (Nominale)" if lang == 'it' else "Accumulation vs Final Correlation (Nominal)",
                    labels={
                        'x': 'Valore Fine Accumulo (€)' if lang == 'it' else 'End of Accumulation Value (€)', 
                        'y': 'Valore Finale (€)' if lang == 'it' else 'Final Value (€)'
                    },
                    opacity=0.6
                )
                fig_scatter_acc_final.update_traces(marker=dict(size=4))
                st.plotly_chart(fig_scatter_acc_final, use_container_width=True)
                
                # Add correlation coefficient with validation
                try:
                    correlation_acc_final = np.corrcoef(accumulation_nominal, final_nominal)[0, 1]
                    if np.isnan(correlation_acc_final):
                        st.info("**Correlazione**: Non calcolabile (varianza zero)")
                    else:
                        st.info(f"**Correlazione**: {correlation_acc_final:.3f}")
                except:
                    st.info("**Correlazione**: Non calcolabile")
            
            with col2:
                # Enhanced scatter plot with color gradient based on accumulation value
                fig_scatter_enhanced = px.scatter(
                    x=accumulation_nominal,
                    y=final_nominal,
                    color=accumulation_nominal,
                    title="Mappa di Calore: Accumulo → Finale (Nominale)" if lang == 'it' else "Heat Map: Accumulation → Final (Nominal)",
                    labels={
                        'x': 'Valore Fine Accumulo (€)' if lang == 'it' else 'End of Accumulation Value (€)', 
                        'y': 'Valore Finale (€)' if lang == 'it' else 'Final Value (€)',
                        'color': 'Valore Accumulo' if lang == 'it' else 'Accumulation Value'
                    },
                    color_continuous_scale='Viridis'
                )
                fig_scatter_enhanced.update_traces(marker=dict(size=4))
                st.plotly_chart(fig_scatter_enhanced, use_container_width=True)
        
        with tab3:
            # Comparison between nominal and real values
            col1, col2 = st.columns(2)
            
            with col1:
                # Box plot comparison for final values
                fig_box_final = go.Figure()
                
                fig_box_final.add_trace(go.Box(
                    y=final_nominal,
                    name="Nominali" if lang == 'it' else "Nominal",
                    boxmean='sd',
                    marker_color='lightblue'
                ))
                
                fig_box_final.add_trace(go.Box(
                    y=final_real,
                    name="Reali" if lang == 'it' else "Real",
                    boxmean='sd',
                    marker_color='lightcoral'
                ))
                
                fig_box_final.update_layout(
                    title="Confronto Valori Finali: Nominali vs Reali" if lang == 'it' else "Final Values Comparison: Nominal vs Real",
                    yaxis_title="Valore (€)" if lang == 'it' else "Value (€)",
                    showlegend=True
                )
                
                st.plotly_chart(fig_box_final, use_container_width=True)
            
            with col2:
                # Scatter plot: Nominal vs Real final values
                fig_scatter_nom_real = px.scatter(
                    x=final_real,
                    y=final_nominal,
                    title="Correlazione Valori Finali: Reali vs Nominali" if lang == 'it' else "Final Values Correlation: Real vs Nominal",
                    labels={
                        'x': 'Valore Finale Reale (€)' if lang == 'it' else 'Real Final Value (€)', 
                        'y': 'Valore Finale Nominale (€)' if lang == 'it' else 'Nominal Final Value (€)'
                    },
                    opacity=0.6
                )
                
                # Add diagonal line for reference
                min_val = min(min(final_real), min(final_nominal))
                max_val = max(max(final_real), max(final_nominal))
                fig_scatter_nom_real.add_trace(
                    go.Scatter(
                        x=[min_val, max_val],
                        y=[min_val, max_val],
                        mode='lines',
                        name='Linea 1:1' if lang == 'it' else '1:1 Line',
                        line=dict(dash='dash', color='red')
                    )
                )
                
                fig_scatter_nom_real.update_traces(marker=dict(size=4))
                st.plotly_chart(fig_scatter_nom_real, use_container_width=True)
                
                # Show inflation impact statistics with zero-division protection
                valid_pairs = [(nom, real) for nom, real in zip(final_nominal, final_real) if nom > 0]
                
                if valid_pairs:
                    inflation_impact = np.mean([(nom - real) / nom * 100 for nom, real in valid_pairs])
                    avg_real_percentage = 100 - inflation_impact
                    
                    st.info(f"""
                    **Impatto Inflazione Media**: {inflation_impact:.1f}%
                    
                    I valori reali sono mediamente il {avg_real_percentage:.1f}% dei valori nominali
                    
                    *Calcolato su {len(valid_pairs)} scenari con portafoglio residuo > 0*
                    """ if lang == 'it' else f"""
                    **Average Inflation Impact**: {inflation_impact:.1f}%
                    
                    Real values are on average {avg_real_percentage:.1f}% of nominal values
                    
                    *Calculated on {len(valid_pairs)} scenarios with remaining portfolio > 0*
                    """)
                else:
                    st.warning("""
                    **⚠️ Attenzione**: Tutti gli scenari hanno portafoglio esaurito (valore finale = 0)
                    
                    Impossibile calcolare l'impatto inflazione
                    """ if lang == 'it' else """
                    **⚠️ Warning**: All scenarios have depleted portfolio (final value = 0)
                    
                    Cannot calculate inflation impact
                    """)
    
    @staticmethod
    def _show_success_message(success_rate, lang):
        """Display success rate message with appropriate styling"""
        if success_rate >= 80:
            st.success(get_text('excellent_success', lang).format(success_rate))
        elif success_rate >= 60:
            st.warning(get_text('fair_success', lang).format(success_rate))
        else:
            st.error(get_text('warning_success', lang).format(success_rate))
