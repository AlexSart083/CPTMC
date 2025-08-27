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
        
        # Display key metrics for final values
        if 'final' in phases_data:
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
        
        # Loss probability analysis
        if 'final' in results:
            ResultsDisplay._show_loss_probability_analysis(results['final'], total_deposited, lang)

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
