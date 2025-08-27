"""
Enhanced results display components with CORRECTED REAL withdrawal support, detailed withdrawal analysis, and integrated VaR/CVaR risk metrics
COMPLETE FILE - Corretti tutti i calcoli dei prelievi + integrato VaR/CVaR direttamente nell'app
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from translations import get_text


class ResultsDisplay:
    """Enhanced display of simulation results with CORRECTED REAL withdrawal analysis and integrated VaR/CVaR metrics"""
    
    @staticmethod
    def calculate_var(values, confidence_level=0.95):
        """Calculate Value at Risk (VaR) at specified confidence level"""
        if not values or len(values) == 0:
            return 0.0
        values_array = np.array(values)
        percentile = (1 - confidence_level) * 100
        return np.percentile(values_array, percentile)
    
    @staticmethod
    def calculate_cvar(values, confidence_level=0.95):
        """Calculate Conditional Value at Risk (CVaR) at specified confidence level"""
        if not values or len(values) == 0:
            return 0.0
        var_value = ResultsDisplay.calculate_var(values, confidence_level)
        values_array = np.array(values)
        tail_values = values_array[values_array <= var_value]
        return np.mean(tail_values) if len(tail_values) > 0 else var_value
    
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
            total_deposited = initial_amount
            current_contribution = annual_contribution
            for year in range(int(years_to_retirement)):
                total_deposited += current_contribution
                current_contribution *= (1 + inflation / 100)
        else:
            total_deposited = initial_amount + (annual_contribution * years_to_retirement)
        return total_deposited
    
    @staticmethod
    def show_results(results, simulator, total_deposited, n_simulations, years_to_retirement, 
                    years_retired, capital_gains_tax_rate, nominal_withdrawal, inflation_rate, 
                    use_real_withdrawal, lang):
        """Display simulation results with CORRECTED REAL withdrawal analysis and integrated VaR/CVaR"""
        st.markdown("---")
        st.header(get_text('simulation_results', lang))
        
        accumulation_balances = results['accumulation']
        accumulation_balances_nominal = results['accumulation_nominal']
        final_results = results['final']
        
        # Calculate final results in real terms
        inflation_decimal = inflation_rate / 100 if inflation_rate > 1 else inflation_rate
        total_inflation_factor = (1 + inflation_decimal) ** (years_to_retirement + years_retired)
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
        
        # Display all sections
        ResultsDisplay._show_key_metrics_with_withdrawal_info(
            total_deposited, stats['accumulation_nominal']['median'], 
            stats['final']['median'], stats['success_rate'], 
            nominal_withdrawal, use_real_withdrawal, inflation_rate, years_to_retirement, years_retired, lang
        )
        
        ResultsDisplay._show_detailed_withdrawal_analysis(
            results, nominal_withdrawal, use_real_withdrawal, inflation_rate, years_to_retirement, years_retired, lang
        )
        
        ResultsDisplay._show_simplified_tax_analysis(
            results, total_deposited, nominal_withdrawal, capital_gains_tax_rate, lang
        )
        
        ResultsDisplay._show_enhanced_detailed_statistics(
            stats, years_to_retirement, years_retired, total_deposited, inflation_rate, lang
        )
        
        ResultsDisplay._show_enhanced_charts_with_scatter(
            accumulation_balances_nominal, accumulation_balances, 
            final_results, final_results_real, lang
        )
        
        # NEW: VaR/CVaR Analysis
        ResultsDisplay._show_integrated_var_cvar_analysis(
            results, total_deposited, lang
        )
        
        ResultsDisplay._show_success_message(stats['success_rate'], lang)
    
    @staticmethod
    def _show_key_metrics_with_withdrawal_info(total_deposited, median_accumulation, median_final, 
                                             success_rate, nominal_withdrawal, use_real_withdrawal, 
                                             inflation_rate, years_to_retirement, years_retired, lang):
        """Show key metrics with withdrawal information"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(get_text('total_deposited', lang), f"€{total_deposited:,.0f}")
        
        with col2:
            st.metric(get_text('median_accumulation', lang), f"€{median_accumulation:,.0f}")
        
        with col3:
            st.metric(get_text('median_final', lang), f"€{median_final:,.0f}")
        
        with col4:
            st.metric(get_text('success_rate', lang), f"{success_rate:.1f}%")
        
        # NEW: Show withdrawal information
        st.markdown("---")
        if use_real_withdrawal:
            # Calculate real withdrawal progression
            inflation_decimal = inflation_rate / 100 if inflation_rate > 1 else inflation_rate
            first_retirement_withdrawal = nominal_withdrawal * ((1 + inflation_decimal) ** years_to_retirement)
            final_withdrawal = nominal_withdrawal * ((1 + inflation_decimal) ** (years_to_retirement + years_retired - 1))
            
            st.info(f"💰 **" + get_text('real_withdrawal_amount_result', lang) + f"**: €{nominal_withdrawal:,.0f} " +
                   ("(potere d'acquisto di oggi)" if lang == 'it' else "(today's purchasing power)"))
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    ("Primo prelievo (al pensionamento)" if lang == 'it' else "First withdrawal (at retirement)"),
                    f"€{first_retirement_withdrawal:,.0f}",
                    help=("Aggiustato per inflazione durante accumulo" if lang == 'it' else "Adjusted for inflation during accumulation")
                )
            
            with col2:
                st.metric(
                    ("Ultimo prelievo (fine pensione)" if lang == 'it' else "Final withdrawal (end of retirement)"),
                    f"€{final_withdrawal:,.0f}",
                    help=("Aggiustato per inflazione totale" if lang == 'it' else "Adjusted for total inflation")
                )
        else:
            st.warning(f"⚠️ **" + ("Prelievo Nominale" if lang == 'it' else "Nominal Withdrawal") + f"**: €{nominal_withdrawal:,.0f} " +
                      ("(importo fisso, potere d'acquisto diminuisce)" if lang == 'it' else "(fixed amount, purchasing power decreases)"))
    
    @staticmethod
    def _show_detailed_withdrawal_analysis(results, nominal_withdrawal, use_real_withdrawal, 
                                         inflation_rate, years_to_retirement, years_retired, lang):
        """Show detailed withdrawal analysis"""
        st.markdown("---")
        st.subheader("💸 " + ("Analisi Dettagliata Prelievi" if lang == 'it' else "Detailed Withdrawal Analysis"))
        
        # Get withdrawal data from results if available
        if 'real_withdrawal' in results:
            real_withdrawal_amounts = results['real_withdrawal']
            avg_real_withdrawal = np.mean(real_withdrawal_amounts)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    ("Prelievo Medio Effettivo (dopo tasse)" if lang == 'it' else "Average Effective Withdrawal (after taxes)"),
                    f"€{avg_real_withdrawal:,.0f}",
                    help=("Media dei prelievi netti nelle simulazioni" if lang == 'it' else "Average of net withdrawals across simulations")
                )
            
            with col2:
                if use_real_withdrawal:
                    effectiveness = (avg_real_withdrawal / nominal_withdrawal * 100) if nominal_withdrawal > 0 else 0
                    st.metric(
                        ("Efficacia Prelievo" if lang == 'it' else "Withdrawal Effectiveness"),
                        f"{effectiveness:.1f}%",
                        help=("% del prelievo desiderato effettivamente ottenuto" if lang == 'it' else "% of desired withdrawal actually obtained")
                    )
        
        # Show withdrawal progression over time (theoretical)
        if use_real_withdrawal:
            st.markdown("**" + ("Progressione Prelievi Reali nel Tempo:" if lang == 'it' else "Real Withdrawal Progression Over Time:") + "**")
            
            inflation_decimal = inflation_rate / 100 if inflation_rate > 1 else inflation_rate
            
            # Calculate withdrawal amounts for key years
            withdrawal_data = []
            key_years = [0, 5, 10, 15, 20, min(25, int(years_retired))]
            
            for year in key_years:
                if year < years_retired:
                    total_years = years_to_retirement + year
                    withdrawal_amount = nominal_withdrawal * ((1 + inflation_decimal) ** total_years)
                    
                    withdrawal_data.append({
                        ('Anno Pensione' if lang == 'it' else 'Retirement Year'): year + 1,
                        ('Prelievo Nominale (€)' if lang == 'it' else 'Nominal Withdrawal (€)'): f"€{withdrawal_amount:,.0f}",
                        ('Potere Acquisto Oggi (€)' if lang == 'it' else 'Today\'s Purchasing Power (€)'): f"€{nominal_withdrawal:,.0f}"
                    })
            
            if withdrawal_data:
                df_withdrawal = pd.DataFrame(withdrawal_data)
                st.dataframe(df_withdrawal, use_container_width=True)
        
        else:
            st.info("ℹ️ " + ("Prelievo nominale: €{:,.0f} ogni anno (il potere d'acquisto diminuisce del {:.1f}% annuo)" if lang == 'it' 
                            else "Nominal withdrawal: €{:,.0f} every year (purchasing power decreases by {:.1f}% annually)").format(
                                nominal_withdrawal, inflation_rate))
    
    @staticmethod
    def _show_simplified_tax_analysis(results, total_deposited, nominal_withdrawal, capital_gains_tax_rate, lang):
        """Show simplified tax analysis"""
        if 'tax_details' not in results:
            return
        
        st.markdown("---")
        st.subheader("💰 " + ("Analisi Fiscale Semplificata" if lang == 'it' else "Simplified Tax Analysis"))
        
        tax_analysis = None
        try:
            # Get tax analysis from simulator if available
            if hasattr(results, 'get_tax_analysis'):
                tax_analysis = results.get_tax_analysis()
        except:
            pass
        
        # Display basic tax information
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                ("Aliquota Capital Gains" if lang == 'it' else "Capital Gains Tax Rate"),
                f"{capital_gains_tax_rate:.1f}%"
            )
        
        with col2:
            # Estimate effective tax rate
            if tax_analysis and 'effective_tax_rate_statistics' in tax_analysis:
                avg_effective_rate = tax_analysis['effective_tax_rate_statistics']['mean']
                st.metric(
                    ("Aliquota Effettiva Media" if lang == 'it' else "Average Effective Tax Rate"),
                    f"{avg_effective_rate:.2f}%",
                    help=("Aliquota media effettiva sui prelievi" if lang == 'it' else "Average effective rate on withdrawals")
                )
            else:
                st.info("📊 " + ("Analisi fiscale dettagliata non disponibile" if lang == 'it' else "Detailed tax analysis not available"))
        
        # Tax explanation
        with st.expander("ℹ️ " + ("Come Funziona la Tassazione" if lang == 'it' else "How Taxation Works")):
            if lang == 'it':
                st.markdown(f"""
                **🏛️ Meccanismo di Tassazione Capital Gains:**
                
                1. **Solo i guadagni vengono tassati** al {capital_gains_tax_rate:.1f}%
                2. **Il capitale iniziale non è tassato** (è già stato tassato quando guadagnato)
                3. **Metodo proporzionale**: quando prelevi, una parte è capitale originale (non tassato) e una parte è guadagno (tassato)
                4. **Tassazione effettiva** dipende da quanto è cresciuto il portafoglio
                
                **Esempio**: Se il tuo portafoglio vale €200.000 e hai depositato €100.000:
                - 50% è capitale originale (non tassato)
                - 50% sono guadagni (tassati al {capital_gains_tax_rate:.1f}%)
                - Su un prelievo di €10.000: €5.000 non tassati + €5.000 tassati = circa €{10000 * (1 - capital_gains_tax_rate/100 * 0.5):,.0f} netti
                """)
            else:
                st.markdown(f"""
                **🏛️ Capital Gains Taxation Mechanism:**
                
                1. **Only gains are taxed** at {capital_gains_tax_rate:.1f}%
                2. **Original capital is not taxed** (already taxed when earned)
                3. **Proportional method**: when you withdraw, part is original capital (not taxed) and part is gain (taxed)
                4. **Effective taxation** depends on how much the portfolio has grown
                
                **Example**: If your portfolio is worth €200,000 and you deposited €100,000:
                - 50% is original capital (not taxed)
                - 50% are gains (taxed at {capital_gains_tax_rate:.1f}%)
                - On a €10,000 withdrawal: €5,000 not taxed + €5,000 taxed = about €{10000 * (1 - capital_gains_tax_rate/100 * 0.5):,.0f} net
                """)
    
    @staticmethod
    def _show_enhanced_detailed_statistics(stats, years_to_retirement, years_retired, total_deposited, inflation_rate, lang):
        """Show enhanced detailed statistics"""
        st.markdown("---")
        st.subheader("📊 " + ("Statistiche Dettagliate" if lang == 'it' else "Detailed Statistics"))
        
        # Create tabs for different statistics
        tab1, tab2, tab3 = st.tabs([
            get_text('accumulation_phase_real', lang),
            get_text('final_values', lang),
            "📈 " + ("CAGR & Performance" if lang == 'en' else "CAGR & Performance")
        ])
        
        with tab1:
            ResultsDisplay._show_phase_statistics(stats, 'accumulation', years_to_retirement, total_deposited, lang)
        
        with tab2:
            ResultsDisplay._show_phase_statistics(stats, 'final', years_to_retirement + years_retired, total_deposited, lang)
            
            # Also show real final values if available
            if 'final_real' in stats:
                st.markdown("**" + ("Valori Finali (Potere d'Acquisto Oggi)" if lang == 'it' else "Final Values (Today's Purchasing Power)") + "**")
                ResultsDisplay._show_phase_statistics(stats, 'final_real', years_to_retirement + years_retired, total_deposited, lang)
        
        with tab3:
            ResultsDisplay._show_performance_statistics(stats, years_to_retirement, years_retired, total_deposited, lang)
    
    @staticmethod
    def _show_phase_statistics(stats, phase, years, total_deposited, lang):
        """Show statistics for a specific phase"""
        if phase not in stats:
            st.warning(f"⚠️ " + ("Dati non disponibili per" if lang == 'it' else "Data not available for") + f" {phase}")
            return
        
        phase_stats = stats[phase]
        
        # Create percentile table
        percentiles_data = []
        percentiles = [
            ('p10', '10%'),
            ('p25', '25%'),
            ('median', '50%'),
            ('mean', get_text('average', lang)),
            ('p75', '75%'),
            ('p90', '90%')
        ]
        
        for key, label in percentiles:
            if key in phase_stats:
                value = phase_stats[key]
                cagr = ResultsDisplay.calculate_cagr(value, total_deposited, years) if years > 0 else 0
                
                percentiles_data.append({
                    get_text('percentile', lang): label,
                    get_text('value_euro', lang): f"€{value:,.0f}",
                    get_text('cagr_percent', lang): f"{cagr:.2f}%"
                })
        
        if percentiles_data:
            df_percentiles = pd.DataFrame(percentiles_data)
            st.dataframe(df_percentiles, use_container_width=True)
        
        # Additional insights
        if phase == 'final':
            success_rate = stats.get('success_rate', 0)
            if success_rate < 50:
                st.error(f"⚠️ " + ("Basso tasso di successo" if lang == 'it' else "Low success rate") + f": {success_rate:.1f}%")
            elif success_rate < 80:
                st.warning(f"📊 " + ("Tasso di successo moderato" if lang == 'it' else "Moderate success rate") + f": {success_rate:.1f}%")
            else:
                st.success(f"✅ " + ("Buon tasso di successo" if lang == 'it' else "Good success rate") + f": {success_rate:.1f}%")
    
    @staticmethod
    def _show_performance_statistics(stats, years_to_retirement, years_retired, total_deposited, lang):
        """Show performance and CAGR statistics"""
        if 'accumulation' not in stats or 'final' not in stats:
            st.warning("⚠️ " + ("Dati insufficienti per analisi performance" if lang == 'it' else "Insufficient data for performance analysis"))
            return
        
        acc_stats = stats['accumulation']
        final_stats = stats['final']
        
        # Calculate CAGRs
        acc_cagr = ResultsDisplay.calculate_cagr(acc_stats['median'], total_deposited, years_to_retirement)
        total_cagr = ResultsDisplay.calculate_cagr(final_stats['median'], total_deposited, years_to_retirement + years_retired)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                ("CAGR Fase Accumulo" if lang == 'it' else "Accumulation Phase CAGR"),
                f"{acc_cagr:.2f}%",
                help=("Crescita annua composta durante accumulo" if lang == 'it' else "Compound annual growth during accumulation")
            )
        
        with col2:
            st.metric(
                ("CAGR Totale" if lang == 'it' else "Total CAGR"),
                f"{total_cagr:.2f}%",
                help=("Crescita annua composta su tutto il periodo" if lang == 'it' else "Compound annual growth over entire period")
            )
        
        with col3:
            # Calculate multiple on deposited amount
            multiple = final_stats['median'] / total_deposited if total_deposited > 0 else 0
            st.metric(
                ("Moltiplicatore" if lang == 'it' else "Multiplier"),
                f"{multiple:.1f}x",
                help=("Quante volte il capitale iniziale" if lang == 'it' else "Multiple of initial capital")
            )
        
        # Performance insights
        if acc_cagr > 7:
            st.success("🚀 " + ("Eccellente crescita durante accumulo" if lang == 'it' else "Excellent growth during accumulation"))
        elif acc_cagr > 5:
            st.info("📈 " + ("Buona crescita durante accumulo" if lang == 'it' else "Good growth during accumulation"))
        elif acc_cagr > 3:
            st.warning("📊 " + ("Crescita moderata durante accumulo" if lang == 'it' else "Moderate growth during accumulation"))
        else:
            st.error("📉 " + ("Crescita bassa durante accumulo" if lang == 'it' else "Low growth during accumulation"))
    
    @staticmethod
    def _show_enhanced_charts_with_scatter(accumulation_nominal, accumulation_real, final_nominal, final_real, lang):
        """Show enhanced charts including scatter plots"""
        st.markdown("---")
        st.header(get_text('distribution_charts_title', lang))
        
        # Create tabs for different chart types
        tab1, tab2, tab3 = st.tabs([
            get_text('distributions_tab', lang),
            get_text('correlations_tab', lang),
            get_text('comparison_tab', lang)
        ])
        
        with tab1:
            ResultsDisplay._show_distribution_charts(accumulation_nominal, accumulation_real, final_nominal, final_real, lang)
        
        with tab2:
            ResultsDisplay._show_correlation_charts(accumulation_nominal, final_nominal, lang)
        
        with tab3:
            ResultsDisplay._show_comparison_charts(final_nominal, final_real, lang)
    
    @staticmethod
    def _show_distribution_charts(accumulation_nominal, accumulation_real, final_nominal, final_real, lang):
        """Show distribution histograms"""
        col1, col2 = st.columns(2)
        
        with col1:
            # Accumulation distributions
            fig_acc = go.Figure()
            
            fig_acc.add_trace(go.Histogram(
                x=accumulation_nominal,
                name=get_text('accumulation_nominal_dist', lang),
                opacity=0.7,
                nbinsx=30,
                marker_color='lightblue'
            ))
            
            fig_acc.add_trace(go.Histogram(
                x=accumulation_real,
                name=get_text('accumulation_real_dist', lang),
                opacity=0.7,
                nbinsx=30,
                marker_color='orange'
            ))
            
            fig_acc.update_layout(
                title=get_text('distribution_accumulation', lang),
                xaxis_title=get_text('value_euro', lang),
                yaxis_title=get_text('frequency', lang),
                barmode='overlay',
                height=400
            )
            
            st.plotly_chart(fig_acc, use_container_width=True)
        
        with col2:
            # Final distributions
            fig_final = go.Figure()
            
            fig_final.add_trace(go.Histogram(
                x=final_nominal,
                name=get_text('final_nominal_dist', lang),
                opacity=0.7,
                nbinsx=30,
                marker_color='lightgreen'
            ))
            
            fig_final.add_trace(go.Histogram(
                x=final_real,
                name=get_text('final_real_dist', lang),
                opacity=0.7,
                nbinsx=30,
                marker_color='red'
            ))
            
            fig_final.update_layout(
                title=get_text('distribution_final', lang),
                xaxis_title=get_text('value_euro', lang),
                yaxis_title=get_text('frequency', lang),
                barmode='overlay',
                height=400
            )
            
            st.plotly_chart(fig_final, use_container_width=True)
    
    @staticmethod
    def _show_correlation_charts(accumulation_nominal, final_nominal, lang):
        """Show correlation scatter plots"""
        col1, col2 = st.columns(2)
        
        with col1:
            # Accumulation vs Final scatter plot
            fig_scatter = px.scatter(
                x=accumulation_nominal,
                y=final_nominal,
                title=get_text('accumulation_final_correlation', lang),
                labels={'x': get_text('accumulation_phase_nominal', lang), 'y': get_text('final_values', lang)},
                opacity=0.6,
                height=400
            )
            
            # Add correlation coefficient
            correlation = np.corrcoef(accumulation_nominal, final_nominal)[0, 1]
            fig_scatter.add_annotation(
                x=0.05, y=0.95,
                xref="paper", yref="paper",
                text=f"{get_text('correlation_label', lang)}: {correlation:.3f}",
                showarrow=False,
                bgcolor="rgba(255,255,255,0.8)"
            )
            
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        with col2:
            # Heat map (simplified)
            fig_heatmap = px.density_heatmap(
                x=accumulation_nominal,
                y=final_nominal,
                title=get_text('accumulation_final_heatmap', lang),
                labels={'x': get_text('accumulation_phase_nominal', lang), 'y': get_text('final_values', lang)},
                height=400
            )
            
            st.plotly_chart(fig_heatmap, use_container_width=True)
    
    @staticmethod
    def _show_comparison_charts(final_nominal, final_real, lang):
        """Show nominal vs real comparison charts"""
        col1, col2 = st.columns(2)
        
        with col1:
            # Final values comparison scatter plot
            fig_comparison = px.scatter(
                x=final_real,
                y=final_nominal,
                title=get_text('final_values_comparison', lang),
                labels={'x': get_text('final_real_dist', lang), 'y': get_text('final_nominal_dist', lang)},
                opacity=0.6,
                height=400
            )
            
            # Add 1:1 line
            min_val = min(min(final_real), min(final_nominal))
            max_val = max(max(final_real), max(final_nominal))
            fig_comparison.add_trace(go.Scatter(
                x=[min_val, max_val],
                y=[min_val, max_val],
                mode='lines',
                name=get_text('one_to_one_line', lang),
                line=dict(dash='dash', color='red')
            ))
            
            # Add correlation
            correlation = np.corrcoef(final_real, final_nominal)[0, 1]
            fig_comparison.add_annotation(
                x=0.05, y=0.95,
                xref="paper", yref="paper",
                text=f"{get_text('correlation_label', lang)}: {correlation:.3f}",
                showarrow=False,
                bgcolor="rgba(255,255,255,0.8)"
            )
            
            st.plotly_chart(fig_comparison, use_container_width=True)
        
        with col2:
            # Inflation impact analysis
            avg_real = np.mean(final_real)
            avg_nominal = np.mean(final_nominal)
            inflation_impact = (avg_real / avg_nominal * 100) if avg_nominal > 0 else 0
            
            st.metric(
                get_text('inflation_impact_label', lang),
                f"{inflation_impact:.1f}%",
                help=get_text('inflation_impact_text', lang).format(inflation_impact)
            )
            
            # Box plot comparison
            fig_box = go.Figure()
            
            fig_box.add_trace(go.Box(
                y=final_nominal,
                name=get_text('final_nominal_dist', lang),
                boxpoints='outliers'
            ))
            
            fig_box.add_trace(go.Box(
                y=final_real,
                name=get_text('final_real_dist', lang),
                boxpoints='outliers'
            ))
            
            fig_box.update_layout(
                title=get_text('final_values_correlation', lang),
                yaxis_title=get_text('value_euro', lang),
                height=400
            )
            
            st.plotly_chart(fig_box, use_container_width=True)
    
    @staticmethod
    def _show_integrated_var_cvar_analysis(results, total_deposited, lang):
        """Display integrated VaR/CVaR risk analysis directly in the app"""
        st.markdown("---")
        st.header("⚡ " + ("Analisi del Rischio (VaR & CVaR)" if lang == 'it' else "Risk Analysis (VaR & CVaR)"))
        
        # Risk explanation
        with st.expander("ℹ️ " + ("Cosa sono VaR e CVaR?" if lang == 'it' else "What are VaR and CVaR?"), expanded=False):
            if lang == 'it':
                st.markdown("""
                **📊 Value at Risk (VaR) al 5%:**
                - Indica il valore minimo che il tuo portafoglio raggiungerà nel 95% dei casi
                - Es: VaR 5% = €50.000 significa che solo nel 5% dei casi peggiori il portafoglio varrà meno di €50.000
                
                **📉 Conditional Value at Risk (CVaR) al 5%:**
                - È il valore medio del portafoglio nei peggiori 5% degli scenari
                - Es: CVaR 5% = €30.000 significa che quando le cose vanno davvero male, il portafoglio vale in media €30.000
                
                **🎯 Perché sono importanti:**
                - Aiutano a comprendere i rischi estremi del tuo piano di investimento
                - CVaR è sempre ≤ VaR e mostra quanto possono essere gravi le perdite estreme
                - Utili per valutare se puoi tollerare gli scenari peggiori
                """)
            else:
                st.markdown("""
                **📊 Value at Risk (VaR) at 5%:**
                - Indicates the minimum value your portfolio will reach in 95% of cases
                - Ex: VaR 5% = €50,000 means that only in the worst 5% of cases will the portfolio be worth less than €50,000
                
                **📉 Conditional Value at Risk (CVaR) at 5%:**
                - Is the average portfolio value in the worst 5% of scenarios
                - Ex: CVaR 5% = €30,000 means when things go really bad, the portfolio averages €30,000
                
                **🎯 Why they matter:**
                - Help understand extreme risks of your investment plan
                - CVaR is always ≤ VaR and shows how severe extreme losses can be
                - Useful for assessing whether you can tolerate worst-case scenarios
                """)
        
        # Calculate VaR and CVaR for different phases
        phases_data = {}
        
        if 'accumulation_nominal' in results:
            acc_nom_var5 = ResultsDisplay.calculate_var(results['accumulation_nominal'], 0.95)
            acc_nom_cvar5 = ResultsDisplay.calculate_cvar(results['accumulation_nominal'], 0.95)
            phases_data['accumulation_nominal'] = {
                'name': 'Accumulo (Nominale)' if lang == 'it' else 'Accumulation (Nominal)',
                'var5': acc_nom_var5,
                'cvar5': acc_nom_cvar5,
                'mean': np.mean(results['accumulation_nominal'])
            }
        
        if 'accumulation' in results:
            acc_real_var5 = ResultsDisplay.calculate_var(results['accumulation'], 0.95)
            acc_real_cvar5 = ResultsDisplay.calculate_cvar(results['accumulation'], 0.95)
            phases_data['accumulation_real'] = {
                'name': 'Accumulo (Reale)' if lang == 'it' else 'Accumulation (Real)',
                'var5': acc_real_var5,
                'cvar5': acc_real_cvar5,
                'mean': np.mean(results['accumulation'])
            }
        
        if 'final' in results:
            final_var5 = ResultsDisplay.calculate_var(results['final'], 0.95)
            final_cvar5 = ResultsDisplay.calculate_cvar(results['final'], 0.95)
            final_mean = np.mean(results['final'])
            phases_data['final'] = {
                'name': 'Finale' if lang == 'it' else 'Final',
                'var5': final_var5,
                'cvar5': final_cvar5,
                'mean': final_mean
            }
        
        if not phases_data:
            st.warning("⚠️ " + ("Dati insufficienti per l'analisi VaR/CVaR" if lang == 'it' else "Insufficient data for VaR/CVaR analysis"))
            return
        
        # Display key metrics for ACCUMULATION NOMINAL values (most important for retirement planning)
        if 'accumulation_nominal' in phases_data:
            accumulation_nominal_data = phases_data['accumulation_nominal']
            st.subheader("🎯 " + ("Metriche di Rischio Chiave (Fine Accumulo - Nominale)" if lang == 'it' else "Key Risk Metrics (End of Accumulation - Nominal)"))
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="📊 VaR 5%",
                    value=f"€{accumulation_nominal_data['var5']:,.0f}",
                    help="Valore nominale minimo al pensionamento nel 95% dei casi" if lang == 'it' else "Minimum nominal value at retirement in 95% of cases"
                )
            
            with col2:
                st.metric(
                    label="📉 CVaR 5%", 
                    value=f"€{accumulation_nominal_data['cvar5']:,.0f}",
                    help="Valore nominale medio al pensionamento nei peggiori 5% dei casi" if lang == 'it' else "Average nominal value at retirement in worst 5% of cases"
                )
            
            with col3:
                st.metric(
                    label="📈 " + ("Media" if lang == 'it' else "Mean"),
                    value=f"€{accumulation_nominal_data['mean']:,.0f}",
                    help="Valore nominale medio al pensionamento" if lang == 'it' else "Average nominal value at retirement"
                )
            
            with col4:
                risk_gap = accumulation_nominal_data['mean'] - accumulation_nominal_data['cvar5'] if accumulation_nominal_data['cvar5'] < accumulation_nominal_data['mean'] else 0
                st.metric(
                    label="⚡ " + ("Gap di Rischio" if lang == 'it' else "Risk Gap"),
                    value=f"€{risk_gap:,.0f}",
                    help="Differenza tra media e CVaR 5%" if lang == 'it' else "Difference between mean and CVaR 5%"
                )
            
            # Risk level assessment based on accumulation nominal values
            ResultsDisplay._assess_risk_level(accumulation_nominal_data, total_deposited, lang)
        elif 'accumulation' in phases_data:
            # Fallback to real accumulation values if nominal not available
            accumulation_data = phases_data['accumulation']
            st.subheader("🎯 " + ("Metriche di Rischio Chiave (Fine Accumulo - Reale)" if lang == 'it' else "Key Risk Metrics (End of Accumulation - Real)"))
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="📊 VaR 5%",
                    value=f"€{accumulation_data['var5']:,.0f}",
                    help="Valore reale minimo al pensionamento nel 95% dei casi" if lang == 'it' else "Minimum real value at retirement in 95% of cases"
                )
            
            with col2:
                st.metric(
                    label="📉 CVaR 5%", 
                    value=f"€{accumulation_data['cvar5']:,.0f}",
                    help="Valore reale medio al pensionamento nei peggiori 5% dei casi" if lang == 'it' else "Average real value at retirement in worst 5% of cases"
                )
            
            with col3:
                st.metric(
                    label="📈 " + ("Media" if lang == 'it' else "Mean"),
                    value=f"€{accumulation_data['mean']:,.0f}",
                    help="Valore reale medio al pensionamento" if lang == 'it' else "Average real value at retirement"
                )
            
            with col4:
                risk_gap = accumulation_data['mean'] - accumulation_data['cvar5'] if accumulation_data['cvar5'] < accumulation_data['mean'] else 0
                st.metric(
                    label="⚡ " + ("Gap di Rischio" if lang == 'it' else "Risk Gap"),
                    value=f"€{risk_gap:,.0f}",
                    help="Differenza tra media e CVaR 5%" if lang == 'it' else "Difference between mean and CVaR 5%"
                )
            
            # Risk level assessment
            ResultsDisplay._assess_risk_level(accumulation_data, total_deposited, lang)
        elif 'final' in phases_data:
            # Last fallback to final values
            final_data = phases_data['final']
            st.subheader("🎯 " + ("Metriche di Rischio Chiave (Valori Finali)" if lang == 'it' else "Key Risk Metrics (Final Values)"))
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="📊 VaR 5%",
                    value=f"€{final_data['var5']:,.0f}",
                    help="Valore minimo nel 95% dei casi" if lang == 'it' else "Minimum value in 95% of cases"
                )
            
            with col2:
                st.metric(
                    label="📉 CVaR 5%", 
                    value=f"€{final_data['cvar5']:,.0f}",
                    help="Valore medio nei peggiori 5% dei casi" if lang == 'it' else "Average value in worst 5% of cases"
                )
            
            with col3:
                st.metric(
                    label="📈 " + ("Media" if lang == 'it' else "Mean"),
                    value=f"€{final_data['mean']:,.0f}",
                    help="Valore medio di tutti gli scenari" if lang == 'it' else "Average value across all scenarios"
                )
            
            with col4:
                risk_gap = final_data['mean'] - final_data['cvar5'] if final_data['cvar5'] < final_data['mean'] else 0
                st.metric(
                    label="⚡ " + ("Gap di Rischio" if lang == 'it' else "Risk Gap"),
                    value=f"€{risk_gap:,.0f}",
                    help="Differenza tra media e CVaR 5%" if lang == 'it' else "Difference between mean and CVaR 5%"
                )
            
            # Risk level assessment
            ResultsDisplay._assess_risk_level(final_data, total_deposited, lang)
        
        # VaR/CVaR comparison table
        ResultsDisplay._show_var_cvar_table(phases_data, lang)
        
        # VaR/CVaR visualizations
        ResultsDisplay._show_var_cvar_visualizations(results, phases_data, lang)
        
        # Loss probability analysis - CORRECTED: Use accumulation NOMINAL values as primary
        if 'accumulation_nominal' in results:
            ResultsDisplay._show_loss_probability_analysis(results['accumulation_nominal'], total_deposited, lang, "accumulation_nominal")
        elif 'accumulation' in results:
            ResultsDisplay._show_loss_probability_analysis(results['accumulation'], total_deposited, lang, "accumulation")
        elif 'final' in results:
            # Last fallback to final values if accumulation not available
            ResultsDisplay._show_loss_probability_analysis(results['final'], total_deposited, lang, "final")

    @staticmethod
    def _assess_risk_level(final_data, total_deposited, lang):
        """Assess and display risk level based on VaR"""
        var5 = final_data['var5']
        mean_val = final_data['mean']
        
        if var5 <= 0:
            risk_status = "🔴 " + ("ALTO RISCHIO" if lang == 'it' else "HIGH RISK")
            risk_message = ("Significativa probabilità di perdere tutto il capitale" if lang == 'it' 
                           else "Significant probability of losing all capital")
            st.error(f"{risk_status}: {risk_message}")
        elif var5 < mean_val * 0.3:
            risk_status = "🟡 " + ("RISCHIO MODERATO-ALTO" if lang == 'it' else "MODERATE-HIGH RISK") 
            risk_message = ("I peggiori scenari possono essere molto negativi" if lang == 'it'
                           else "Worst-case scenarios can be very negative")
            st.warning(f"{risk_status}: {risk_message}")
        elif var5 < mean_val * 0.7:
            risk_status = "🟠 " + ("RISCHIO MODERATO" if lang == 'it' else "MODERATE RISK")
            risk_message = ("Rischio gestibile ma da monitorare" if lang == 'it'
                           else "Manageable risk but worth monitoring")
            st.info(f"{risk_status}: {risk_message}")
        else:
            risk_status = "🟢 " + ("RISCHIO BASSO" if lang == 'it' else "LOW RISK")
            risk_message = ("Scenari peggiori relativamente contenuti" if lang == 'it'
                           else "Worst-case scenarios relatively contained")
            st.success(f"{risk_status}: {risk_message}")
    
    @staticmethod
    def _show_var_cvar_table(phases_data, lang):
        """Show VaR/CVaR comparison table"""
        st.subheader("📊 " + ("Tabella VaR e CVaR per Fase" if lang == 'it' else "VaR and CVaR Table by Phase"))
        
        table_data = []
        for phase_key, phase_info in phases_data.items():
            table_data.append({
                ('Fase' if lang == 'it' else 'Phase'): phase_info['name'],
                ('Media (€)' if lang == 'it' else 'Mean (€)'): f"€{phase_info['mean']:,.0f}",
                ('VaR 5% (€)'): f"€{phase_info['var5']:,.0f}",
                ('CVaR 5% (€)'): f"€{phase_info['cvar5']:,.0f}",
                ('Rischio %' if lang == 'it' else 'Risk %'): f"{(1 - phase_info['var5']/phase_info['mean'])*100:.1f}%" if phase_info['mean'] > 0 else "N/A"
            })
        
        if table_data:
            df_var_cvar = pd.DataFrame(table_data)
            st.dataframe(df_var_cvar, use_container_width=True)
    
    @staticmethod
    def _show_var_cvar_visualizations(results, phases_data, lang):
        """Show VaR/CVaR visualizations"""
        st.subheader("📈 " + ("Visualizzazioni VaR e CVaR" if lang == 'it' else "VaR and CVaR Visualizations"))
        
        tab1, tab2 = st.tabs([
            "📊 " + ("Distribuzione con VaR/CVaR" if lang == 'it' else "Distribution with VaR/CVaR"),
            "📈 " + ("Confronto Fasi" if lang == 'it' else "Phase Comparison")
        ])
        
        with tab1:
            # CORRECTED: Use accumulation NOMINAL values for primary analysis
            if 'accumulation_nominal' in results and 'accumulation_nominal' in phases_data:
                ResultsDisplay._show_distribution_with_var_cvar_markers(results['accumulation_nominal'], phases_data['accumulation_nominal'], lang, "accumulation_nominal")
            elif 'accumulation' in results and 'accumulation' in phases_data:
                ResultsDisplay._show_distribution_with_var_cvar_markers(results['accumulation'], phases_data['accumulation'], lang, "accumulation")
            elif 'final' in results and 'final' in phases_data:
                ResultsDisplay._show_distribution_with_var_cvar_markers(results['final'], phases_data['final'], lang, "final")
        
        with tab2:
            ResultsDisplay._show_var_cvar_comparison_chart(phases_data, lang)
    
    @staticmethod
    def _show_distribution_with_var_cvar_markers(final_values, final_data, lang):
        """Show distribution with VaR and CVaR markers"""
        fig = go.Figure()
        
        # Add histogram
        fig.add_trace(go.Histogram(
            x=final_values,
            name="Distribuzione" if lang == 'it' else "Distribution",
            opacity=0.7,
            nbinsx=50,
            marker_color='lightblue'
        ))
        
        # Add VaR line
        fig.add_vline(
            x=final_data['var5'],
            line=dict(color="red", width=3, dash="dash"),
            annotation_text=f"VaR 5%: €{final_data['var5']:,.0f}",
            annotation_position="top"
        )
        
        # Add CVaR line
        fig.add_vline(
            x=final_data['cvar5'],
            line=dict(color="darkred", width=3, dash="solid"),
            annotation_text=f"CVaR 5%: €{final_data['cvar5']:,.0f}",
            annotation_position="top"
        )
        
        # Add mean line
        fig.add_vline(
            x=final_data['mean'],
            line=dict(color="green", width=2, dash="dot"),
            annotation_text=f"{'Media' if lang == 'it' else 'Mean'}: €{final_data['mean']:,.0f}",
            annotation_position="bottom"
        )
        
        fig.update_layout(
            title="Distribuzione Valori Finali con VaR e CVaR" if lang == 'it' else "Final Values Distribution with VaR and CVaR",
            xaxis_title="Valore Portfolio (€)" if lang == 'it' else "Portfolio Value (€)",
            yaxis_title="Frequenza" if lang == 'it' else "Frequency",
            height=500,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add explanation
        if lang == 'it':
            st.info("""
            **📖 Come leggere il grafico:**
            - **Linea rossa tratteggiata (VaR 5%)**: Solo il 5% dei risultati è a sinistra di questa linea
            - **Linea rossa continua (CVaR 5%)**: Valore medio di tutti i risultati a sinistra del VaR 5%
            - **Linea verde punteggiata**: Valore medio di tutti gli scenari
            """)
        else:
            st.info("""
            **📖 How to read the chart:**
            - **Red dashed line (VaR 5%)**: Only 5% of results are to the left of this line
            - **Red solid line (CVaR 5%)**: Average value of all results to the left of VaR 5%
            - **Green dotted line**: Average value across all scenarios
            """)
    
    @staticmethod
    def _show_var_cvar_comparison_chart(phases_data, lang):
        """Show VaR/CVaR comparison across phases"""
        phases = list(phases_data.keys())
        phase_names = [phases_data[phase]['name'] for phase in phases]
        var_values = [phases_data[phase]['var5'] for phase in phases]
        cvar_values = [phases_data[phase]['cvar5'] for phase in phases]
        mean_values = [phases_data[phase]['mean'] for phase in phases]
        
        fig = go.Figure()
        
        # Add VaR bars
        fig.add_trace(go.Bar(
            name='VaR 5%',
            x=phase_names,
            y=var_values,
            marker_color='lightcoral'
        ))
        
        # Add CVaR bars
        fig.add_trace(go.Bar(
            name='CVaR 5%',
            x=phase_names,
            y=cvar_values,
            marker_color='darkred'
        ))
        
        # Add Mean line
        fig.add_trace(go.Scatter(
            name='Media' if lang == 'it' else 'Mean',
            x=phase_names,
            y=mean_values,
            mode='lines+markers',
            line=dict(color='green', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="Confronto VaR e CVaR tra le Fasi" if lang == 'it' else "VaR and CVaR Comparison Across Phases",
            xaxis_title="Fase" if lang == 'it' else "Phase",
            yaxis_title="Valore (€)" if lang == 'it' else "Value (€)",
            barmode='group',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def _show_loss_probability_analysis(final_values, total_deposited, lang):
        """Show loss probability analysis"""
        st.subheader("📉 " + ("Analisi Probabilità di Perdita" if lang == 'it' else "Loss Probability Analysis"))
        
        # Calculate loss probabilities
        final_array = np.array(final_values)
        
        # Probability of total loss (final value < total deposited)
        total_loss_prob = np.sum(final_array < total_deposited) / len(final_array) * 100
        
        # Average value when loss occurs
        loss_values = final_array[final_array < total_deposited]
        avg_loss_value = np.mean(loss_values) if len(loss_values) > 0 else total_deposited
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                label="📊 " + ("Probabilità Perdita Totale" if lang == 'it' else "Total Loss Probability"),
                value=f"{total_loss_prob:.1f}%",
                help="Probabilità che il portfolio finale sia inferiore al totale depositato" if lang == 'it' 
                     else "Probability that final portfolio is less than total deposited"
            )
        
        with col2:
            st.metric(
                label="💔 " + ("Valore Medio (quando c'è perdita)" if lang == 'it' else "Average Value (when loss occurs)"),
                value=f"€{avg_loss_value:,.0f}",
                help="Valore medio del portfolio quando si verifica una perdita" if lang == 'it'
                     else "Average portfolio value when a loss occurs"
            )
        
        # Loss threshold analysis
        thresholds = [0.1, 0.2, 0.3, 0.5]  # 10%, 20%, 30%, 50% loss
        threshold_data = []
        
        for threshold in thresholds:
            threshold_value = total_deposited * (1 - threshold)
            prob = np.sum(final_array < threshold_value) / len(final_array) * 100
            
            threshold_data.append({
                ('Soglia Perdita' if lang == 'it' else 'Loss Threshold'): f"{threshold*100:.0f}%",
                ('Valore Soglia (€)' if lang == 'it' else 'Threshold Value (€)'): f"€{threshold_value:,.0f}",
                ('Probabilità (%)' if lang == 'it' else 'Probability (%)'): f"{prob:.1f}%"
            })
        
        if threshold_data:
            df_thresholds = pd.DataFrame(threshold_data)
            st.markdown("**" + ("Probabilità per Soglia:" if lang == 'it' else "Probability by Threshold:") + "**")
            st.dataframe(df_thresholds, use_container_width=True)
        
        # Visual representation
        threshold_names = [f"{int(t*100)}%" for t in thresholds]
        probabilities = [np.sum(final_array < total_deposited * (1 - t)) / len(final_array) * 100 for t in thresholds]
        
        fig = px.bar(
            x=threshold_names,
            y=probabilities,
            title="Probabilità di Perdita per Soglia" if lang == 'it' else "Loss Probability by Threshold",
            labels={
                'x': 'Soglia di Perdita' if lang == 'it' else 'Loss Threshold',
                'y': 'Probabilità (%)' if lang == 'it' else 'Probability (%)'
            },
            color=probabilities,
            color_continuous_scale='Reds'
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def _show_success_message(success_rate, lang):
        """Display success message based on success rate"""
        st.markdown("---")
        
        if success_rate >= 85:
            st.success(get_text('excellent_success', lang).format(success_rate))
        elif success_rate >= 65:
            st.warning(get_text('fair_success', lang).format(success_rate))
        else:
            st.error(get_text('warning_success', lang).format(success_rate))
