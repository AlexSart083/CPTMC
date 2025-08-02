import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import json
import os

class CantierSimulatorWeb:
    def __init__(self):
        self.asset_profiles = self.load_asset_profiles()
        self.asset_characteristics = self.load_asset_characteristics()
    
    def load_asset_profiles(self):
        """Load asset profiles from configuration file"""
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
    
    def load_asset_characteristics(self):
        """Load asset characteristics from configuration file"""
        config_file = 'config.json'
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config['asset_characteristics']
        except Exception as e:
            st.error(f"❌ Error loading asset characteristics: {str(e)}")
            st.stop()

def main():
    st.set_page_config(
        page_title="Monte Carlo Investment Simulator",
        page_icon="🏗️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    simulator = CantierSimulatorWeb()
    
    # Main header
    st.title("🏗️ Monte Carlo Simulation for Retirement Planning")
    st.markdown("This application is for educational purposes only and simulates purely theoretical scenarios based on simplified assumptions. Results should not be interpreted as real predictions nor as investment recommendations. No information provided constitutes financial, wealth or tax advice.")
    
    # Data disclaimer and credits
    st.info("📊 **Data Information**: The returns used are based on the last 30 years with Euro currency. Data may be inaccurate or outdated and should be used for educational purposes only.")
    
    # Credits
    st.markdown("---")
    col_left, col_right = st.columns([3, 1])
    with col_right:
        st.markdown("**Created by AS with the supervision of KIM**")
    st.markdown("---")    
    
    # Sidebar for parameters
    with st.sidebar:
        st.header("⚙️ Simulation Parameters")
        
        # General parameters
        st.subheader("📊 General Parameters")
        initial_amount = st.number_input("Initial amount (€)", value=0.0, min_value=0.0, step=500.0)
        years_to_retirement = st.number_input("Years to retirement", value=40.0, min_value=0.0, max_value=99.0, step=1.0)
        years_retired = st.number_input("Years in retirement", value=25.0, min_value=0.0, max_value=99.0, step=1.0)
        annual_contribution = st.number_input("Annual contribution (€)", value=6000.0, min_value=0.0, step=500.0)
        inflation = st.number_input("Annual inflation (%)", value=2.5, min_value=0.0, max_value=10.0, step=0.1, format="%.2f")
        withdrawal = st.number_input("Annual withdrawal in retirement (€)", value=12000.0, min_value=0.0, step=500.0)
        n_simulations = st.selectbox("Number of simulations", [1000, 5000, 10000], index=2)
        
        # Risk profile
        st.subheader("🎯 Investment Profile")
        selected_profile = st.selectbox("Select profile:", list(simulator.asset_profiles.keys()), index=1)
    
    # Main area divided into columns
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("💼 Portfolio Configuration")
        
        # Load selected profile
        if st.button("🔄 Load Selected Profile"):
            # Combine profile data with asset characteristics
            loaded_assets = []
            for asset_profile in simulator.asset_profiles[selected_profile]:
                asset_name = asset_profile['name']
                if asset_name in simulator.asset_characteristics:
                    characteristics = simulator.asset_characteristics[asset_name]
                    combined_asset = {
                        'name': asset_name,
                        'allocation': asset_profile['allocation'],
                        'ter': asset_profile['ter'],
                        'return': characteristics['return'],
                        'volatility': characteristics['volatility'],
                        'min_return': characteristics['min_return'],
                        'max_return': characteristics['max_return']
                    }
                    loaded_assets.append(combined_asset)
            st.session_state.current_assets = loaded_assets
        
        # Initialize assets if they don't exist
        if 'current_assets' not in st.session_state:
            loaded_assets = []
            for asset_profile in simulator.asset_profiles[selected_profile]:
                asset_name = asset_profile['name']
                if asset_name in simulator.asset_characteristics:
                    characteristics = simulator.asset_characteristics[asset_name]
                    combined_asset = {
                        'name': asset_name,
                        'allocation': asset_profile['allocation'],
                        'ter': asset_profile['ter'],
                        'return': characteristics['return'],
                        'volatility': characteristics['volatility'],
                        'min_return': characteristics['min_return'],
                        'max_return': characteristics['max_return']
                    }
                    loaded_assets.append(combined_asset)
            st.session_state.current_assets = loaded_assets
        
        # Initialize edit mode if it doesn't exist
        if 'edit_mode' not in st.session_state:
            st.session_state.edit_mode = {}
        
        assets_data = []
        
        for i, asset in enumerate(st.session_state.current_assets):
            with st.expander(f"📈 {asset['name']}", expanded=False):
                
                # Always editable fields: Allocation and TER
                col_a, col_b = st.columns(2)
                
                with col_a:
                    alloc = st.number_input(
                        f"Allocation (%)", 
                        value=asset['allocation'], 
                        key=f"alloc_{i}", 
                        step=1.0, 
                        format="%.2f", 
                        min_value=0.0, 
                        max_value=100.0
                    )
                
                with col_b:
                    ter = st.number_input(
                        f"TER (%)", 
                        value=asset['ter'], 
                        key=f"ter_{i}", 
                        step=0.01, 
                        format="%.3f", 
                        min_value=0.0, 
                        max_value=5.0
                    )
                
                # Update values in asset
                asset['allocation'] = alloc
                asset['ter'] = ter
                
                # Edit button for other parameters
                edit_key = f"edit_{i}"
                if edit_key not in st.session_state.edit_mode:
                    st.session_state.edit_mode[edit_key] = False
                
                if st.button(f"✏️ Edit Parameters", key=f"edit_btn_{i}"):
                    st.session_state.edit_mode[edit_key] = not st.session_state.edit_mode[edit_key]
                
                # Fields editable only in edit mode
                if st.session_state.edit_mode[edit_key]:
                    st.markdown("**Advanced Parameters:**")
                    col_c, col_d = st.columns(2)
                    
                    with col_c:
                        ret = st.number_input(
                            f"Return (%)", 
                            value=asset['return'], 
                            key=f"return_{i}", 
                            step=0.1, 
                            format="%.2f"
                        )
                        vol = st.number_input(
                            f"Volatility (%)", 
                            value=asset['volatility'], 
                            key=f"vol_{i}", 
                            step=0.1, 
                            format="%.2f", 
                            min_value=0.0
                        )
                    
                    with col_d:
                        min_ret = st.number_input(
                            f"Min Return (%)", 
                            value=asset['min_return'], 
                            key=f"min_{i}", 
                            step=1.0, 
                            format="%.2f"
                        )
                        max_ret = st.number_input(
                            f"Max Return (%)", 
                            value=asset['max_return'], 
                            key=f"max_{i}", 
                            step=1.0, 
                            format="%.2f"
                        )
                    
                    # Update values in asset
                    asset['return'] = ret
                    asset['volatility'] = vol
                    asset['min_return'] = min_ret
                    asset['max_return'] = max_ret
                
                else:
                    # Show parameters in read-only mode
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.info(f"**Return:** {asset['return']:.2f}%")
                        st.info(f"**Volatility:** {asset['volatility']:.2f}%")
                    with col_info2:
                        st.info(f"**Min Return:** {asset['min_return']:.2f}%")
                        st.info(f"**Max Return:** {asset['max_return']:.2f}%")
                
                assets_data.append({
                    'name': asset['name'],
                    'allocation': alloc,
                    'ter': ter,
                    'return': asset['return'],
                    'volatility': asset['volatility'],
                    'min_return': asset['min_return'],
                    'max_return': asset['max_return']
                })
        
        total_allocation = sum(asset['allocation'] for asset in assets_data)
        
        # Buttons to manage allocations
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
                st.info("No asset selected")
        
        st.subheader("📋 Asset Summary")
        # Show only assets with allocation > 0 in the summary table
        active_assets_df = pd.DataFrame([asset for asset in assets_data if asset['allocation'] > 0])
        if not active_assets_df.empty:
            # Reorder columns to show allocation and ter first
            columns_order = ['name', 'allocation', 'ter', 'return', 'volatility', 'min_return', 'max_return']
            active_assets_df = active_assets_df.reindex(columns=columns_order)
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
            st.error("❌ Fix allocations first!")
            return
        
        total_deposited = initial_amount + (annual_contribution * years_to_retirement)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        with st.spinner("🔄 Simulation in progress..."):
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
    ters = [asset['ter'] / 100 for asset in assets_data]
    
    accumulation_balances = []
    final_results = []
    
    for sim in range(n_simulations):
        if sim % 100 == 0:
            progress_bar.progress((sim + 1) / n_simulations)
            status_text.text(f"Simulation {sim + 1} of {n_simulations}")
        
        balance = initial_amount
        
        # Accumulation phase
        for year in range(int(years_to_retirement)):
            annual_returns = [np.random.normal(mean_returns[i], volatilities[i]) for i in range(len(mean_returns))]
            capped_returns = [max(min(annual_returns[i], max_returns[i]), min_returns[i]) for i in range(len(mean_returns))]
            # Apply TER (subtract fees from returns)
            net_returns = [capped_returns[i] - ters[i] for i in range(len(capped_returns))]
            annual_return = sum(net_returns[i] * allocations[i] for i in range(len(net_returns)))
            balance *= (1 + annual_return)
            balance += annual_contribution
            balance /= (1 + inflation)
        
        accumulation_balances.append(balance)
        
        # Retirement phase
        for year in range(int(years_retired)):
            annual_returns = [np.random.normal(mean_returns[i], volatilities[i]) for i in range(len(mean_returns))]
            capped_returns = [max(min(annual_returns[i], max_returns[i]), min_returns[i]) for i in range(len(mean_returns))]
            # Apply TER (subtract fees from returns)
            net_returns = [capped_returns[i] - ters[i] for i in range(len(capped_returns))]
            annual_return = sum(net_returns[i] * allocations[i] for i in range(len(net_returns)))
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
    acc_75th = np.percentile(accumulation_balances, 75)
    
    avg_final = np.mean(final_results)
    final_25th = np.percentile(final_results, 25)
    final_75th = np.percentile(final_results, 75)
    success_rate = sum(r > 0 for r in final_results) / n_simulations * 100
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Total Deposited", f"€{total_deposited:,.0f}")
    with col2:
        st.metric("📈 Average Accumulation Value", f"€{avg_accumulation:,.0f}")
    with col3:
        st.metric("✨ Average Final Value", f"€{avg_final:,.0f}")
    with col4:
        st.metric("✅ Success Rate", f"{success_rate:.1f}%")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Accumulation Phase")
        acc_data = {
            'Percentile': ['25th', 'Average', '75th'],
            'Value (€)': [f"{acc_25th:,.0f}", f"{avg_accumulation:,.0f}", f"{acc_75th:,.0f}"]
        }
        st.table(pd.DataFrame(acc_data))
    
    with col2:
        st.subheader("🏁 Final Values")
        final_data = {
            'Percentile': ['25th', 'Average', '75th'],
            'Value (€)': [f"{final_25th:,.0f}", f"{avg_final:,.0f}", f"{final_75th:,.0f}"]
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
        st.success(f"🎉 Excellent! With {success_rate:.1f}% probability of success, you can now watch the construction sites from Monte Carlo")
    elif success_rate >= 60:
        st.warning(f"⚠️ Fair. With {success_rate:.1f}% success rate, you might need to consider canned tuna.")
    else:
        st.error(f"❌ Warning! Only {success_rate:.1f}% probability of success. Charity awaits you.")

if __name__ == "__main__":
    main()
