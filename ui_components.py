"""
Updated UI components with enhanced disclaimers and REAL withdrawal option
MODIFIED VERSION - Added real withdrawal functionality
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from translations import get_text, get_profile_names, get_asset_names


class UIComponents:
    """Collection of reusable UI components with enhanced disclaimers and real withdrawal"""
    
    @staticmethod
    def render_language_selector(lang):
        """Render language selector"""
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
    
    @staticmethod
    def render_disclaimers(lang):
        """Render enhanced disclaimers section with long-term focus, return assumptions, and correlation limitations"""
        with st.expander(get_text('disclaimers_header', lang)):
            # Educational purpose disclaimer
            st.markdown(get_text('educational_disclaimer', lang))
            st.markdown(get_text('educational_text', lang))
            st.markdown(get_text('app_explanation', lang))
            
            # NEW: Long-term investment focus
            st.markdown(get_text('long_term_disclaimer', lang))
            st.markdown(get_text('long_term_text', lang))
            
            # NEW: Asset return assumptions
            st.markdown(get_text('returns_disclaimer', lang))
            st.markdown(get_text('returns_text', lang))
            
            # NEW: Asset correlation limitations
            st.markdown(get_text('correlation_disclaimer', lang))
            st.markdown(get_text('correlation_text', lang))
            
            # NEW: Real withdrawal explanation
            st.markdown(get_text('real_withdrawal_disclaimer', lang))
            st.markdown(get_text('real_withdrawal_text', lang))
            
            # Data information
            st.markdown(get_text('data_info', lang))
            st.markdown(get_text('data_text', lang))
            st.markdown("---")
    
    @staticmethod
    def render_general_parameters(lang):
        """Render general parameters in sidebar including tax rate and REAL withdrawal options"""
        st.subheader(get_text('general_parameters', lang))
        
        params = {}
        params['initial_amount'] = st.number_input(
            get_text('initial_amount', lang), 
            value=0.0, min_value=0.0, step=500.0
        )
        params['years_to_retirement'] = st.number_input(
            get_text('years_to_retirement', lang), 
            value=40.0, min_value=0.0, max_value=99.0, step=1.0
        )
        params['years_retired'] = st.number_input(
            get_text('years_retired', lang), 
            value=25.0, min_value=0.0, max_value=99.0, step=1.0
        )
        params['annual_contribution'] = st.number_input(
            get_text('annual_contribution', lang), 
            value=6000.0, min_value=0.0, step=500.0
        )
        params['adjust_contribution_inflation'] = st.checkbox(
            get_text('adjust_contribution_inflation', lang), 
            value=True,
            help=get_text('adjust_contribution_inflation_help', lang)
        )
        params['inflation'] = st.number_input(
            get_text('inflation', lang), 
            value=2.5, min_value=0.0, max_value=10.0, step=0.1, format="%.2f"
        )
        
        # MODIFIED: Real withdrawal section with explanation
        st.markdown("---")
        st.markdown("**💰 " + get_text('withdrawal_section_title', lang) + "**")
        
        # NEW: Real withdrawal toggle
        params['use_real_withdrawal'] = st.checkbox(
            get_text('use_real_withdrawal', lang),
            value=True,  # Default to True for better user experience
            help=get_text('use_real_withdrawal_help', lang)
        )
        
        # Withdrawal amount input with dynamic label
        if params['use_real_withdrawal']:
            withdrawal_label = get_text('real_withdrawal_amount', lang)
            withdrawal_help = get_text('real_withdrawal_help', lang)
        else:
            withdrawal_label = get_text('nominal_withdrawal_amount', lang)
            withdrawal_help = get_text('nominal_withdrawal_help', lang)
        
        params['withdrawal'] = st.number_input(
            withdrawal_label, 
            value=12000.0, min_value=0.0, step=500.0,
            help=withdrawal_help
        )
        
        # Show withdrawal explanation
        if params['use_real_withdrawal']:
            st.info(get_text('real_withdrawal_explanation', lang))
        else:
            st.warning(get_text('nominal_withdrawal_explanation', lang))
        
        # Capital gains tax rate parameter
        params['capital_gains_tax_rate'] = st.number_input(
            get_text('capital_gains_tax_rate', lang), 
            value=26.0, min_value=0.0, max_value=100.0, step=0.1, format="%.1f",
            help=get_text('capital_gains_tax_help', lang)
        )
        
        params['n_simulations'] = st.selectbox(
            get_text('n_simulations', lang), 
            [1000, 5000, 10000], index=2
        )
        
        return params
    
    @staticmethod
    def render_same_portfolio_toggle(lang):
        """Render the toggle for using same portfolio for both phases"""
        use_same = st.checkbox(
            get_text('use_same_portfolio', lang),
            value=st.session_state.use_same_portfolio,
            help=get_text('use_same_portfolio_help', lang),
            key='same_portfolio_toggle'
        )
        
        # Handle toggle change
        if use_same != st.session_state.use_same_portfolio:
            st.session_state.use_same_portfolio = use_same
            # Don't import here - let the main app handle the sync
            if use_same and 'current_accumulation_assets' in st.session_state:
                # Sync retirement to accumulation directly
                st.session_state.current_retirement_assets = [asset.copy() for asset in st.session_state.current_accumulation_assets]
                st.session_state.last_selected_retirement_profile = st.session_state.last_selected_accumulation_profile
            st.rerun()
        
        return use_same
    
    @staticmethod
    def render_profile_selector(asset_profiles, lang, phase='accumulation'):
        """Render investment profile selector for specific phase"""
        profile_names = get_profile_names(lang)
        profile_keys = list(asset_profiles.keys())
        profile_display_names = [profile_names.get(key, key) for key in profile_keys]
        
        if phase == 'accumulation':
            title = get_text('accumulation_profile', lang)
            key = 'accumulation_profile_selector'
            default_index = 2  # Moderate
        else:
            title = get_text('retirement_profile', lang)
            key = 'retirement_profile_selector'
            default_index = 1  # Conservative
        
        selected_profile_display = st.selectbox(
            title, 
            profile_display_names, 
            index=default_index,
            key=key
        )
        
        # Get the actual profile key
        selected_profile = profile_keys[profile_display_names.index(selected_profile_display)]
        return selected_profile
    
    @staticmethod
    def render_asset_editor(assets_data, lang, phase='accumulation'):
        """Render asset allocation editor for specific phase"""
        asset_names = get_asset_names(lang)
        
        # Initialize edit mode if it doesn't exist
        if 'edit_mode' not in st.session_state:
            st.session_state.edit_mode = {}
        
        updated_assets = []
        
        for i, asset in enumerate(assets_data):
            display_name = asset_names.get(asset['name'], asset['name'])
            edit_key = f"edit_{phase}_{i}"
            
            with st.expander(f"📈 {display_name}", expanded=False):
                
                # Always editable fields: Allocation and TER
                col_a, col_b = st.columns(2)
                
                with col_a:
                    alloc = st.number_input(
                        get_text('allocation_percent', lang), 
                        value=asset['allocation'], 
                        key=f"alloc_{phase}_{i}", 
                        step=1.0, 
                        format="%.2f", 
                        min_value=0.0, 
                        max_value=100.0
                    )
                
                with col_b:
                    ter = st.number_input(
                        get_text('ter_percent', lang), 
                        value=asset['ter'], 
                        key=f"ter_{phase}_{i}", 
                        step=0.01, 
                        format="%.3f", 
                        min_value=0.0, 
                        max_value=5.0
                    )
                
                # Update values in asset
                asset['allocation'] = alloc
                asset['ter'] = ter
                
                # Edit button for other parameters
                if edit_key not in st.session_state.edit_mode:
                    st.session_state.edit_mode[edit_key] = False
                
                if st.button(get_text('edit_parameters', lang), key=f"edit_btn_{phase}_{i}"):
                    st.session_state.edit_mode[edit_key] = not st.session_state.edit_mode[edit_key]
                
                # Fields editable only in edit mode
                if st.session_state.edit_mode[edit_key]:
                    st.markdown(get_text('advanced_parameters', lang))
                    col_c, col_d = st.columns(2)
                    
                    with col_c:
                        ret = st.number_input(
                            get_text('return_percent', lang), 
                            value=asset['return'], 
                            key=f"return_{phase}_{i}", 
                            step=0.1, 
                            format="%.2f"
                        )
                        vol = st.number_input(
                            get_text('volatility_percent', lang), 
                            value=asset['volatility'], 
                            key=f"vol_{phase}_{i}", 
                            step=0.1, 
                            format="%.2f", 
                            min_value=0.0
                        )
                    
                    with col_d:
                        min_ret = st.number_input(
                            get_text('min_return_percent', lang), 
                            value=asset['min_return'], 
                            key=f"min_{phase}_{i}", 
                            step=1.0, 
                            format="%.2f"
                        )
                        max_ret = st.number_input(
                            get_text('max_return_percent', lang), 
                            value=asset['max_return'], 
                            key=f"max_{phase}_{i}", 
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
                
                updated_assets.append({
                    'name': asset['name'],
                    'display_name': display_name,
                    'allocation': alloc,
                    'ter': ter,
                    'return': asset['return'],
                    'volatility': asset['volatility'],
                    'min_return': asset['min_return'],
                    'max_return': asset['max_return']
                })
        
        return updated_assets
    
    @staticmethod
    def render_allocation_controls(lang, phase='accumulation'):
        """Render allocation control buttons for specific phase"""
        col_reset, col_balance = st.columns(2)
        
        reset_clicked = False
        balance_clicked = False
        
        with col_reset:
            if st.button(get_text('reset_allocations', lang), key=f"reset_{phase}"):
                reset_clicked = True
        
        with col_balance:
            if st.button(get_text('balance_allocations', lang), key=f"balance_{phase}"):
                balance_clicked = True
        
        return reset_clicked, balance_clicked
    
    @staticmethod
    def render_allocation_status(total_allocation, lang):
        """Render allocation status message"""
        if abs(total_allocation - 100.0) > 0.01:
            st.error(get_text('total_allocation_error', lang).format(total_allocation))
            return False
        else:
            st.success(get_text('correct_allocation', lang).format(total_allocation))
            return True
    
    @staticmethod
    def render_allocation_chart(assets_data, lang, phase='accumulation'):
        """Render allocation pie chart for specific phase with unique key"""
        if phase == 'accumulation':
            title = get_text('accumulation_chart', lang)
        else:
            title = get_text('retirement_chart', lang)
        
        st.subheader(title)
        
        # Filter only assets with allocation > 0 for the chart
        active_assets = [asset for asset in assets_data if asset['allocation'] > 0]
        total_allocation = sum(asset['allocation'] for asset in assets_data)
        
        if abs(total_allocation - 100.0) <= 0.01 and active_assets:
            df_alloc = pd.DataFrame([
                {'Asset': asset['display_name'], 'Allocation': asset['allocation']}
                for asset in active_assets
            ])
            fig_pie = px.pie(
                df_alloc, 
                values='Allocation', 
                names='Asset', 
                title=get_text('portfolio_distribution', lang)
            )
            fig_pie.update_layout(height=400)
            # Add unique key based on phase to avoid duplicate ID error
            st.plotly_chart(fig_pie, use_container_width=True, key=f"pie_chart_{phase}")
        else:
            st.info(get_text('no_asset_selected', lang))
    
    @staticmethod
    def render_asset_summary(assets_data, lang, phase='accumulation'):
        """Render asset summary table for specific phase"""
        if phase == 'accumulation':
            title = get_text('accumulation_summary', lang)
        else:
            title = get_text('retirement_summary', lang)
        
        st.subheader(title)
        
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
    
    @staticmethod
    def render_run_simulation_button(lang):
        """Render run simulation button"""
        return st.button(get_text('run_simulation', lang), type="primary")
    
    @staticmethod
    def render_footer(lang):
        """Render footer"""
        st.markdown("---")
        st.markdown(
            f"<div style='text-align: center; color: #666; font-size: 0.8em; margin-top: 2em;'>"
            f"{get_text('footer', lang)}"
            f"</div>", 
            unsafe_allow_html=True
        )
