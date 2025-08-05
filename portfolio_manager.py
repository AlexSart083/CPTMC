"""
Portfolio management utilities for the Monte Carlo Investment Simulator
"""

import streamlit as st


class PortfolioManager:
    """Manages portfolio operations and state management"""
    
    @staticmethod
    def initialize_session_state():
        """Initialize session state variables"""
        if 'language' not in st.session_state:
            st.session_state.language = 'en'
        
        if 'edit_mode' not in st.session_state:
            st.session_state.edit_mode = {}
        
        # Separate profiles for accumulation and retirement
        if 'last_selected_accumulation_profile' not in st.session_state:
            st.session_state.last_selected_accumulation_profile = None
        
        if 'last_selected_retirement_profile' not in st.session_state:
            st.session_state.last_selected_retirement_profile = None
        
        # Separate assets for accumulation and retirement
        if 'current_accumulation_assets' not in st.session_state:
            st.session_state.current_accumulation_assets = []
        
        if 'current_retirement_assets' not in st.session_state:
            st.session_state.current_retirement_assets = []
        
        # Flag to use same portfolio for both phases
        if 'use_same_portfolio' not in st.session_state:
            st.session_state.use_same_portfolio = True
    
    @staticmethod
    def load_accumulation_profile(config_manager, selected_profile):
        """Load a specific investment profile for accumulation phase"""
        if st.session_state.last_selected_accumulation_profile != selected_profile:
            st.session_state.last_selected_accumulation_profile = selected_profile
            loaded_assets = config_manager.get_profile_data(selected_profile)
            if loaded_assets:
                st.session_state.current_accumulation_assets = loaded_assets
                # If using same portfolio, also load for retirement
                if st.session_state.use_same_portfolio:
                    st.session_state.current_retirement_assets = loaded_assets.copy()
                    st.session_state.last_selected_retirement_profile = selected_profile
                st.rerun()
    
    @staticmethod
    def load_retirement_profile(config_manager, selected_profile):
        """Load a specific investment profile for retirement phase"""
        if st.session_state.last_selected_retirement_profile != selected_profile:
            st.session_state.last_selected_retirement_profile = selected_profile
            loaded_assets = config_manager.get_profile_data(selected_profile)
            if loaded_assets:
                st.session_state.current_retirement_assets = loaded_assets
                st.rerun()
    
    @staticmethod
    def initialize_default_profiles(config_manager, accumulation_profile, retirement_profile):
        """Initialize default profiles if no assets are loaded"""
        if 'current_accumulation_assets' not in st.session_state or not st.session_state.current_accumulation_assets:
            loaded_assets = config_manager.get_profile_data(accumulation_profile)
            if loaded_assets:
                st.session_state.current_accumulation_assets = loaded_assets
        
        if 'current_retirement_assets' not in st.session_state or not st.session_state.current_retirement_assets:
            if st.session_state.use_same_portfolio:
                # Use same assets as accumulation
                st.session_state.current_retirement_assets = st.session_state.current_accumulation_assets.copy()
            else:
                loaded_assets = config_manager.get_profile_data(retirement_profile)
                if loaded_assets:
                    st.session_state.current_retirement_assets = loaded_assets
    
    @staticmethod
    def sync_retirement_to_accumulation():
        """Sync retirement portfolio to match accumulation when using same portfolio"""
        if st.session_state.use_same_portfolio and st.session_state.current_accumulation_assets:
            st.session_state.current_retirement_assets = [asset.copy() for asset in st.session_state.current_accumulation_assets]
            st.session_state.last_selected_retirement_profile = st.session_state.last_selected_accumulation_profile
    
    @staticmethod
    def reset_allocations(phase='accumulation'):
        """Reset all allocations to 0 for specified phase"""
        if phase == 'accumulation' and 'current_accumulation_assets' in st.session_state:
            for asset in st.session_state.current_accumulation_assets:
                asset['allocation'] = 0.0
            if st.session_state.use_same_portfolio:
                PortfolioManager.sync_retirement_to_accumulation()
            st.rerun()
        elif phase == 'retirement' and 'current_retirement_assets' in st.session_state:
            for asset in st.session_state.current_retirement_assets:
                asset['allocation'] = 0.0
            st.rerun()
    
    @staticmethod
    def balance_allocations(phase='accumulation'):
        """Distribute allocations equally among active assets for specified phase"""
        assets_key = f'current_{phase}_assets'
        if assets_key in st.session_state:
            assets = st.session_state[assets_key]
            # Distribute equally among assets with allocation > 0
            active_assets = [asset for asset in assets if asset['allocation'] > 0]
            if active_assets:
                equal_alloc = 100.0 / len(active_assets)
                for asset in assets:
                    if asset['allocation'] > 0:
                        asset['allocation'] = equal_alloc
                    else:
                        asset['allocation'] = 0.0
                
                if phase == 'accumulation' and st.session_state.use_same_portfolio:
                    PortfolioManager.sync_retirement_to_accumulation()
                st.rerun()
    
    @staticmethod
    def get_total_allocation(assets_data):
        """Calculate total allocation across all assets"""
        return sum(asset['allocation'] for asset in assets_data)
    
    @staticmethod
    def validate_simulation_inputs(accumulation_assets, retirement_assets, lang):
        """Validate inputs before running simulation"""
        from translations import get_text
        
        # Filter only assets with allocation > 0
        active_accumulation_assets = [asset for asset in accumulation_assets if asset['allocation'] > 0]
        active_retirement_assets = [asset for asset in retirement_assets if asset['allocation'] > 0]
        
        if not active_accumulation_assets:
            st.error(get_text('select_accumulation_assets_error', lang))
            return False, None, None
        
        if not active_retirement_assets:
            st.error(get_text('select_retirement_assets_error', lang))
            return False, None, None
        
        # Check accumulation allocations
        accumulation_total = sum(asset['allocation'] for asset in active_accumulation_assets)
        if abs(accumulation_total - 100.0) > 0.01:
            st.error(get_text('fix_accumulation_allocations_error', lang))
            return False, None, None
        
        # Check retirement allocations
        retirement_total = sum(asset['allocation'] for asset in active_retirement_assets)
        if abs(retirement_total - 100.0) > 0.01:
            st.error(get_text('fix_retirement_allocations_error', lang))
            return False, None, None
        
        return True, active_accumulation_assets, active_retirement_assets
    
    @staticmethod
    def update_assets_from_ui(assets_data, phase='accumulation'):
        """Update session state assets with UI changes"""
        assets_key = f'current_{phase}_assets'
        if assets_key in st.session_state:
            # Update the session state with the modified assets
            for i, asset in enumerate(st.session_state[assets_key]):
                if i < len(assets_data):
                    ui_asset = assets_data[i]
                    asset['allocation'] = ui_asset['allocation']
                    asset['ter'] = ui_asset['ter']
                    asset['return'] = ui_asset['return']
                    asset['volatility'] = ui_asset['volatility']
                    asset['min_return'] = ui_asset['min_return']
                    asset['max_return'] = ui_asset['max_return']
            
            # Sync retirement if using same portfolio and updating accumulation
            if phase == 'accumulation' and st.session_state.use_same_portfolio:
                PortfolioManager.sync_retirement_to_accumulation()
    
    @staticmethod
    def handle_same_portfolio_toggle():
        """Handle the toggle of use_same_portfolio checkbox"""
        if st.session_state.use_same_portfolio:
            # Sync retirement to accumulation
            PortfolioManager.sync_retirement_to_accumulation()
            st.rerun()
