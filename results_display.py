"""
Results display components for the Monte Carlo Investment Simulator
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from translations import get_text


class ResultsDisplay:
    """Handles display of simulation results"""
    
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
    def show_results(results, total_deposited, n_simulations, years_to_retirement, 
                    years_retired, lang):
        """Display comprehensive simulation results"""
        st.markdown("---")
        st.header(get_text('simulation_results', lang))
        
        accumulation_balances = results['accumulation']
        accumulation_balances_nominal = results['accumulation_nominal']
        final_results = results['final']
        
        # Calculate statistics for real values (inflation-adjusted)
        avg_accumulation = np.mean(accumulation_balances)
        acc_25th = np.percentile(accumulation_balances, 25)
        acc_50th = np.percentile(accumulation_balances, 50)
        acc_75th = np.percentile(accumulation_balances, 75)
        
        # Calculate statistics for nominal values (without inflation adjustment)
        avg_accumulation_nominal = np.mean(accumulation_balances_nominal)
        acc_25th_nominal = np.percentile(accumulation_balances_nominal, 25)
        acc_50th_nominal = np.percentile(accumulation_balances_nominal, 50)
        acc_75th_nominal = np.percentile(accumulation_balances_nominal, 75)
        
        avg_final = np.mean(final_results)
        final_25th = np.percentile(final_results, 25)
        final_50th = np.percentile(final_results, 50)
        final_75th = np.percentile(final_results, 75)
        success_rate = sum(r > 0 for r in final_results) / n_simulations * 100
        
        # Calculate CAGR for accumulation phase (nominal)
        acc_cagr_50th_nominal = ResultsDisplay.calculate_cagr(acc_50th_nominal, total_deposited, years_to_retirement)
        acc_cagr_25th_nominal = ResultsDisplay.calculate_cagr(acc_25th_nominal, total_deposited, years_to_retirement)
        acc_cagr_75th_nominal = ResultsDisplay.calculate_cagr(acc_75th_nominal, total_deposited, years_to_retirement)
        acc_cagr_avg_nominal = ResultsDisplay.calculate_cagr(avg_accumulation_nominal, total_deposited, years_to_retirement)
        
        # Calculate CAGR for accumulation phase (real)
        acc_cagr_50th = ResultsDisplay.calculate_cagr(acc_50th, total_deposited, years_to_retirement)
        acc_cagr_25th = ResultsDisplay.calculate_cagr(acc_25th, total_deposited, years_to_retirement)
        acc_cagr_75th = ResultsDisplay.calculate_cagr(acc_75th, total_deposited, years_to_retirement)
        acc_cagr_avg = ResultsDisplay.calculate_cagr(avg_accumulation, total_deposited, years_to_retirement)
        
        # Calculate CAGR for final phase (from start of accumulation to end of retirement)
        total_years = years_to_retirement + years_retired
        final_cagr_50th = ResultsDisplay.calculate_cagr(final_50th, total_deposited, total_years)
        final_cagr_25th = ResultsDisplay.calculate_cagr(final_25th, total_deposited, total_years)
        final_cagr_75th = ResultsDisplay.calculate_cagr(final_75th, total_deposited, total_years)
        final_cagr_avg = ResultsDisplay.calculate_cagr(avg_final, total_deposited, total_years)
        
        # Display key metrics
        ResultsDisplay._show_key_metrics(total_deposited, acc_50th, final_50th, success_rate, lang)
        
        # Display detailed tables
        ResultsDisplay._show_detailed_tables(
            acc_50th_nominal, acc_25th_nominal, acc_75th_nominal, avg_accumulation_nominal,
            acc_cagr_50th_nominal, acc_cagr_25th_nominal, acc_cagr_75th_nominal, acc_cagr_avg_nominal,
            acc_50th, acc_25th, acc_75th, avg_accumulation,
            acc_cagr_50th, acc_cagr_25th, acc_cagr_75th, acc_cagr_avg,
            final_50th, final_25th, final_75th, avg_final,
            final_cagr_50th, final_cagr_25th, final_cagr_75th, final_cagr_avg,
            lang
        )
        
        # Display histograms
        ResultsDisplay._show_histograms(
            accumulation_balances_nominal, accumulation_balances, final_results, lang
        )
        
        # Display success message
        ResultsDisplay._show_success_message(success_rate, lang)
    
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
    def _show_detailed_tables(acc_50th_nominal, acc_25th_nominal, acc_75th_nominal, avg_accumulation_nominal,
                             acc_cagr_50th_nominal, acc_cagr_25th_nominal, acc_cagr_75th_nominal, acc_cagr_avg_nominal,
                             acc_50th, acc_25th, acc_75th, avg_accumulation,
                             acc_cagr_50th, acc_cagr_25th, acc_cagr_75th, acc_cagr_avg,
                             final_50th, final_25th, final_75th, avg_final,
                             final_cagr_50th, final_cagr_25th, final_cagr_75th, final_cagr_avg,
                             lang):
        """Display detailed statistics tables"""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader(get_text('accumulation_phase_nominal', lang))
            acc_data_nominal = {
                get_text('percentile', lang): [get_text('median', lang), '25th', '75th', get_text('average', lang)], 
                get_text('value_euro', lang): [f"{acc_50th_nominal:,.0f}", f"{acc_25th_nominal:,.0f}", 
                                             f"{acc_75th_nominal:,.0f}", f"{avg_accumulation_nominal:,.0f}"],
                get_text('cagr_percent', lang): [f"{acc_cagr_50th_nominal:.2f}%", f"{acc_cagr_25th_nominal:.2f}%", 
                                               f"{acc_cagr_75th_nominal:.2f}%", f"{acc_cagr_avg_nominal:.2f}%"]
            }
            st.table(pd.DataFrame(acc_data_nominal))
        
        with col2:
            st.subheader(get_text('accumulation_phase_real', lang))
            acc_data = {
                get_text('percentile', lang): [get_text('median', lang), '25th', '75th', get_text('average', lang)], 
                get_text('value_euro', lang): [f"{acc_50th:,.0f}", f"{acc_25th:,.0f}", 
                                             f"{acc_75th:,.0f}", f"{avg_accumulation:,.0f}"],
                get_text('cagr_percent', lang): [f"{acc_cagr_50th:.2f}%", f"{acc_cagr_25th:.2f}%", 
                                               f"{acc_cagr_75th:.2f}%", f"{acc_cagr_avg:.2f}%"]
            }
            st.table(pd.DataFrame(acc_data))
        
        with col3:
            st.subheader(get_text('final_values', lang))
            final_data = {
                get_text('percentile', lang): [get_text('median', lang), '25th', '75th', get_text('average', lang)], 
                get_text('value_euro', lang): [f"{final_50th:,.0f}", f"{final_25th:,.0f}", 
                                             f"{final_75th:,.0f}", f"{avg_final:,.0f}"],
                get_text('cagr_percent', lang): [f"{final_cagr_50th:.2f}%", f"{final_cagr_25th:.2f}%", 
                                               f"{final_cagr_75th:.2f}%", f"{final_cagr_avg:.2f}%"]
            }
            st.table(pd.DataFrame(final_data))
    
    @staticmethod
    def _show_histograms(accumulation_balances_nominal, accumulation_balances, final_results, lang):
        """Display distribution histograms"""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fig_acc_nominal = px.histogram(
                x=accumulation_balances_nominal, 
                nbins=50, 
                title=get_text('distribution_accumulation_nominal', lang)
            )
            fig_acc_nominal.update_xaxes(title=get_text('value_euro', lang))
            fig_acc_nominal.update_yaxes(title=get_text('frequency', lang))
            st.plotly_chart(fig_acc_nominal, use_container_width=True)
        
        with col2:
            fig_acc = px.histogram(
                x=accumulation_balances, 
                nbins=50, 
                title=get_text('distribution_accumulation_real', lang)
            )
            fig_acc.update_xaxes(title=get_text('value_euro', lang))
            fig_acc.update_yaxes(title=get_text('frequency', lang))
            st.plotly_chart(fig_acc, use_container_width=True)
        
        with col3:
            fig_final = px.histogram(
                x=final_results, 
                nbins=50, 
                title=get_text('distribution_final', lang)
            )
            fig_final.update_xaxes(title=get_text('value_euro', lang))
            fig_final.update_yaxes(title=get_text('frequency', lang))
            st.plotly_chart(fig_final, use_container_width=True)
    
    @staticmethod
    def _show_success_message(success_rate, lang):
        """Display success rate message with appropriate styling"""
        if success_rate >= 80:
            st.success(get_text('excellent_success', lang).format(success_rate))
        elif success_rate >= 60:
            st.warning(get_text('fair_success', lang).format(success_rate))
        else:
            st.error(get_text('warning_success', lang).format(success_rate))
