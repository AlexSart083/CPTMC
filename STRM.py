import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import json
import os
from translations import get_text, get_profile_names, get_asset_names

class CantierSimulatorWeb:
    def __init__(self):
        self.asset_profiles = self.load_asset_profiles()
        self.asset_characteristics = self.load_asset_characteristics()
    
    def load_asset_profiles(self):
        """Load asset profiles from configuration file"""
        config_file = 'config.json'
        
        if not os.path.exists(config_file):
            lang = st.session_state.get('language', 'en')
            st.error(get_text('config_not_found', lang).format(config_file))
            st.stop()
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config['asset_profiles']
        except Exception as e:
            lang = st.session_state.get('language', 'en')
            st.error(get_text('config_load_error', lang).format(str(e)))
            st.stop()
    
    def load_asset_characteristics(self):
        """Load asset characteristics from configuration file"""
        config_file = 'config.json'
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config['asset_characteristics']
        except Exception as e:
            lang = st.session_state.get('language', 'en')
            st.error(get_text('asset_characteristics_error', lang).format(str(e)))
            st.stop()

def main():
    # Initialize language in session state
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    
    lang = st.session_state.language
    
    st.set_page_config(
        page_title=get_text('page_title', lang),
        page_icon="🏗️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Language selector in the top right corner
    col1, col2, col3 = st.columns([6, 1, 1])
    with col3:
        language_options = {'English': 'en', 'Italiano': 'it'}
        selected_lang = st.selectbox(
            get_text('language_selector', lang),
            options=list(language_options.keys()),
            index=0 if lang == 'en' else 1,
            key='lang_selector'
        )
        
        # Update language if changed
        new_lang = language_options[selected_lang]
        if new_lang != st.session_state.language:
            st.session_state.language = new_lang
            st.rerun()
    
    simulator = CantierSimulatorWeb()
    
    # Main header
    st.title(get_text('main_title', lang))
    
    # Collapsible disclaimers
    with st.expander(get_text('disclaimers_header', lang)):
        st.markdown(get_text('educational_disclaimer', lang))
        st.markdown(get_text('educational_text', lang))
        
        st.markdown(get_text('data_info', lang))
        st.markdown(get_text('data_text', lang))
    
    st.markdown("---")    
    
    # Sidebar for parameters
    with st.sidebar:
        st.header(get_text('simulation_parameters', lang))
        
        # General parameters
        st.subheader(get_text('general_parameters', lang))
        initial_amount = st.number_input(get_text('initial_amount', lang), value=0.0, min_value=0.0, step=500.0)
        years_to_retirement = st.number_input(get_text('years_to_retirement', lang), value=40.0, min_value=0.0, max_value=99.0, step=1.0)
        years_retired = st.number_input(get_text('years_retired', lang), value=25.0, min_value=0.0, max_value=99.0, step=1.0)
        annual_contribution = st.number_input(get_text('annual_contribution', lang), value=6000.0, min_value=0.0, step=500.0)
        inflation = st.number_input(get_text('inflation', lang), value=2.5, min_value=0.0, max_value=10.0, step=0.1, format="%.2f")
        withdrawal = st.number_input(get_text('withdrawal', lang), value=12000.0, min_value=0.0, step=500.0)
        n_simulations = st.selectbox(get_text('n_simulations', lang), [1000, 5000, 10000], index=2)
        

    
    # Main area divided into columns
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader(get_text('portfolio_config', lang))
        
        # Investment profile selector
        st.subheader(get_text('investment_profile', lang))
        profile_names = get_profile_names(lang)
        profile_keys = list(simulator.asset_profiles.keys())
        profile_display_names = [profile_names.get(key, key) for key in profile_keys]
        
        selected_profile_display = st.selectbox(
            get_text('select_profile', lang), 
            profile_display_names, 
            index=1,
            key='profile_selector'
        )
        
        # Get the actual profile key
        selected_profile = profile_keys[profile_display_names.index(selected_profile_display)]
        
        # Auto-load profile when selection changes
        if 'last_selected_profile' not in st.session_state:
            st.session_state.last_selected_profile = selected_profile
        
        if selected_profile != st.session_state.last_selected_profile:
            st.session_state.last_selected_profile = selected_profile
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
            st.rerun()
        
        # Initialize assets if they don't exist or if it's the first load
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
        asset_names = get_asset_names(lang)
        
        for i, asset in enumerate(st.session_state.current_assets):
            display_name = asset_names.get(asset['name'], asset['name'])
            with st.expander(f"📈 {display_name}", expanded=False):
                
                # Always editable fields: Allocation and TER
                col_a, col_b = st.columns(2)
                
                with col_a:
                    alloc = st.number_input(
                        get_text('allocation_percent', lang), 
                        value=asset['allocation'], 
                        key=f"alloc_{i}", 
                        step=1.0, 
                        format="%.2f", 
                        min_value=0.0, 
                        max_value=100.0
                    )
                
                with col_b:
                    ter = st.number_input(
                        get_text('ter_percent', lang), 
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
                
                if st.button(get_text('edit_parameters', lang), key=f"edit_btn_{i}"):
                    st.session_state.edit_mode[edit_key] = not st.session_state.edit_mode[edit_key]
                
                # Fields editable only in edit mode
                if st.session_state.edit_mode[edit_key]:
                    st.markdown(get_text('advanced_parameters', lang))
                    col_c, col_d = st.columns(2)
                    
                    with col_c:
                        ret = st.number_input(
                            get_text('return_percent', lang), 
                            value=asset['return'], 
                            key=f"return_{i}", 
                            step=0.1, 
                            format="%.2f"
                        )
                        vol = st.number_input(
                            get_text('volatility_percent', lang), 
                            value=asset['volatility'], 
                            key=f"vol_{i}", 
                            step=0.1, 
                            format="%.2f", 
                            min_value=0.0
                        )
                    
                    with col_d:
                        min_ret = st.number_input(
                            get_text('min_return_percent', lang), 
                            value=asset['min_return'], 
                            key=f"min_{i}", 
                            step=1.0, 
                            format="%.2f"
                        )
                        max_ret = st.number_input(
                            get_text('max_return_percent', lang), 
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
                        st.info(f"{get_text('return_label', lang)} {asset['return']:.2f}%")
                        st.info(f"{get_text('volatility_label', lang)} {asset['volatility']:.2f}%")
                    with col_info2:
                        st.info(f"{get_text('min_return_label', lang)} {asset['min_return']:.2f}%")
                        st.info(f"{get_text('max_return_label', lang)} {asset['max_return']:.2f}%")
                
                assets_data.append({
                    'name': asset['name'],
                    'display_name': display_name,
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
            if st.button(get_text('reset_allocations', lang)):
                for asset in st.session_state.current_assets:
                    asset['allocation'] = 0.0
                st.rerun()
        
        with col_balance:
            if st.button(get_text('balance_allocations', lang)):
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
            st.error(get_text('total_allocation_error', lang).format(total_allocation))
        else:
            st.success(get_text('correct_allocation', lang).format(total_allocation))
    
    with col2:
        st.subheader(get_text('allocation_chart', lang))
        if abs(total_allocation - 100.0) <= 0.01:
            # Filter only assets with allocation > 0 for the chart
            active_assets = [asset for asset in assets_data if asset['allocation'] > 0]
            if active_assets:
                df_alloc = pd.DataFrame([
                    {'Asset': asset['display_name'], 'Allocation': asset['allocation']}
                    for asset in active_assets
                ])
                fig_pie = px.pie(df_alloc, values='Allocation', names='Asset', title=get_text('portfolio_distribution', lang))
                fig_pie.update_layout(height=400)
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info(get_text('no_asset_selected', lang))
        
        st.subheader(get_text('asset_summary', lang))
        # Show only assets with allocation > 0 in the summary table
        active_assets_df = pd.DataFrame([asset for asset in assets_data if asset['allocation'] > 0])
        if not active_assets_df.empty:
            # Show only asset name and allocation
            summary_df = active_assets_df[['display_name', 'allocation']].copy()
            # Rename columns for display
            summary_df.columns = ['Asset', get_text('allocation_percent', lang)]
            st.dataframe(summary_df, use_container_width=True)
        else:
            st.info(get_text('no_active_assets', lang))
    
    st.markdown("---")
    
    if st.button(get_text('run_simulation', lang), type="primary"):
        # Filter only assets with allocation > 0
        active_assets = [asset for asset in assets_data if asset['allocation'] > 0]
        
        if not active_assets:
            st.error(get_text('select_assets_error', lang))
            return
        
        active_total = sum(asset['allocation'] for asset in active_assets)
        if abs(active_total - 100.0) > 0.01:
            st.error(get_text('fix_allocations_error', lang))
            return
        
        total_deposited = initial_amount + (annual_contribution * years_to_retirement)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        with st.spinner(get_text('simulation_progress', lang)):
            results = run_monte_carlo_simulation(
                active_assets, initial_amount, years_to_retirement, years_retired,
                annual_contribution, inflation / 100, withdrawal, n_simulations,
                progress_bar, status_text, lang
            )
        
        show_results(results, total_deposited, n_simulations, lang)

def run_monte_carlo_simulation(assets_data, initial_amount, years_to_retirement, 
                              years_retired, annual_contribution, inflation, 
                              withdrawal, n_simulations, progress_bar, status_text, lang):
    
    mean_returns = [asset['return'] / 100 for asset in assets_data]
    volatilities = [asset['volatility'] / 100 for asset in assets_data]
    allocations = [asset['allocation'] / 100 for asset in assets_data]
    min_returns = [asset['min_return'] / 100 for asset in assets_data]
    max_returns = [asset['max_return'] / 100 for asset in assets_data]
    ters = [asset['ter'] / 100 for asset in assets_data]
    
    accumulation_balances = []
    accumulation_balances_nominal = []  # Without inflation adjustment
    final_results = []
    
    for sim in range(n_simulations):
        if sim % 100 == 0:
            progress_bar.progress((sim + 1) / n_simulations)
            status_text.text(get_text('simulation_step', lang).format(sim + 1, n_simulations))
        
        balance = initial_amount
        balance_nominal = initial_amount  # Track nominal value without inflation
        
        # Accumulation phase
        for year in range(int(years_to_retirement)):
            annual_returns = [np.random.normal(mean_returns[i], volatilities[i]) for i in range(len(mean_returns))]
            capped_returns = [max(min(annual_returns[i], max_returns[i]), min_returns[i]) for i in range(len(mean_returns))]
            # Apply TER (subtract fees from returns)
            net_returns = [capped_returns[i] - ters[i] for i in range(len(capped_returns))]
            annual_return = sum(net_returns[i] * allocations[i] for i in range(len(net_returns)))
            
            # Real value (adjusted for inflation)
            balance *= (1 + annual_return)
            balance += annual_contribution
            balance /= (1 + inflation)
            
            # Nominal value (not adjusted for inflation)
            balance_nominal *= (1 + annual_return)
            balance_nominal += annual_contribution
        
        accumulation_balances.append(balance)
        accumulation_balances_nominal.append(balance_nominal)
        
        # Retirement phase (continue with real value)
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
    status_text.text(get_text('simulation_completed', lang))
    
    return {
        'accumulation': accumulation_balances, 
        'accumulation_nominal': accumulation_balances_nominal,
        'final': final_results
    }


def show_results(results, total_deposited, n_simulations, lang):
    st.markdown("---")
    st.header(get_text('simulation_results', lang))
    
    accumulation_balances = results['accumulation']
    accumulation_balances_nominal = results['accumulation_nominal']
    final_results = results['final']
    
    # Calcolo della media e dei percentili per valori reali (aggiustati per inflazione)
    avg_accumulation = np.mean(accumulation_balances)
    acc_25th = np.percentile(accumulation_balances, 25)
    acc_50th = np.percentile(accumulation_balances, 50)
    acc_75th = np.percentile(accumulation_balances, 75)
    
    # Calcolo della media e dei percentili per valori nominali (senza aggiustamento inflazione)
    avg_accumulation_nominal = np.mean(accumulation_balances_nominal)
    acc_25th_nominal = np.percentile(accumulation_balances_nominal, 25)
    acc_50th_nominal = np.percentile(accumulation_balances_nominal, 50)
    acc_75th_nominal = np.percentile(accumulation_balances_nominal, 75)
    
    avg_final = np.mean(final_results)
    final_25th = np.percentile(final_results, 25)
    final_50th = np.percentile(final_results, 50)
    final_75th = np.percentile(final_results, 75)
    success_rate = sum(r > 0 for r in final_results) / n_simulations * 100
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(get_text('total_deposited', lang), f"€{total_deposited:,.0f}")
    with col2:
        st.metric(get_text('median_accumulation', lang), f"€{acc_50th:,.0f}")
    with col3:
        st.metric(get_text('median_final', lang), f"€{final_50th:,.0f}")
    with col4:
        st.metric(get_text('success_rate', lang), f"{success_rate:.1f}%")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader(get_text('accumulation_phase_real', lang))
        acc_data = {
            get_text('percentile', lang): [get_text('median', lang), '25th', '75th', get_text('average', lang)], 
            get_text('value_euro', lang): [f"{acc_50th:,.0f}",  f"{acc_25th:,.0f}", f"{acc_75th:,.0f}", f"{avg_accumulation:,.0f}"]
        }
        st.table(pd.DataFrame(acc_data))
    
    with col2:
        st.subheader(get_text('accumulation_phase_nominal', lang))
        acc_data_nominal = {
            get_text('percentile', lang): [get_text('median', lang), '25th', '75th', get_text('average', lang)], 
            get_text('value_euro', lang): [f"{acc_50th_nominal:,.0f}",  f"{acc_25th_nominal:,.0f}", f"{acc_75th_nominal:,.0f}", f"{avg_accumulation_nominal:,.0f}"]
        }
        st.table(pd.DataFrame(acc_data_nominal))
    
    with col3:
        # Create title with info tooltip
        title_col, info_col = st.columns([4, 1])
        with title_col:
            st.subheader(get_text('final_values', lang))
        with info_col:
            with st.popover("ℹ️"):
                st.write(get_text('final_values_info', lang))
        
        final_data = {
            get_text('percentile', lang): [get_text('median', lang), '25th', '75th', get_text('average', lang)], 
            get_text('value_euro', lang): [f"{final_50th:,.0f}",  f"{final_25th:,.0f}", f"{final_75th:,.0f}", f"{avg_final:,.0f}"]
        }
        st.table(pd.DataFrame(final_data))
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fig_acc = px.histogram(x=accumulation_balances, nbins=50, title=get_text('distribution_accumulation_real', lang))
        fig_acc.update_xaxes(title=get_text('value_euro', lang))
        fig_acc.update_yaxes(title=get_text('frequency', lang))
        st.plotly_chart(fig_acc, use_container_width=True)
    
    with col2:
        fig_acc_nominal = px.histogram(x=accumulation_balances_nominal, nbins=50, title=get_text('distribution_accumulation_nominal', lang))
        fig_acc_nominal.update_xaxes(title=get_text('value_euro', lang))
        fig_acc_nominal.update_yaxes(title=get_text('frequency', lang))
        st.plotly_chart(fig_acc_nominal, use_container_width=True)
    
    with col3:
        fig_final = px.histogram(x=final_results, nbins=50, title=get_text('distribution_final', lang))
        fig_final.update_xaxes(title=get_text('value_euro', lang))
        fig_final.update_yaxes(title=get_text('frequency', lang))
        st.plotly_chart(fig_final, use_container_width=True)

    if success_rate >= 80:
        st.success(get_text('excellent_success', lang).format(success_rate))
    elif success_rate >= 60:
        st.warning(get_text('fair_success', lang).format(success_rate))
    else:
        st.error(get_text('warning_success', lang).format(success_rate))

if __name__ == "__main__":
    main()
    
    # Footer
    st.markdown("---")
    lang = st.session_state.get('language', 'en')
    st.markdown(
        f"<div style='text-align: center; color: #666; font-size: 0.8em; margin-top: 2em;'>"
        f"{get_text('footer', lang)}"
        f"</div>", 
        unsafe_allow_html=True
    )
