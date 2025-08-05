"""
Configuration manager for the Monte Carlo Investment Simulator
Handles loading and managing asset profiles and characteristics
"""

import json
import os
import streamlit as st
from translations import get_text


class ConfigManager:
    """Manages configuration loading and validation"""
    
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self._asset_profiles = None
        self._asset_characteristics = None
        self._load_config()
    
    def _load_config(self):
        """Load configuration from JSON file"""
        if not os.path.exists(self.config_file):
            lang = st.session_state.get('language', 'en')
            st.error(get_text('config_not_found', lang).format(self.config_file))
            st.stop()
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self._asset_profiles = config['asset_profiles']
            self._asset_characteristics = config['asset_characteristics']
            
        except Exception as e:
            lang = st.session_state.get('language', 'en')
            st.error(get_text('config_load_error', lang).format(str(e)))
            st.stop()
    
    @property
    def asset_profiles(self):
        """Get asset profiles"""
        return self._asset_profiles
    
    @property
    def asset_characteristics(self):
        """Get asset characteristics"""
        return self._asset_characteristics
    
    def get_profile_data(self, profile_name):
        """Get data for a specific profile"""
        if profile_name not in self._asset_profiles:
            return None
        
        loaded_assets = []
        for asset_profile in self._asset_profiles[profile_name]:
            asset_name = asset_profile['name']
            if asset_name in self._asset_characteristics:
                characteristics = self._asset_characteristics[asset_name]
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
        
        return loaded_assets
    
    def validate_allocations(self, assets_data):
        """Validate that allocations sum to 100%"""
        total_allocation = sum(asset['allocation'] for asset in assets_data)
        return abs(total_allocation - 100.0) <= 0.01
    
    def get_active_assets(self, assets_data):
        """Get only assets with allocation > 0"""
        return [asset for asset in assets_data if asset['allocation'] > 0]
