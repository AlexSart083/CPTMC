"""
Enhanced scatter plots for tax analysis - replacement for distribution charts
Add this code to results_display.py in the _show_enhanced_charts method
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd

@staticmethod
def _show_portfolio_charts(accumulation_nominal, accumulation_real, final_results, lang):
    """Show enhanced portfolio value charts with tax correlation analysis"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Traditional accumulation chart
        fig_acc_real = px.histogram(
            x=accumulation_real, 
            nbins=50, 
            title="Distribuzione Valori Accumulo (Reale)" if lang == 'it' else "Accumulation Values Distribution (Real)"
        )
        fig_acc_real.update_xaxes(title="Valore (€)" if lang == 'it' else "Value (€)")
        fig_acc_real.update_yaxes(title="Frequenza" if lang == 'it' else "Frequency")
        st.plotly_chart(fig_acc_real, use_container_width=True)
    
    with col2:
        # Enhanced final values chart
        fig_final = px.histogram(
            x=final_results, 
            nbins=50, 
            title="Distribuzione Valori Finali" if lang == 'it' else "Final Values Distribution"
        )
        fig_final.update_xaxes(title="Valore (€)" if lang == 'it' else "Value (€)")
        fig_final.update_yaxes(title="Frequenza" if lang == 'it' else "Frequency")
        st.plotly_chart(fig_final, use_container_width=True)

@staticmethod
def _show_tax_charts(tax_details, final_results, lang):
    """Enhanced tax analysis charts with multiple correlation views"""
    
    # Extract data
    total_taxes = [detail['total_taxes_paid'] for detail in tax_details]
    avg_annual_taxes = [detail['average_annual_tax'] for detail in tax_details]
    total_contributions = [detail['total_contributions'] for detail in tax_details]
    total_withdrawals = [detail['total_withdrawals'] for detail in tax_details]
    total_capital_gains = [detail.get('total_capital_gains_realized', 0) for detail in tax_details]
    
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
            tax_efficiency_scores.append(final_values_aligned[i])  # No taxes = infinite efficiency
    
    # Create comprehensive scatter plot analysis
    st.subheader("📊 Analisi Correlazione Fiscale Avanzata" if lang == 'it' else "📊 Advanced Tax Correlation Analysis")
    
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
    
    fig_subplots.update_layout(height=800, title_text="Analisi Multi-Dimensionale del Carico Fiscale" if lang == 'it' else "Multi-Dimensional Tax Burden Analysis")
    
    st.plotly_chart(fig_subplots, use_container_width=True)
    
    # Statistical summary table
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
