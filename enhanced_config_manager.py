"""
Enhanced Configuration manager with correlation support - FIXED VERSION
"""

import json
import os
import streamlit as st
import numpy as np
from translations import get_text


class EnhancedConfigManager:
    """Enhanced configuration manager with correlation support"""
    
    def __init__(self, config_file='enhanced_config.json'):  # Default to enhanced config
        self.config_file = config_file
        self._asset_profiles = None
        self._asset_characteristics = None
        self._correlation_matrix = None
        self._correlation_scenarios = None
        self._correlation_metadata = None
        self._load_config()
    
    def _load_config(self):
        """Load configuration from JSON file with enhanced features"""
        if not os.path.exists(self.config_file):
            # Try fallback to regular config.json
            fallback_config = 'config.json'
            if os.path.exists(fallback_config):
                st.warning(f"Enhanced config '{self.config_file}' not found, using fallback '{fallback_config}'")
                self.config_file = fallback_config
            else:
                lang = st.session_state.get('language', 'en')
                st.error(get_text('config_not_found', lang).format(self.config_file))
                st.stop()
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Load basic configuration
            self._asset_profiles = config['asset_profiles']
            self._asset_characteristics = config['asset_characteristics']
            
            # Load correlation data if available
            if 'correlation_matrix' in config:
                self._correlation_matrix = {
                    'assets': config['correlation_matrix']['assets'],
                    'matrix': np.array(config['correlation_matrix']['matrix'])
                }
                print(f"✅ Loaded default correlation matrix for {len(self._correlation_matrix['assets'])} assets")
            
            if 'correlation_scenarios' in config:
                self._correlation_scenarios = {}
                for scenario_name, scenario_data in config['correlation_scenarios'].items():
                    self._correlation_scenarios[scenario_name] = {
                        'description': scenario_data.get('description', f'Scenario: {scenario_name}'),
                        'market_regime': scenario_data.get('market_regime', 'unknown'),
                        'stress_level': scenario_data.get('stress_level', 'unknown'),
                        'matrix': np.array(scenario_data['matrix'])
                    }
                print(f"✅ Loaded {len(self._correlation_scenarios)} correlation scenarios: {list(self._correlation_scenarios.keys())}")
            
            # Load correlation metadata if available
            if 'correlation_metadata' in config:
                self._correlation_metadata = config['correlation_metadata']
                print("✅ Loaded correlation metadata")
            
        except Exception as e:
            lang = st.session_state.get('language', 'en')
            st.error(get_text('config_load_error', lang).format(str(e)))
            print(f"❌ Config loading error: {str(e)}")
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
    
    @property
    def correlation_metadata(self):
        """Get correlation metadata"""
        return self._correlation_metadata
    
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
            print(f"⚠️ Scenario '{scenario}' not found in correlation scenarios")
            return None
        
        if not self._correlation_matrix or 'assets' not in self._correlation_matrix:
            print("⚠️ No default correlation matrix available")
            return None
        
        # Get the full asset list from config
        config_assets = self._correlation_matrix['assets']
        scenario_matrix = self._correlation_scenarios[scenario]['matrix']
        
        print(f"🔍 Looking for assets {asset_names} in config assets {config_assets}")
        
        # Find indices for requested assets
        try:
            asset_indices = [config_assets.index(asset_name) for asset_name in asset_names]
            print(f"✅ Found asset indices: {asset_indices}")
        except ValueError as e:
            print(f"❌ Some assets not found in correlation matrix: {e}")
            return None
        
        # Extract submatrix for requested assets
        submatrix = scenario_matrix[np.ix_(asset_indices, asset_indices)]
        print(f"✅ Extracted {submatrix.shape} correlation submatrix for scenario '{scenario}'")
        return submatrix
    
    def get_correlation_scenario_info(self, scenario_name):
        """Get detailed information about a correlation scenario"""
        if not self._correlation_scenarios or scenario_name not in self._correlation_scenarios:
            return None
        
        scenario = self._correlation_scenarios[scenario_name]
        return {
            'name': scenario_name,
            'description': scenario['description'],
            'market_regime': scenario.get('market_regime', 'unknown'),
            'stress_level': scenario.get('stress_level', 'unknown'),
            'matrix_shape': scenario['matrix'].shape,
            'matrix': scenario['matrix']
        }
    
    def get_default_correlation_matrix(self, asset_names):
        """
        Generate default correlation matrix for given assets
        
        Args:
            asset_names: List of asset names
            
        Returns:
            numpy array with default correlations
        """
        # Check if we can get it from the config first
        if self._correlation_matrix and 'assets' in self._correlation_matrix:
            config_assets = self._correlation_matrix['assets']
            default_matrix = self._correlation_matrix['matrix']
            
            # Try to extract submatrix for requested assets
            try:
                asset_indices = [config_assets.index(asset_name) for asset_name in asset_names]
                submatrix = default_matrix[np.ix_(asset_indices, asset_indices)]
                print(f"✅ Using config default correlation matrix for {asset_names}")
                return submatrix
            except ValueError:
                print(f"⚠️ Some assets not in config, generating fallback correlation matrix")
        
        # Fallback: generate basic correlation matrix
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
        
        print(f"🔧 Generated fallback correlation matrix for {asset_names}")
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
        print(f"💾 Saved custom correlation matrix '{scenario_name}' for assets {asset_names}")
    
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
        
        print(f"📋 Available correlation scenarios: {scenarios}")
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
            print(f"💾 Exported correlation config to {filename}")
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
            
            print(f"📂 Imported correlation config from {filename}")
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
    
    def has_correlation_support(self):
        """Check if this config manager has correlation support"""
        return self._correlation_scenarios is not None and len(self._correlation_scenarios) > 0
    
    def debug_correlation_info(self):
        """Print debug information about correlation configuration"""
        print("\n🔍 CORRELATION DEBUG INFO:")
        print(f"📁 Config file: {self.config_file}")
        print(f"🎯 Has correlation scenarios: {self._correlation_scenarios is not None}")
        if self._correlation_scenarios:
            print(f"📊 Number of scenarios: {len(self._correlation_scenarios)}")
            print(f"📋 Scenario names: {list(self._correlation_scenarios.keys())}")
        
        print(f"🎯 Has correlation matrix: {self._correlation_matrix is not None}")
        if self._correlation_matrix:
            print(f"📊 Matrix shape: {self._correlation_matrix['matrix'].shape}")
            print(f"📋 Assets: {self._correlation_matrix['assets']}")
        
        print(f"🎯 Has correlation metadata: {self._correlation_metadata is not None}")
        print("=" * 50)
