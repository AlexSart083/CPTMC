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
        
        if 'last_selected_profile' not in st.session_state:
            st.session_state.last_selected_profile = None
        
        if 'current_assets' not in st.session_state:
            st.session_state.current_assets = []
    
    @staticmethod
    def load_profile(config_manager, selected_profile):
        """Load a specific investment profile"""
        # Auto-load profile when selection changes
        if st.session_state.last_selected_profile != selected_profile:
            st.session_state.last_selected_profile = selected_profile
            loaded_assets = config_manager.get_profile_data(selected_profile)
            if loaded_assets:
                st.session_state.current_assets = loaded_assets
                st.rerun()
    
    @staticmethod
    def initialize_default_profile(config_manager, selected_profile):
        """Initialize default profile if no assets are loaded"""
        if 'current_assets' not in st.session_state or not st.session_state.current_assets:
            loaded_assets = config_manager.get_profile_data(selected_profile)
            if loaded_assets:
                st.session_state.current_assets = loaded_assets
    
    @staticmethod
    def reset_allocations():
        """Reset all allocations to 0"""
        if 'current_assets' in st.session_state:
            for asset in st.session_state.current_assets:
                asset['allocation'] = 0.0
            st.rerun()
    
    @staticmethod
    def balance_allocations():
        """Distribute allocations equally among active assets"""
        if 'current_assets' in st.session_state:
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
    
    @staticmethod
    def get_total_allocation(assets_data):
        """Calculate total allocation across all assets"""
        return sum(asset['allocation'] for asset in assets_data)
    
    @staticmethod
    def validate_simulation_inputs(assets_data, lang):
        """Validate inputs before running simulation"""
        from translations import get_text
        
        # Filter only assets with allocation > 0
        active_assets = [asset for asset in assets_data if asset['allocation'] > 0]
        
        if not active_assets:
            st.error(get_text('select_assets_error', lang))
            return False, None
        
        active_total = sum(asset['allocation'] for asset in active_assets)
        if abs(active_total - 100.0) > 0.01:
            st.error(get_text('fix_allocations_error', lang))
            return False, None
        
        return True, active_assets
    
    @staticmethod
    def update_assets_from_ui(assets_data):
        """Update session state assets with UI changes"""
        if 'current_assets' in st.session_state:
            # Update the session state with the modified assets
            for i, asset in enumerate(st.session_state.current_assets):
                if i < len(assets_data):
                    ui_asset = assets_data[i]
                    asset['allocation'] = ui_asset['allocation']
                    asset['ter'] = ui_asset['ter']
                    asset['return'] = ui_asset['return']
                    asset['volatility'] = ui_asset['volatility']
                    asset['min_return'] = ui_asset['min_return']
                    asset['max_return'] = ui_asset['max_return']
