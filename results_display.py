"""
Enhanced results display components with detailed tax analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from translations import get_text


class ResultsDisplay:
    """Enhanced display of simulation results with detailed tax analysis"""
    
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
                    years_retired, capital_gains_tax_rate, nominal_withdrawal, lang):
        """Display comprehensive simulation results with detailed tax analysis"""
        st.markdown("---")
        st.header(get_text('simulation_results', lang))
        
        accumulation_balances = results['accumulation']
        accumulation_balances_nominal = results['accumulation_nominal']
        final_results = results['final']
        
        # Get statistics and tax analysis
        stats = simulator.get_statistics()
        tax_analysis = simulator.get_tax_analysis()
        
        # Check if enhanced tax calculation is available
        has_enhanced_tax = bool(tax_analysis and simulator.use_enhanced_tax)
        
        # Display key metrics
        ResultsDisplay._show_key_metrics(
            total_deposited, stats['accumulation']['median'], 
            stats['final']['median'], stats['success_rate'], lang
        )
        
        # Display tax impact analysis if available
        if has_enhanced_tax:
            ResultsDisplay._show_enhanced_tax_analysis(
                tax_analysis, nominal_withdrawal, capital_gains_tax_rate, lang
            )
        else:
            # Show traditional tax analysis
            ResultsDisplay._show_traditional_tax_analysis(
                results, total_deposited, nominal_withdrawal, capital_gains_tax_rate, lang
            )
        
        # Display detailed statistics tables
        ResultsDisplay._show_detailed_statistics(stats, years_to_retirement, total_deposited, lang)
        
        # Display tax statistics if available
        if has_enhanced_tax:
            ResultsDisplay._show_tax_statistics(tax_analysis, lang)
        
        # Display charts
        if has_enhanced_tax:
            ResultsDisplay._show_enhanced_charts(
                accumulation_balances_nominal, accumulation_balances, final_results, 
                results['tax_details'], lang
            )
        else:
            # Show traditional charts
            ResultsDisplay._show_traditional_charts(
                accumulation_balances_nominal, accumulation_balances, final_results, lang
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
    def _show_enhanced_tax_analysis(tax_analysis, nominal_withdrawal, capital_gains_tax_rate, lang):
        """Display comprehensive enhanced tax impact analysis"""
        st.subheader("💰 Analisi Impatto Fiscale Dettagliata" if lang == 'it' else "💰 Detailed Tax Impact Analysis")
        
        # Create columns for different tax metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("📊 Tasse Totali" if lang == 'it' else "📊 Total Taxes")
            tax_stats = tax_analysis['total_taxes_statistics']
            
            st.metric("Mediana", f"€{tax_stats['median']:,.0f}")
            st.metric("Media", f"€{tax_stats['mean']:,.0f}")
            st.metric("Min - Max", f"€{tax_stats['min']:,.0f} - €{tax_stats['max']:,.0f}")
        
        with col2:
            st.subheader("📈 Aliquota Effettiva" if lang == 'it' else "📈 Effective Tax Rate")
            rate_stats = tax_analysis['effective_tax_rate_statistics']
            
            st.metric("Mediana", f"{rate_stats['median']:.2f}%")
            st.metric("Media", f"{rate_stats['mean']:.2f}%")
            st.metric("Range", f"{rate_stats['min']:.2f}% - {rate_stats['max']:.2f}%")
        
        with col3:
            st.subheader("⚖️ Distribuzione Carico Fiscale" if lang == 'it' else "⚖️ Tax Burden Distribution")
            burden_stats = tax_analysis['tax_burden_analysis']
            
            st.metric("Alta Tassazione (>20%)", f"{burden_stats['percentage_high_tax']:.1f}%")
            st.metric("Bassa Tassazione (<5%)", f"{burden_stats['percentage_low_tax']:.1f}%")
        
        # Tax efficiency insights
        efficiency_savings = max(0, (capital_gains_tax_rate - rate_stats['mean']) / capital_gains_tax_rate * 100)
        st.info(f"""
        **💡 Insights Fiscali:**
        - **Aliquota nominale**: {capital_gains_tax_rate:.1f}% sui capital gains
        - **Aliquota effettiva media**: {rate_stats['mean']:.2f}% sui prelievi totali
        - **Efficienza fiscale**: {efficiency_savings:.1f}% di risparmio rispetto alla tassazione piena
        - **Impatto sui prelievi**: La tassazione riduce i prelievi netti del {rate_stats['mean']:.1f}% in media
        """)
    
    @staticmethod
    def _show_traditional_tax_analysis(results, total_deposited, nominal_withdrawal, capital_gains_tax_rate, lang):
        """Display traditional tax analysis (fallback method)"""
        st.subheader("💰 Analisi Impatto Fiscale" if lang == 'it' else "💰 Tax Impact Analysis")
        
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
            """)
        else:
            st.info(f"""
            **📊 Analisi Impatto Fiscale (Caso Mediano):**
            - Totale Depositato (Nominale): €{total_deposited:,.0f}
            - Valore Portafoglio (Nominale): €{median_acc_nominal:,.0f}
            - **Nessun capital gain** (Portafoglio ≤ Importo Depositato)
            - **Nessuna tassa sui capital gains applicata** ✅
            - Prelievo Annuale: €{nominal_withdrawal:,.0f} (nessun importo aggiuntivo necessario)
            """)
    
    @staticmethod
    def _show_detailed_statistics(stats, years_to_retirement, total_deposited, lang):
        """Display detailed statistics tables with CAGR calculations"""
        st.subheader("📊 Statistiche Dettagliate" if lang == 'it' else "📊 Detailed Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("💰 Accumulo (Nominale)")
            acc_nominal = stats['accumulation_nominal']
            
            data = {
                'Percentile': ['Mediana', '25°', '75°', 'Media'],
                'Valore (€)': [f"{acc_nominal['median']:,.0f}", f"{acc_nominal['p25']:,.0f}", 
                              f"{acc_nominal['p75']:,.0f}", f"{acc_nominal['mean']:,.0f}"],
                'CAGR (%)': [
                    f"{ResultsDisplay.calculate_cagr(acc_nominal['median'], total_deposited, years_to_retirement):.2f}%",
                    f"{ResultsDisplay.calculate_cagr(acc_nominal['p25'], total_deposited, years_to_retirement):.2f}%",
                    f"{ResultsDisplay.calculate_cagr(acc_nominal['p75'], total_deposited, years_to_retirement):.2f}%",
                    f"{ResultsDisplay.calculate_cagr(acc_nominal['mean'], total_deposited, years_to_retirement):.2f}%"
                ]
            }
            st.table(pd.DataFrame(data))
        
        with col2:
            st.subheader("📈 Accumulo (Reale)")
            acc_real = stats['accumulation']
            
            data = {
                'Percentile': ['Mediana', '25°', '75°', 'Media'],
                'Valore (€)': [f"{acc_real['median']:,.0f}", f"{acc_real['p25']:,.0f}", 
                              f"{acc_real['p75']:,.0f}", f"{acc_real['mean']:,.0f}"],
                'CAGR (%)': [
                    f"{ResultsDisplay.calculate_cagr(acc_real['median'], total_deposited, years_to_retirement):.2f}%",
                    f"{ResultsDisplay.calculate_cagr(acc_real['p25'], total_deposited, years_to_retirement):.2f}%",
                    f"{ResultsDisplay.calculate_cagr(acc_real['p75'], total_deposited, years_to_retirement):.2f}%",
                    f"{ResultsDisplay.calculate_cagr(acc_real['mean'], total_deposited, years_to_retirement):.2f}%"
                ]
            }
            st.table(pd.DataFrame(data))
        
        with col3:
            st.subheader("🏁 Valori Finali")
            final = stats['final']
            
            data = {
                'Percentile': ['Mediana', '25°', '75°', 'Media'],
                'Valore (€)': [f"{final['median']:,.0f}", f"{final['p25']:,.0f}", 
                              f"{final['p75']:,.0f}", f"{final['mean']:,.0f}"]
            }
            st.table(pd.DataFrame(data))
    
    @staticmethod
    def _show_tax_statistics(tax_analysis, lang):
        """Display detailed tax statistics"""
        st.subheader("📋 Statistiche Fiscali Dettagliate" if lang == 'it' else "📋 Detailed Tax Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💸 Tasse Pagate nel Tempo")
            tax_stats = tax_analysis['total_taxes_statistics']
            
            tax_data = {
                'Statistica': ['Media', 'Mediana', 'Deviazione Standard', 'Minimo', 'Massimo'],
                'Tasse Totali (€)': [
                    f"{tax_stats['mean']:,.0f}",
                    f"{tax_stats['median']:,.0f}",
                    f"{tax_stats['std']:,.0f}",
                    f"{tax_stats['min']:,.0f}",
                    f"{tax_stats['max']:,.0f}"
                ]
            }
            st.table(pd.DataFrame(tax_data))
        
        with col2:
            st.subheader("📊 Distribuzione Aliquote Effettive")
            rate_stats = tax_analysis['effective_tax_rate_statistics']
            
            rate_data = {
                'Statistica': ['Media', 'Mediana', 'Deviazione Standard', 'Minima', 'Massima'],
                'Aliquota Effettiva (%)': [
                    f"{rate_stats['mean']:.2f}%",
                    f"{rate_stats['median']:.2f}%",
                    f"{rate_stats['std']:.2f}%",
                    f"{rate_stats['min']:.2f}%",
                    f"{rate_stats['max']:.2f}%"
                ]
            }
            st.table(pd.DataFrame(rate_data))
    
    @staticmethod
    def _show_enhanced_charts(accumulation_nominal, accumulation_real, final_results, tax_details, lang):
        """Display enhanced charts including tax analysis"""
        st.subheader("📈 Grafici di Distribuzione" if lang == 'it' else "📈 Distribution Charts")
        
        # Filter valid tax details
        valid_tax_details = [detail for detail in tax_details if detail]
        
        if valid_tax_details:
            tab1, tab2, tab3 = st.tabs([
                "💰 Valori Portafoglio", 
                "💸 Analisi Fiscale", 
                "📊 Confronto Scenari"
            ])
            
            with tab1:
                ResultsDisplay._show_portfolio_charts(accumulation_nominal, accumulation_real, final_results, lang)
            
            with tab2:
                ResultsDisplay._show_tax_charts(valid_tax_details, final_results, lang)
            
            with tab3:
                ResultsDisplay._show_scenario_comparison(valid_tax_details, final_results, lang)
        else:
            # Fallback to traditional charts if no tax details
            ResultsDisplay._show_traditional_charts(accumulation_nominal, accumulation_real, final_results, lang)
    
    @staticmethod
    def _show_traditional_charts(accumulation_nominal, accumulation_real, final_results, lang):
        """Display traditional charts without tax analysis"""
        col1, col2 = st.columns(2)
        
        with col1:
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
            fig_final = px.histogram(
                x=final_results, 
                nbins=50, 
                title="Distribuzione Valori Finali" if lang == 'it' else "Final Values Distribution"
            )
            fig_final.update_xaxes(title="Valore (€)" if lang == 'it' else "Value (€)")
            fig_final.update_yaxes(title="Frequenza" if lang == 'it' else "Frequency")
            st.plotly_chart(fig_final, use_container_width=True)
    
    @staticmethod
    def _show_portfolio_charts(accumulation_nominal, accumulation_real, final_results, lang):
        """Show portfolio value charts"""
        col1, col2 = st.columns(2)
        
        with col1:
            fig_acc_nominal = px.histogram(
                x=accumulation_nominal, 
                nbins=50, 
                title="Distribuzione Valori Accumulo (Nominale)"
            )
            fig_acc_nominal.update_xaxes(title="Valore (€)")
            fig_acc_nominal.update_yaxes(title="Frequenza")
            st.plotly_chart(fig_acc_nominal, use_container_width=True)
            
            fig_acc_real = px.histogram(
                x=accumulation_real, 
                nbins=50, 
                title="Distribuzione Valori Accumulo (Reale)"
            )
            fig_acc_real.update_xaxes(title="Valore (€)")
            fig_acc_real.update_yaxes(title="Frequenza")
            st.plotly_chart(fig_acc_real, use_container_width=True)
        
        with col2:
            fig_final = px.histogram(
                x=final_results, 
                nbins=50, 
                title="Distribuzione Valori Finali"
            )
            fig_final.update_xaxes(title="Valore (€)")
            fig_final.update_yaxes(title="Frequenza")
            st.plotly_chart(fig_final, use_container_width=True)
    
    @staticmethod
    def _show_tax_charts(tax_details, final_results, lang):
        """Show tax analysis charts"""
        total_taxes = [detail['total_taxes_paid'] for detail in tax_details]
        avg_annual_taxes = [detail['average_annual_tax'] for detail in tax_details]
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_total_tax = px.histogram(
                x=total_taxes, 
                nbins=50, 
                title="Distribuzione Tasse Totali Pagate"
            )
            fig_total_tax.update_xaxes(title="Tasse Totali (€)")
            fig_total_tax.update_yaxes(title="Frequenza")
            st.plotly_chart(fig_total_tax, use_container_width=True)
        
        with col2:
            fig_annual_tax = px.histogram(
                x=avg_annual_taxes, 
                nbins=50, 
                title="Distribuzione Tasse Annuali Medie"
            )
            fig_annual_tax.update_xaxes(title="Tasse Annuali Medie (€)")
            fig_annual_tax.update_yaxes(title="Frequenza")
            st.plotly_chart(fig_annual_tax, use_container_width=True)
        
        # Scatter plot: Total taxes vs Final portfolio value
        fig_scatter = px.scatter(
            x=final_results[:len(total_taxes)],  # Ensure same length
            y=total_taxes,
            title="Relazione tra Valore Finale e Tasse Pagate",
            labels={'x': 'Valore Finale Portafoglio (€)', 'y': 'Tasse Totali Pagate (€)'}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    @staticmethod
    def _show_scenario_comparison(tax_details, final_results, lang):
        """Show scenario comparison charts"""
        st.subheader("📊 Confronto Scenari di Tassazione")
        
        total_taxes = [detail['total_taxes_paid'] for detail in tax_details]
        
        # Calculate percentiles for different metrics
        percentiles = [10, 25, 50, 75, 90]
        
        comparison_data = []
        for p in percentiles:
            final_p = np.percentile(final_results[:len(total_taxes)], p)
            tax_p = np.percentile(total_taxes, p)
            
            comparison_data.append({
                'Percentile': f"{p}°",
                'Valore Finale (€)': f"{final_p:,.0f}",
                'Tasse Pagate (€)': f"{tax_p:,.0f}",
                'Tasse/Valore Finale (%)': f"{(tax_p / final_p * 100) if final_p > 0 else 0:.2f}%"
            })
        
        st.table(pd.DataFrame(comparison_data))
        
        # Box plot comparison
        fig_box = go.Figure()
        
        fig_box.add_trace(go.Box(
            y=total_taxes,
            name="Tasse Totali (€)",
            boxmean='sd'
        ))
        
        avg_annual_taxes = [detail['average_annual_tax'] for detail in tax_details]
        fig_box.add_trace(go.Box(
            y=avg_annual_taxes,
            name="Tasse Annuali Medie (€)",
            boxmean='sd'
        ))
        
        fig_box.update_layout(
            title="Distribuzione Carichi Fiscali",
            yaxis_title="Importo (€)",
            showlegend=True
        )
        
        st.plotly_chart(fig_box, use_container_width=True)
    
    @staticmethod
    def _show_success_message(success_rate, lang):
        """Display success rate message with appropriate styling"""
        if success_rate >= 80:
            st.success(get_text('excellent_success', lang).format(success_rate))
        elif success_rate >= 60:
            st.warning(get_text('fair_success', lang).format(success_rate))
        else:
            st.error(get_text('warning_success', lang).format(success_rate))
