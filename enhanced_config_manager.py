"""
Enhanced Configuration manager with correlation support
"""

import json
import os
import streamlit as st
import numpy as np
from translations import get_text


class EnhancedConfigManager:
    """Enhanced configuration manager with correlation support"""
    
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self._asset_profiles = None
        self._asset_characteristics = None
        self._correlation_matrix = None
        self._correlation_scenarios = None
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
            
            # Load correlation data if available
            if 'correlation_matrix' in config:
                self._correlation_matrix = {
                    'assets': config['correlation_matrix']['assets'],
                    'matrix': np.array(config['correlation_matrix']['matrix'])
                }
            
            if 'correlation_scenarios' in config:
                self._correlation_scenarios = {}
                for scenario_name, scenario_data in config['correlation_scenarios'].items():
                    self._correlation_scenarios[scenario_name] = {
                        'description': scenario_data['description'],
                        'matrix': np.array(scenario_data['matrix'])
                    }
            
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
    
    @property
    def correlation_matrix(self):
        """Get default correlation matrix"""
        return self._correlation_matrix
    
    @property
    def correlation_scenarios(self):
        """Get correlation scenarios"""
        return self._correlation_scenarios
    
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
    
    def get_correlation_matrix_for_assets(self, asset_names, scenario='normal_times'):
        """
        Get correlation matrix for specific assets and scenario
        
        Args:
            asset_names: List of asset names
            scenario: Correlation scenario name
            
        Returns:
            numpy array with correlation matrix, or None if not available
        """
        if not self._correlation_scenarios or scenario not in self._correlation_scenarios:
            return None
        
        if not self._correlation_matrix or 'assets' not in self._correlation_matrix:
            return None
        
        # Get the full asset list from config
        config_assets = self._correlation_matrix['assets']
        scenario_matrix = self._correlation_scenarios[scenario]['matrix']
        
        # Find indices for requested assets
        try:
            asset_indices = [config_assets.index(asset_name) for asset_name in asset_names]
        except ValueError:
            # Some assets not found in correlation matrix
            return None
        
        # Extract submatrix for requested assets
        submatrix = scenario_matrix[np.ix_(asset_indices, asset_indices)]
        return submatrix
    
    def get_default_correlation_matrix(self, asset_names):
        """
        Generate default correlation matrix for given assets
        
        Args:
            asset_names: List of asset names
            
        Returns:
            numpy array with default correlations
        """
        # Default correlation values based on asset types
        default_correlations = {
            ('Stocks', 'Bond'): -0.1,
            ('Stocks', 'Gold'): 0.1,
            ('Stocks', 'REIT'): 0.7,
            ('Stocks', 'Commodities'): 0.3,
            ('Stocks', 'Cash'): 0.0,
            ('Bond', 'Gold'): 0.2,
            ('Bond', 'REIT'): 0.1,
            ('Bond', 'Commodities'): 0.1,
            ('Bond', 'Cash'): 0.3,
            ('Gold', 'REIT'): 0.2,
            ('Gold', 'Commodities'): 0.4,
            ('Gold', 'Cash'): 0.1,
            ('REIT', 'Commodities'): 0.3,
            ('REIT', 'Cash'): 0.0,
            ('Commodities', 'Cash'): 0.0,
        }
        
        n_assets = len(asset_names)
        correlation_matrix = np.eye(n_assets)
        
        for i, asset1 in enumerate(asset_names):
            for j, asset2 in enumerate(asset_names):
                if i != j:
                    # Try both orders of asset pairs
                    corr = default_correlations.get((asset1, asset2))
                    if corr is None:
                        corr = default_correlations.get((asset2, asset1))
                    
                    if corr is not None:
                        correlation_matrix[i, j] = corr
                    else:
                        # Default correlation for unknown pairs
                        if 'UserAsset' in asset1 or 'UserAsset' in asset2:
                            correlation_matrix[i, j] = 0.2
                        else:
                            correlation_matrix[i, j] = 0.1
        
        return correlation_matrix
    
    def save_custom_correlation_matrix(self, asset_names, correlation_matrix, scenario_name='custom'):
        """
        Save custom correlation matrix to session state or config
        
        Args:
            asset_names: List of asset names
            correlation_matrix: numpy array with correlations
            scenario_name: Name for the custom scenario
        """
        # Store in session state for current session
        if 'custom_correlations' not in st.session_state:
            st.session_state.custom_correlations = {}
        
        st.session_state.custom_correlations[scenario_name] = {
            'assets': asset_names,
            'matrix': correlation_matrix.tolist(),
            'description': f'Custom correlation scenario: {scenario_name}'
        }
    
    def get_available_correlation_scenarios(self):
        """Get list of available correlation scenarios"""
        scenarios = []
        
        # Add predefined scenarios
        if self._correlation_scenarios:
            scenarios.extend(list(self._correlation_scenarios.keys()))
        
        # Add custom scenarios from session state
        if hasattr(st.session_state, 'custom_correlations'):
            scenarios.extend([f"custom_{name}" for name in st.session_state.custom_correlations.keys()])
        
        # Always include independent scenario
        if 'independent' not in scenarios:
            scenarios.append('independent')
        
        return scenarios
    
    def export_correlation_config(self, filename='custom_correlations.json'):
        """Export current correlation settings to JSON file"""
        export_data = {
            'correlation_scenarios': {},
            'asset_list': list(self._asset_characteristics.keys()) if self._asset_characteristics else []
        }
        
        # Add predefined scenarios
        if self._correlation_scenarios:
            for name, scenario in self._correlation_scenarios.items():
                export_data['correlation_scenarios'][name] = {
                    'description': scenario['description'],
                    'matrix': scenario['matrix'].tolist()
                }
        
        # Add custom scenarios from session state
        if hasattr(st.session_state, 'custom_correlations'):
            for name, scenario in st.session_state.custom_correlations.items():
                export_data['correlation_scenarios'][f'custom_{name}'] = {
                    'description': scenario['description'],
                    'matrix': scenario['matrix']
                }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            st.error(f"Error exporting correlation config: {str(e)}")
            return False
    
    def import_correlation_config(self, filename):
        """Import correlation settings from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            if 'correlation_scenarios' in import_data:
                # Store imported scenarios in session state
                if 'imported_correlations' not in st.session_state:
                    st.session_state.imported_correlations = {}
                
                for name, scenario in import_data['correlation_scenarios'].items():
                    st.session_state.imported_correlations[name] = {
                        'description': scenario['description'],
                        'matrix': np.array(scenario['matrix']),
                        'assets': import_data.get('asset_list', [])
                    }
            
            return True
        
        except Exception as e:
            st.error(f"Error importing correlation config: {str(e)}")
            return False
    
    def validate_correlation_matrix(self, matrix):
        """
        Validate correlation matrix properties
        
        Args:
            matrix: numpy array to validate
            
        Returns:
            dict with validation results
        """
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Check if matrix is square
            if matrix.shape[0] != matrix.shape[1]:
                validation_results['is_valid'] = False
                validation_results['errors'].append("Matrix is not square")
                return validation_results
            
            # Check if symmetric
            if not np.allclose(matrix, matrix.T, rtol=1e-10):
                validation_results['is_valid'] = False
                validation_results['errors'].append("Matrix is not symmetric")
            
            # Check diagonal elements
            if not np.allclose(np.diag(matrix), 1.0, rtol=1e-10):
                validation_results['is_valid'] = False
                validation_results['errors'].append("Diagonal elements are not 1.0")
            
            # Check correlation bounds
            if not np.all((matrix >= -1.0) & (matrix <= 1.0)):
                validation_results['is_valid'] = False
                validation_results['errors'].append("Correlation values outside [-1, 1] range")
            
            # Check if positive semi-definite
            eigenvals = np.linalg.eigvals(matrix)
            if np.any(eigenvals < -1e-8):
                validation_results['is_valid'] = False
                validation_results['errors'].append("Matrix is not positive semi-definite")
            
            # Warnings for unusual correlations
            upper_triangle = np.triu(matrix, k=1)
            correlations = upper_triangle[upper_triangle != 0]
            
            if len(correlations) > 0:
                if np.any(np.abs(correlations) > 0.9):
                    validation_results['warnings'].append("Some correlations are very high (>0.9)")
                
                if np.mean(np.abs(correlations)) > 0.6:
                    validation_results['warnings'].append("Average correlation is quite high")
        
        except Exception as e:
            validation_results['is_valid'] = False
            validation_results['errors'].append(f"Validation error: {str(e)}")
        
        return validation_results
