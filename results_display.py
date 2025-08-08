"""
Enhanced Results Display for Monte Carlo Investment Simulator
Complete implementation with tax analysis and visualization
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from translations import get_text


class ResultsDisplay:
    """Enhanced results display with comprehensive tax analysis"""
    
    @staticmethod
    def calculate_total_deposited(initial_amount, annual_contribution, years_to_retirement, 
                                adjust_contribution_inflation, inflation):
        """Calculate total amount deposited over accumulation phase"""
        total_deposited = initial_amount
        current_contribution = annual_contribution
        
        for _ in range(int(years_to_retirement)):
            total_deposited += current_contribution
            if adjust_contribution_inflation:
                current_contribution *= (1 + inflation / 100)
        
        return total_deposited
    
    @staticmethod
    def show_results(results, simulator, total_deposited, n_simulations, years_to_retirement, 
                    years_retired, capital_gains_tax_rate, withdrawal, lang):
        """Display comprehensive simulation results with enhanced tax analysis"""
        
        st.header(get_text('simulation_results', lang))
        
        # Get statistics
        stats = simulator.get_statistics()
        if not stats:
            st.error("No statistics available from simulation")
            return
        
        # Main results summary
        ResultsDisplay._show_main_summary(results, stats, total_deposited, withdrawal, lang)
        
        # Enhanced charts section
        ResultsDisplay._show_enhanced_charts(results, simulator, lang)
        
        # Detailed statistics tables
        ResultsDisplay._show_detailed_statistics(stats, lang)
        
        # Success rate analysis
        ResultsDisplay._show_success_analysis(stats['success_rate'], lang)
    
    @staticmethod
    def _show_main_summary(results, stats, total_deposited, withdrawal, lang):
        """Show main results summary"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                get_text('total_deposited', lang),
                f"€{total_deposited:,.0f}"
            )
        
        with col2:
            st.metric(
                get_text('median_accumulation', lang),
                f"€{stats['accumulation']['median']:,.0f}"
            )
        
        with col3:
            st.metric(
                get_text('median_final', lang),
                f"€{stats['final']['median']:,.0f}"
            )
        
        with col4:
            st.metric(
                get_text('success_rate', lang),
                f"{stats['success_rate']:.1f}%"
            )
        
        # Real withdrawal amount if using enhanced tax
        if 'real_withdrawal' in stats and stats['real_withdrawal']:
            st.metric(
                get_text('real_withdrawal_amount', lang),
                f"€{stats['real_withdrawal']['median']:,.0f}",
                help="Median net withdrawal amount after taxes"
            )
    
    @staticmethod
    def _show_enhanced_charts(results, simulator, lang):
        """Show enhanced charts with tax analysis"""
        st.subheader("📊 Analisi Visiva dei Risultati" if lang == 'it' else "📊 Visual Results Analysis")
        
        # Portfolio value charts
        ResultsDisplay._show_portfolio_charts(
            results['accumulation_nominal'], 
            results['accumulation'], 
            results['final'], 
            lang
        )
        
        # Tax analysis charts if available
        if simulator.use_enhanced_tax and 'tax_details' in results:
            st.markdown("---")
            st.subheader("💰 Analisi Fiscale Dettagliata" if lang == 'it' else "💰 Detailed Tax Analysis")
            ResultsDisplay._show_tax_charts(results['tax_details'], results['final'], lang)
    
    @staticmethod
    def _show_portfolio_charts(accumulation_nominal, accumulation_real, final_results, lang):
        """Show enhanced portfolio value charts"""
        col1, col2 = st.columns(2)
        
        with col1:
            # Accumulation phase chart (real values)
            fig_acc_real = px.histogram(
                x=accumulation_real, 
                nbins=50, 
                title=get_text('distribution_accumulation_real', lang)
            )
            fig_acc_real.update_xaxes(title=get_text('value_euro', lang))
            fig_acc_real.update_yaxes(title=get_text('frequency', lang))
            st.plotly_chart(fig_acc_real, use_container_width=True)
        
        with col2:
            # Final values chart
            fig_final = px.histogram(
                x=final_results, 
                nbins=50, 
                title=get_text('distribution_final', lang)
            )
            fig_final.update_xaxes(title=get_text('value_euro', lang))
            fig_final.update_yaxes(title=get_text('frequency', lang))
            st.plotly_chart(fig_final, use_container_width=True)
        
        # Additional comparison chart
        fig_comparison = go.Figure()
        fig_comparison.add_trace(go.Histogram(
            x=accumulation_real,
            name="Fine Accumulo" if lang == 'it' else "End of Accumulation",
            opacity=0.7,
            nbinsx=30
        ))
        fig_comparison.add_trace(go.Histogram(
            x=final_results,
            name="Valore Finale" if lang == 'it' else "Final Value",
            opacity=0.7,
            nbinsx=30
        ))
        
        fig_comparison.update_layout(
            title="Confronto: Accumulo vs Valore Finale" if lang == 'it' else "Comparison: Accumulation vs Final Value",
            xaxis_title=get_text('value_euro', lang),
            yaxis_title=get_text('frequency', lang),
            barmode='overlay'
        )
        
        st.plotly_chart(fig_comparison, use_container_width=True)
    
    @staticmethod
    def _show_tax_charts(tax_details, final_results, lang):
        """Enhanced tax analysis charts with multiple correlation views"""
        
        # Filter out empty tax details
        valid_tax_details = [detail for detail in tax_details if detail]
        
        if not valid_tax_details:
            st.info("Nessun dato fiscale disponibile per l'analisi" if lang == 'it' else "No tax data available for analysis")
            return
        
        # Extract data
        total_taxes = [detail['total_taxes_paid'] for detail in valid_tax_details]
        avg_annual_taxes = [detail['average_annual_tax'] for detail in valid_tax_details]
        total_contributions = [detail['total_contributions'] for detail in valid_tax_details]
        total_withdrawals = [detail['total_withdrawals'] for detail in valid_tax_details]
        total_capital_gains = [detail.get('total_capital_gains_realized', 0) for detail in valid_tax_details]
        
        # Ensure same length for all arrays
        min_length = min(len(final_results), len(total_taxes))
        final_values_aligned = final_results[:min_length]
        total_taxes_aligned = total_taxes[:min_length]
        avg_annual_taxes_aligned = avg_annual_taxes[:min_length]
        total_contributions_aligned = total_contributions[:min_length]
        total_withdrawals_aligned = total_withdrawals[:min_length]
        total_capital_gains_aligned = total_capital_gains[:min_length]
        
        # Calculate additional metrics
        effective_tax_rates = []
        tax_efficiency_scores = []
        
        for i in range(min_length):
            # Effective tax rate (taxes / total withdrawals)
            if total_withdrawals_aligned[i] > 0:
                eff_rate = (total_taxes_aligned[i] / total_withdrawals_aligned[i]) * 100
                effective_tax_rates.append(eff_rate)
            else:
                effective_tax_rates.append(0)
            
            # Tax efficiency score (final value per euro of taxes paid)
            if total_taxes_aligned[i] > 0:
                efficiency = final_values_aligned[i] / total_taxes_aligned[i]
                tax_efficiency_scores.append(efficiency)
            else:
                tax_efficiency_scores.append(final_values_aligned[i] if final_values_aligned[i] > 0 else 1000)  # High efficiency when no taxes
        
        # Primary scatter plot: Final Value vs Total Taxes
        col1, col2 = st.columns(2)
        
        with col1:
            # Create color-coded scatter plot
            fig_main_scatter = px.scatter(
                x=final_values_aligned,
                y=total_taxes_aligned,
                color=effective_tax_rates,
                title="Tasse Totali vs Valore Finale del Portafoglio" if lang == 'it' else "Total Taxes vs Final Portfolio Value",
                labels={
                    'x': 'Valore Finale Portafoglio (€)' if lang == 'it' else 'Final Portfolio Value (€)', 
                    'y': 'Tasse Totali Pagate (€)' if lang == 'it' else 'Total Taxes Paid (€)',
                    'color': 'Aliquota Effettiva (%)' if lang == 'it' else 'Effective Tax Rate (%)'
                },
                color_continuous_scale='RdYlBu_r',  # Red for high taxes, Blue for low taxes
                hover_data=['x', 'y']
            )
            
            # Add trend line
            if len(final_values_aligned) > 1:
                z = np.polyfit(final_values_aligned, total_taxes_aligned, 1)
                p = np.poly1d(z)
                x_trend = np.linspace(min(final_values_aligned), max(final_values_aligned), 100)
                y_trend = p(x_trend)
                
                fig_main_scatter.add_trace(go.Scatter(
                    x=x_trend, 
                    y=y_trend, 
                    mode='lines',
                    name='Trend Line' if lang == 'en' else 'Linea di Tendenza',
                    line=dict(color='red', dash='dash')
                ))
            
            fig_main_scatter.update_layout(
                showlegend=True,
                coloraxis_colorbar=dict(title="Aliquota (%)" if lang == 'it' else "Tax Rate (%)")
            )
            
            st.plotly_chart(fig_main_scatter, use_container_width=True)
        
        with col2:
            # Tax Efficiency Analysis
            fig_efficiency = px.scatter(
                x=total_capital_gains_aligned,
                y=tax_efficiency_scores,
                color=final_values_aligned,
                title="Efficienza Fiscale vs Capital Gains" if lang == 'it' else "Tax Efficiency vs Capital Gains",
                labels={
                    'x': 'Capital Gains Realizzati (€)' if lang == 'it' else 'Capital Gains Realized (€)',
                    'y': 'Efficienza Fiscale (€ finali / € tasse)' if lang == 'it' else 'Tax Efficiency (€ final / € taxes)',
                    'color': 'Valore Finale (€)' if lang == 'it' else 'Final Value (€)'
                },
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig_efficiency, use_container_width=True)
        
        # Secondary analysis plots
        st.subheader("📈 Analisi Dettagliata del Carico Fiscale" if lang == 'it' else "📈 Detailed Tax Burden Analysis")
        
        # Create subplot with multiple correlations
        fig_subplots = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Aliquota Effettiva vs Valore Finale" if lang == 'it' else "Effective Tax Rate vs Final Value",
                "Tasse Annuali vs Capital Gains" if lang == 'it' else "Annual Taxes vs Capital Gains", 
                "Distribuzione Efficienza Fiscale" if lang == 'it' else "Tax Efficiency Distribution",
                "Correlazione Contributi-Tasse" if lang == 'it' else "Contributions-Taxes Correlation"
            ),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Plot 1: Effective Tax Rate vs Final Value
        fig_subplots.add_trace(
            go.Scatter(
                x=final_values_aligned,
                y=effective_tax_rates,
                mode='markers',
                name='Aliquota Effettiva' if lang == 'it' else 'Effective Rate',
                marker=dict(color='blue', opacity=0.6),
                showlegend=False
            ),
            row=1, col=1
        )
        
        # Plot 2: Annual Taxes vs Capital Gains
        fig_subplots.add_trace(
            go.Scatter(
                x=total_capital_gains_aligned,
                y=avg_annual_taxes_aligned,
                mode='markers',
                name='Tasse Annuali' if lang == 'it' else 'Annual Taxes',
                marker=dict(color='red', opacity=0.6),
                showlegend=False
            ),
            row=1, col=2
        )
        
        # Plot 3: Tax Efficiency Distribution
        fig_subplots.add_trace(
            go.Histogram(
                x=tax_efficiency_scores,
                nbinsx=30,
                name='Efficienza Fiscale' if lang == 'it' else 'Tax Efficiency',
                marker=dict(color='green', opacity=0.7),
                showlegend=False
            ),
            row=2, col=1
        )
        
        # Plot 4: Contributions vs Taxes Correlation
        fig_subplots.add_trace(
            go.Scatter(
                x=total_contributions_aligned,
                y=total_taxes_aligned,
                mode='markers',
                name='Contributi-Tasse' if lang == 'it' else 'Contributions-Taxes',
                marker=dict(color='purple', opacity=0.6),
                showlegend=False
            ),
            row=2, col=2
        )
        
        # Update subplot layout
        fig_subplots.update_xaxes(title_text="Valore Finale (€)" if lang == 'it' else "Final Value (€)", row=1, col=1)
        fig_subplots.update_yaxes(title_text="Aliquota Effettiva (%)" if lang == 'it' else "Effective Tax Rate (%)", row=1, col=1)
        
        fig_subplots.update_xaxes(title_text="Capital Gains (€)" if lang == 'it' else "Capital Gains (€)", row=1, col=2)
        fig_subplots.update_yaxes(title_text="Tasse Annuali (€)" if lang == 'it' else "Annual Taxes (€)", row=1, col=2)
        
        fig_subplots.update_xaxes(title_text="Efficienza Fiscale" if lang == 'it' else "Tax Efficiency", row=2, col=1)
        fig_subplots.update_yaxes(title_text="Frequenza" if lang == 'it' else "Frequency", row=2, col=1)
        
        fig_subplots.update_xaxes(title_text="Contributi Totali (€)" if lang == 'it' else "Total Contributions (€)", row=2, col=2)
        fig_subplots.update_yaxes(title_text="Tasse Totali (€)" if lang == 'it' else "Total Taxes (€)", row=2, col=2)
        
        fig_subplots.update_layout(
            height=800, 
            title_text="Analisi Multi-Dimensionale del Carico Fiscale" if lang == 'it' else "Multi-Dimensional Tax Burden Analysis"
        )
        
        st.plotly_chart(fig_subplots, use_container_width=True)
        
        # Statistical summary table
        if len(final_values_aligned) > 1:  # Need at least 2 points for correlation
            correlation_data = {
                'Correlazione' if lang == 'it' else 'Correlation': [
                    'Valore Finale ↔ Tasse Totali' if lang == 'it' else 'Final Value ↔ Total Taxes',
                    'Capital Gains ↔ Aliquota Effettiva' if lang == 'it' else 'Capital Gains ↔ Effective Rate',
                    'Contributi ↔ Tasse' if lang == 'it' else 'Contributions ↔ Taxes',
                    'Valore Finale ↔ Efficienza Fiscale' if lang == 'it' else 'Final Value ↔ Tax Efficiency'
                ],
                'Coefficiente' if lang == 'it' else 'Coefficient': [
                    f"{np.corrcoef(final_values_aligned, total_taxes_aligned)[0,1]:.3f}",
                    f"{np.corrcoef(total_capital_gains_aligned, effective_tax_rates)[0,1]:.3f}",
                    f"{np.corrcoef(total_contributions_aligned, total_taxes_aligned)[0,1]:.3f}",
                    f"{np.corrcoef(final_values_aligned, tax_efficiency_scores)[0,1]:.3f}"
                ],
                'Interpretazione' if lang == 'it' else 'Interpretation': [
                    'Positiva (più valore = più tasse)' if lang == 'it' else 'Positive (more value = more taxes)',
                    'Variabile (dipende dal timing)' if lang == 'it' else 'Variable (timing dependent)',
                    'Positiva (più contributi = più tasse future)' if lang == 'it' else 'Positive (more contributions = more future taxes)',
                    'Negativa (più valore = meno efficienza fiscale)' if lang == 'it' else 'Negative (more value = less tax efficiency)'
                ]
            }
            
            st.subheader("🔍 Analisi Correlazioni" if lang == 'it' else "🔍 Correlation Analysis")
            st.table(pd.DataFrame(correlation_data))
        
        # Key insights
        avg_effective_rate = np.mean(effective_tax_rates)
        median_tax_efficiency = np.median(tax_efficiency_scores)
        max_taxes_scenario = np.max(total_taxes_aligned)
        min_taxes_scenario = np.min(total_taxes_aligned)
        
        st.info(f"""
        **💡 Insights Chiave dall'Analisi Fiscale:**
        - **Aliquota Effettiva Media**: {avg_effective_rate:.2f}% sui prelievi totali
        - **Efficienza Fiscale Mediana**: {median_tax_efficiency:.1f} € di valore finale per € di tasse
        - **Range Tasse Totali**: da €{min_taxes_scenario:,.0f} a €{max_taxes_scenario:,.0f}
        - **Correlazione Principale**: Portafogli con più valore finale tendono a pagare più tasse in assoluto ma possono essere più efficienti
        """ if lang == 'it' else f"""
        **💡 Key Insights from Tax Analysis:**
        - **Average Effective Rate**: {avg_effective_rate:.2f}% on total withdrawals
        - **Median Tax Efficiency**: {median_tax_efficiency:.1f} € final value per € of taxes
        - **Total Taxes Range**: from €{min_taxes_scenario:,.0f} to €{max_taxes_scenario:,.0f}
        - **Main Correlation**: Portfolios with higher final values tend to pay more taxes in absolute terms but may be more efficient
        """)
    
    @staticmethod
    def _show_detailed_statistics(stats, lang):
        """Show detailed statistics tables"""
        st.subheader("📋 Statistiche Dettagliate" if lang == 'it' else "📋 Detailed Statistics")
        
        # Create statistics table
        stat_data = []
        
        phases = [
            ('accumulation', get_text('accumulation_phase_real', lang)),
            ('final', get_text('final_values', lang))
        ]
        
        for phase_key, phase_name in phases:
            if phase_key in stats:
                phase_stats = stats[phase_key]
                stat_data.append({
                    'Fase' if lang == 'it' else 'Phase': phase_name,
                    get_text('median', lang): f"€{phase_stats['median']:,.0f}",
                    get_text('average', lang): f"€{phase_stats['mean']:,.0f}",
                    'P25': f"€{phase_stats['p25']:,.0f}",
                    'P75': f"€{phase_stats['p75']:,.0f}",
                    'P10': f"€{phase_stats['p10']:,.0f}",
                    'P90': f"€{phase_stats['p90']:,.0f}"
                })
        
        # Add tax statistics if available
        if 'tax_statistics' in stats:
            tax_stats = stats['tax_statistics']
            
            stat_data.append({
                'Fase' if lang == 'it' else 'Phase': 'Tasse Totali' if lang == 'it' else 'Total Taxes',
                get_text('median', lang): f"€{tax_stats['total_taxes_paid']['median']:,.0f}",
                get_text('average', lang): f"€{tax_stats['total_taxes_paid']['mean']:,.0f}",
                'P25': f"€{tax_stats['total_taxes_paid']['p25']:,.0f}",
                'P75': f"€{tax_stats['total_taxes_paid']['p75']:,.0f}",
                'P10': '-',
                'P90': '-'
            })
            
            stat_data.append({
                'Fase' if lang == 'it' else 'Phase': 'Tasse Annuali Medie' if lang == 'it' else 'Average Annual Taxes',
                get_text('median', lang): f"€{tax_stats['average_annual_tax']['median']:,.0f}",
                get_text('average', lang): f"€{tax_stats['average_annual_tax']['mean']:,.0f}",
                'P25': f"€{tax_stats['average_annual_tax']['p25']:,.0f}",
                'P75': f"€{tax_stats['average_annual_tax']['p75']:,.0f}",
                'P10': '-',
                'P90': '-'
            })
        
        st.table(pd.DataFrame(stat_data))
    
    @staticmethod
    def _show_success_analysis(success_rate, lang):
        """Show success rate analysis with context"""
        st.subheader("✅ Analisi Tasso di Successo" if lang == 'it' else "✅ Success Rate Analysis")
        
        # Success message based on rate
        if success_rate >= 85:
            st.success(get_text('excellent_success', lang).format(success_rate))
        elif success_rate >= 60:
            st.warning(get_text('fair_success', lang).format(success_rate))
        else:
            st.error(get_text('warning_success', lang).format(success_rate))
        
        # Create success rate gauge chart
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = success_rate,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Tasso di Successo (%)" if lang == 'it' else "Success Rate (%)"},
            delta = {'reference': 75, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 75], 'color': "gray"},
                    {'range': [75, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig_gauge.update_layout(height=400)
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Interpretation guide
        with st.expander("📚 Guida all'Interpretazione" if lang == 'it' else "📚 Interpretation Guide"):
            if lang == 'it':
                st.markdown("""
                **Come interpretare il tasso di successo:**
                
                - **90-100%**: Eccellente! Il piano ha altissime probabilità di successo
                - **75-89%**: Molto buono. Il piano è solido con buone probabilità di successo  
                - **60-74%**: Discreto. Potresti voler considerare aggiustamenti al piano
                - **40-59%**: Rischio moderato. Consigliabile rivedere strategia e parametri
                - **0-39%**: Alto rischio. Il piano necessita di modifiche sostanziali
                
                **Fattori che influenzano il successo:**
                - Allocazione degli asset (più azionario = più crescita ma più volatilità)
                - Durata dell'accumulo (più tempo = maggiori probabilità)
                - Importo dei prelievi (prelievi più alti = maggior rischio)
                - Livello di inflazione e tasse
                """)
            else:
                st.markdown("""
                **How to interpret the success rate:**
                
                - **90-100%**: Excellent! The plan has very high probability of success
                - **75-89%**: Very good. The plan is solid with good success probability
                - **60-74%**: Fair. You might want to consider plan adjustments
                - **40-59%**: Moderate risk. Advisable to review strategy and parameters  
                - **0-39%**: High risk. The plan needs substantial modifications
                
                **Factors influencing success:**
                - Asset allocation (more equity = more growth but more volatility)
                - Accumulation duration (more time = higher probability)
                - Withdrawal amount (higher withdrawals = greater risk)
                - Inflation level and taxes
                """)
