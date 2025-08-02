import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import json
import os

class CantierSimulatorWeb:
    def __init__(self):
        self.asset_profiles = self.load_asset_profiles()
    
    def load_asset_profiles(self):
        """Loads asset profiles from the configuration file"""
        config_file = 'config.json'
        
        if not os.path.exists(config_file):
            st.error(f"❌ Configuration file '{config_file}' not found!")
            st.stop()
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config['asset_profiles']
        except Exception as e:
            st.error(f"❌ Error loading configuration file: {str(e)}")
            st.stop()

def main():
    st.set_page_config(
        page_title="Monte Carlo Investment Simulator",
        page_icon="🏗️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    simulator = CantierSimulatorWeb()
    
    # Main Header
    st.title("🏗️ Monte Carlo Simulation for Retirement Planning")
    st.markdown("This application is for educational purposes only and simulates purely theoretical scenarios based on simplified assumptions. The results should not be interpreted as real forecasts or investment recommendations. No information provided constitutes financial, asset, or tax advice.")    
    
    # Sidebar for parameters
    with st.sidebar:
        st.header("⚙️ Simulation Parameters")
        
        # General parameters
        st.subheader("📊 General Parameters")
        initial_amount = st.number_input("Initial Amount (€)", value=0.0, min_value=0.0, step=500.0)
        years_to_retirement = st.number_input("Years to Retirement", value=40.0, min_value=0.0, max_value=99.0, step=1.0)
        years_retired = st.number_input("Years in Retirement", value=25.0, min_value=0.0, max_value=99.0, step=1.0)
        annual_contribution = st.number_input("Annual Contribution (€)", value=6000.0, min_value=0.0, step=500.0)
        inflation = st.number_input("Annual Inflation (%)", value=2.5, min_value=0.0, max_value=10.0, step=0.1, format="%.2f")
        withdrawal = st.number_input("Annual Withdrawal in Retirement (€)", value=12000.0, min_value=0.0, step=500.0)
        n_simulations = st.selectbox("Number of Simulations", [1000, 5000, 10000], index=2)
        
        # Risk profile
        st.subheader("🎯 Investment Profile")
        selected_profile = st.selectbox("Select Profile:", list(simulator.asset_profiles.keys()), index=1)
    
    # Main area divided into columns
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("💼 Portfolio Configuration")
        
        # Load selected profile
        if st.button("🔄 Load Selected Profile"):
            st.session_state.current_assets = [asset.copy() for asset in simulator.asset_profiles[selected_profile]]
        
        # Initialize assets if they don't exist
        if 'current_assets' not in st.session_state:
            st.session_state.current_assets = [asset.copy() for asset in simulator.asset_profiles[selected_profile]]
        
        assets_data = []
        
        for i, asset in enumerate(st.session_state.current_assets):
            with st.expander(f"📈 {asset['name']}", expanded=False):
                col_a, col_b = st.columns(2)
                
                with col_a:
                    # Read-only information
                    st.text_input(f"Name", value=asset['name'], key=f"name_{i}", disabled=True)
                    st.number_input(f"Return (%)", value=asset['return'], key=f"return_{i}", step=0.1, format="%.2f", disabled=True)
                    st.number_input(f"Volatility (%)", value=asset['volatility'], key=f"vol_{i}", step=0.1, format="%.2f", disabled=True)
                
                with col_b:
                    # Only allocation is editable
                    alloc = st.number_input(f"Allocation (%)", value=asset['allocation'], key=f"alloc_{i}", step=1.0, format="%.2f", min_value=0.0, max_value=100.0)
                    st.number_input(f"Min Return (%)", value=asset['min_return'], key=f"min_{i}", step=1.0, format="%.2f", disabled=True)
                    st.number_input(f"Max Return (%)", value=asset['max_return'], key=f"max_{i}", step=1.0, format="%.2f", disabled=True)
                
                # Update allocation in the asset
                asset['allocation'] = alloc
                
                assets_data.append({
                    'name': asset['name'],
                    'return': asset['return'],
                    'volatility': asset['volatility'],
                    'allocation': alloc,
                    'min_return': asset['min_return'],
                    'max_return': asset['max_return']
                })
        
        total_allocation = sum(asset['allocation'] for asset in assets_data)
        
        # Buttons to balance allocations
        col_reset, col_balance = st.columns(2)
        
        with col_reset:
            if st.button("🔄 Reset Allocations"):
                for asset in st.session_state.current_assets:
                    asset['allocation'] = 0.0
                st.rerun()
        
        with col_balance:
            if st.button("⚖️ Balance Allocations"):
                # Distribute equally among assets with allocation > 0
                active_assets = [asset for asset in st.session_state.current_assets if asset['allocation'] > 0]
                if active_assets:
                    equal_alloc = 100.0 / len(active_assets)
                    for asset in st.session_state.current_assets:
                        if asset['allocation'] > 0:
                            asset['allocation'] = equal_alloc
                        else:
                            asset['allocation'] = 0.0
                    st.rerun()
        
        # Show allocation status
        if abs(total_allocation - 100.0) > 0.01:
            st.error(f"⚠️ Total allocation: {total_allocation:.1f}% (must be 100%)")
        else:
            st.success(f"✅ Correct allocation: {total_allocation:.1f}%")
    
    with col2:
        st.subheader("📈 Allocation Chart")
        if abs(total_allocation - 100.0) <= 0.01:
            # Filter only assets with allocation > 0 for the chart
            active_assets = [asset for asset in assets_data if asset['allocation'] > 0]
            if active_assets:
                df_alloc = pd.DataFrame([
                    {'Asset': asset['name'], 'Allocation': asset['allocation']}
                    for asset in active_assets
                ])
                fig_pie = px.pie(df_alloc, values='Allocation', names='Asset', title="Portfolio Distribution")
                fig_pie.update_layout(height=400)
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No assets selected")
        
        st.subheader("📋 Asset Summary")
        # Show only assets with allocation > 0 in the summary table
        active_assets_df = pd.DataFrame([asset for asset in assets_data if asset['allocation'] > 0])
        if not active_assets_df.empty:
            st.dataframe(active_assets_df, use_container_width=True)
        else:
            st.info("No active assets")
    
    st.markdown("---")
    
    if st.button("🚀 **RUN SIMULATION**", type="primary"):
        # Filter only assets with allocation > 0
        active_assets = [asset for asset in assets_data if asset['allocation'] > 0]
        
        if not active_assets:
            st.error("❌ Select at least one asset with allocation > 0!")
            return
        
        active_total = sum(asset['allocation'] for asset in active_assets)
        if abs(active_total - 100.0) > 0.01:
            st.error("❌ Please correct the allocations first!")
            return
        
        total_deposited = initial_amount + (annual_contribution * years_to_retirement)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        with st.spinner("🔄 Simulating..."):
            results = run_monte_carlo_simulation(
                active_assets, initial_amount, years_to_retirement, years_retired,
                annual_contribution, inflation / 100, withdrawal, n_simulations,
                progress_bar, status_text
            )
        
        show_results(results, total_deposited, n_simulations)

def run_monte_carlo_simulation(assets_data, initial_amount, years_to_retirement, 
                              years_retired, annual_contribution, inflation, 
                              withdrawal, n_simulations, progress_bar, status_text):
    
    mean_returns = [asset['return'] / 100 for asset in assets_data]
    volatilities = [asset['volatility'] / 100 for asset in assets_data]
    allocations = [asset['allocation'] / 100 for asset in assets_data]
    min_returns = [asset['min_return'] / 100 for asset in assets_data]
    max_returns = [asset['max_return'] / 100 for asset in assets_data]
    
    accumulation_balances = []
    final_results = []
    
    for sim in range(n_simulations):
        if sim % 100 == 0:
            progress_bar.progress((sim + 1) / n_simulations)
            status_text.text(f"Simulation {sim + 1} of {n_simulations}")
        
        balance = initial_amount
        
        for year in range(int(years_to_retirement)):
            annual_returns = [np.random.normal(mean_returns[i], volatilities[i]) for i in range(len(mean_returns))]
            capped_returns = [max(min(annual_returns[i], max_returns[i]), min_returns[i]) for i in range(len(mean_returns))]
            annual_return = sum(capped_returns[i] * allocations[i] for i in range(len(mean_returns)))
            balance *= (1 + annual_return)
            balance += annual_contribution
            balance /= (1 + inflation)
        
        accumulation_balances.append(balance)
        
        for year in range(int(years_retired)):
            annual_returns = [np.random.normal(mean_returns[i], volatilities[i]) for i in range(len(mean_returns))]
            capped_returns = [max(min(annual_returns[i], max_returns[i]), min_returns[i]) for i in range(len(mean_returns))]
            annual_return = sum(capped_returns[i] * allocations[i] for i in range(len(mean_returns)))
            balance *= (1 + annual_return)
            balance /= (1 + inflation)
            balance -= withdrawal
            if balance < 0:
                balance = 0
                break
        
        final_results.append(balance)
    
    progress_bar.progress(1.0)
    status_text.text("✅ Simulation completed!")
    
    return {'accumulation': accumulation_balances, 'final': final_results}


def show_results(results, total_deposited, n_simulations):
    st.markdown("---")
    st.header("🎯 Simulation Results")
    
    accumulation_balances = results['accumulation']
    final_results = results['final']
    
    avg_accumulation = np.mean(accumulation_balances)
    acc_25th = np.percentile(accumulation_balances, 25)
    acc_50th = np.percentile(accumulation_balances, 50)
    acc_75th = np.percentile(accumulation_balances, 75)
    
    avg_final = np.mean(final_results)
    final_25th = np.percentile(final_results, 25)
    final_50th = np.percentile(final_results, 50)
    final_75th = np.percentile(final_results, 75)
    success_rate = sum(r > 0 for r in final_results) / n_simulations * 100
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Total Deposited", f"€{total_deposited:,.0f}")
    with col2:
        st.metric("📈 Avg Accumulation Value", f"€{avg_accumulation:,.0f}")
    with col3:
        st.metric("✨ Avg Final Value", f"€{avg_final:,.0f}")
    with col4:
        st.metric("✅ Success Rate", f"{success_rate:.1f}%")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Accumulation Phase")
        acc_data = {
            'Percentile': ['Average', '25th', '50th', '75th'],
            'Value (€)': [f"{avg_accumulation:,.0f}", f"{acc_25th:,.0f}", f"{acc_50th:,.0f}", f"{acc_75th:,.0f}"]
        }
        st.table(pd.DataFrame(acc_data))
    
    with col2:
        st.subheader("🏁 Final Values")
        final_data = {
            'Percentile': ['Average', '25th', '50th', '75th'],
            'Value (€)': [f"{avg_final:,.0f}", f"{final_25th:,.0f}", f"{final_50th:,.0f}", f"{final_75th:,.0f}"]
        }
        st.table(pd.DataFrame(final_data))
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_acc = px.histogram(x=accumulation_balances, nbins=50, title="Distribution of End-of-Accumulation Values")
        fig_acc.update_xaxes(title="Value (€)")
        fig_acc.update_yaxes(title="Frequency")
        st.plotly_chart(fig_acc, use_container_width=True)
    
    with col2:
        fig_final = px.histogram(x=final_results, nbins=50, title="Distribution of Final Values")
        fig_final.update_xaxes(title="Value (€)")
        fig_final.update_yaxes(title="Frequency")
        st.plotly_chart(fig_final, use_container_width=True)

    if success_rate >= 80:
        st.success(f"🎉 Excellent! With a {success_rate:.1f}% success rate, now you can watch the construction sites from Monte-Carlo")
    elif success_rate >= 60:
        st.warning(f"⚠️ Decent. With a {success_rate:.1f}% success rate, you might have to consider canned tuna.")
    else:
        st.error(f"❌ Caution! Only a {success_rate:.1f}% success rate. Caritas awaits you.")

if __name__ == "__main__":
    main()
