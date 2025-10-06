"""
Portfolio management utilities for the Monte Carlo Investment Simulator
FIXED VERSION - Risolti i problemi di caricamento asset
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
        
        # NUOVO: Flag per forzare il refresh degli asset dopo il caricamento
        if 'force_asset_refresh' not in st.session_state:
            st.session_state.force_asset_refresh = False
    
    @staticmethod
    def load_accumulation_profile(config_manager, selected_profile):
        """Load a specific investment profile for accumulation phase"""
        # FIXED: Carica SEMPRE il profilo, anche se è lo stesso
        loaded_assets = config_manager.get_profile_data(selected_profile)
        if loaded_assets:
            # Crea una copia profonda degli asset per evitare riferimenti condivisi
            st.session_state.current_accumulation_assets = [asset.copy() for asset in loaded_assets]
            st.session_state.last_selected_accumulation_profile = selected_profile
            
            # If using same portfolio, also load for retirement
            if st.session_state.use_same_portfolio:
                st.session_state.current_retirement_assets = [asset.copy() for asset in loaded_assets]
                st.session_state.last_selected_retirement_profile = selected_profile
            
            # Forza il refresh degli asset
            st.session_state.force_asset_refresh = True
            st.rerun()
    
    @staticmethod
    def load_retirement_profile(config_manager, selected_profile):
        """Load a specific investment profile for retirement phase"""
        # FIXED: Carica SEMPRE il profilo, anche se è lo stesso
        loaded_assets = config_manager.get_profile_data(selected_profile)
        if loaded_assets:
            # Crea una copia profonda degli asset
            st.session_state.current_retirement_assets = [asset.copy() for asset in loaded_assets]
            st.session_state.last_selected_retirement_profile = selected_profile
            
            # Forza il refresh degli asset
            st.session_state.force_asset_refresh = True
            st.rerun()
    
    @staticmethod
    def initialize_default_profiles(config_manager, accumulation_profile, retirement_profile):
        """Initialize default profiles if no assets are loaded"""
        # FIXED: Inizializza SOLO se gli asset sono vuoti
        if not st.session_state.current_accumulation_assets:
            loaded_assets = config_manager.get_profile_data(accumulation_profile)
            if loaded_assets:
                st.session_state.current_accumulation_assets = [asset.copy() for asset in loaded_assets]
                st.session_state.last_selected_accumulation_profile = accumulation_profile
        
        if not st.session_state.current_retirement_assets:
            if st.session_state.use_same_portfolio and st.session_state.current_accumulation_assets:
                # Use same assets as accumulation
                st.session_state.current_retirement_assets = [asset.copy() for asset in st.session_state.current_accumulation_assets]
                st.session_state.last_selected_retirement_profile = st.session_state.last_selected_accumulation_profile
            else:
                loaded_assets = config_manager.get_profile_data(retirement_profile)
                if loaded_assets:
                    st.session_state.current_retirement_assets = [asset.copy() for asset in loaded_assets]
                    st.session_state.last_selected_retirement_profile = retirement_profile
    
    @staticmethod
    def sync_retirement_to_accumulation():
        """Sync retirement portfolio to match accumulation when using same portfolio"""
        if (st.session_state.use_same_portfolio and 
            'current_accumulation_assets' in st.session_state and 
            st.session_state.current_accumulation_assets):
            # Crea una copia profonda per evitare riferimenti condivisi
            st.session_state.current_retirement_assets = [asset.copy() for asset in st.session_state.current_accumulation_assets]
            if 'last_selected_accumulation_profile' in st.session_state:
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
        
        # FIXED: Assicurati che stiamo usando gli asset correnti dal session state
        if not accumulation_assets:
            accumulation_assets = st.session_state.get('current_accumulation_assets', [])
        
        if not retirement_assets:
            retirement_assets = st.session_state.get('current_retirement_assets', [])
        
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
            # FIXED: Aggiorna direttamente il session state con i nuovi dati
            # Questo assicura che le modifiche dall'UI vengano salvate
            st.session_state[assets_key] = [asset.copy() for asset in assets_data]
            
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
    
    @staticmethod
    def get_current_assets(phase='accumulation'):
        """Get current assets for a specific phase - NUOVO metodo helper"""
        assets_key = f'current_{phase}_assets'
        return st.session_state.get(assets_key, [])
    
    @staticmethod
    def clear_force_refresh():
        """Clear the force refresh flag - NUOVO"""
        if 'force_asset_refresh' in st.session_state:
            st.session_state.force_asset_refresh = False
