"""
Enhanced Monte Carlo simulation engine with asset correlation support - FIXED VERSION
CORRECTED: Eliminati tutti i problemi di calcolo che causavano successo rate troppo alti
"""

import numpy as np
from typing import List, Dict, Tuple
from translations import get_text


class CorrelatedMonteCarloSimulator:
    """Monte Carlo simulation engine with asset correlation support - FIXED"""
    
    def __init__(self):
        self.results = None
        self.use_enhanced_tax = True
        self.correlation_matrix = None
        
    def set_correlation_matrix(self, assets_list, correlation_matrix=None):
        """
        Set correlation matrix for assets
        
        Args:
            assets_list: List of asset names in order
            correlation_matrix: 2D array of correlations, if None uses default
        """
        n_assets = len(assets_list)
        
        if correlation_matrix is None:
            # Default correlation matrix based on typical asset relationships
            self.correlation_matrix = self._get_default_correlation_matrix(assets_list)
        else:
            # Validate provided correlation matrix
            if correlation_matrix.shape != (n_assets, n_assets):
                raise ValueError(f"Correlation matrix must be {n_assets}x{n_assets}")
            
            # Ensure matrix is symmetric and positive semi-definite
            correlation_matrix = (correlation_matrix + correlation_matrix.T) / 2
            
            # Check if positive semi-definite, if not use nearest valid matrix
            eigenvals = np.linalg.eigvals(correlation_matrix)
            if np.any(eigenvals < -1e-8):
                print("Warning: Correlation matrix is not positive semi-definite. Using nearest valid matrix.")
                correlation_matrix = self._nearest_correlation_matrix(correlation_matrix)
            
            self.correlation_matrix = correlation_matrix
    
    def _get_default_correlation_matrix(self, assets_list):
        """Generate default correlation matrix based on asset types"""
        asset_correlations = {
            # Format: (asset1, asset2): correlation
            ('Stocks', 'Bond'): -0.1,        # Slight negative correlation
            ('Stocks', 'Gold'): 0.1,         # Low positive correlation
            ('Stocks', 'REIT'): 0.7,         # High correlation (both equity-like)
            ('Stocks', 'Commodities'): 0.3,  # Moderate correlation
            ('Stocks', 'Cash'): 0.0,         # No correlation
            ('Bond', 'Gold'): 0.2,           # Low correlation
            ('Bond', 'REIT'): 0.1,           # Low correlation
            ('Bond', 'Commodities'): 0.1,    # Low correlation
            ('Bond', 'Cash'): 0.3,           # Moderate correlation
            ('Gold', 'REIT'): 0.2,           # Low correlation
            ('Gold', 'Commodities'): 0.4,    # Moderate correlation
            ('Gold', 'Cash'): 0.1,           # Low correlation
            ('REIT', 'Commodities'): 0.3,    # Moderate correlation
            ('REIT', 'Cash'): 0.0,           # No correlation
            ('Commodities', 'Cash'): 0.0,    # No correlation
        }
        
        n_assets = len(assets_list)
        correlation_matrix = np.eye(n_assets)  # Start with identity matrix
        
        for i, asset1 in enumerate(assets_list):
            for j, asset2 in enumerate(assets_list):
                if i != j:
                    # Try both orders of asset pairs
                    corr = asset_correlations.get((asset1, asset2))
                    if corr is None:
                        corr = asset_correlations.get((asset2, asset1))
                    
                    if corr is not None:
                        correlation_matrix[i, j] = corr
                    else:
                        # Default correlation for unknown pairs
                        if 'UserAsset' in asset1 or 'UserAsset' in asset2:
                            correlation_matrix[i, j] = 0.2  # Low default correlation
                        else:
                            correlation_matrix[i, j] = 0.1  # Very low default
        
        return correlation_matrix
    
    def _nearest_correlation_matrix(self, A):
        """Find the nearest positive semi-definite correlation matrix"""
        # Simple method: clip eigenvalues to be non-negative
        eigenvals, eigenvecs = np.linalg.eigh(A)
        eigenvals = np.maximum(eigenvals, 1e-8)  # Ensure positive
        
        # Reconstruct matrix
        result = eigenvecs @ np.diag(eigenvals) @ eigenvecs.T
        
        # Ensure diagonal is 1 (correlation property)
        diag_sqrt = np.sqrt(np.diag(result))
        result = result / np.outer(diag_sqrt, diag_sqrt)
        
        return result
    
    def _generate_correlated_returns(self, mean_returns, volatilities, correlation_matrix, n_simulations):
        """
        Generate correlated asset returns using multivariate normal distribution
        
        Args:
            mean_returns: List of mean returns for each asset
            volatilities: List of volatilities for each asset
            correlation_matrix: Asset correlation matrix
            n_simulations: Number of return scenarios to generate
            
        Returns:
            Array of shape (n_simulations, n_assets) with correlated returns
        """
        n_assets = len(mean_returns)
        
        # Create covariance matrix from correlation matrix and volatilities
        vol_matrix = np.outer(volatilities, volatilities)
        covariance_matrix = correlation_matrix * vol_matrix
        
        # Generate correlated random returns
        correlated_returns = np.random.multivariate_normal(
            mean=mean_returns,
            cov=covariance_matrix,
            size=n_simulations
        )
        
        return correlated_returns
    
    def run_simulation(self, accumulation_assets, retirement_assets, initial_amount, years_to_retirement, 
                      years_retired, annual_contribution, adjust_contribution_inflation,
                      inflation, withdrawal, capital_gains_tax_rate, n_simulations,
                      use_real_withdrawal=True, progress_bar=None, status_text=None, lang='en'):
        """
        Standard interface compatible with MonteCarloSimulator - delegates to correlation version
        """
        return self.run_simulation_with_correlation(
            accumulation_assets, retirement_assets, initial_amount, years_to_retirement, 
            years_retired, annual_contribution, adjust_contribution_inflation,
            inflation, withdrawal, capital_gains_tax_rate, n_simulations, 
            use_real_withdrawal, progress_bar, status_text, lang
        )

    def run_simulation_with_correlation(self, accumulation_assets, retirement_assets, 
                                      initial_amount, years_to_retirement, years_retired,
                                      annual_contribution, adjust_contribution_inflation,
                                      inflation, withdrawal, capital_gains_tax_rate, 
                                      n_simulations, use_real_withdrawal=True, progress_bar=None, status_text=None, lang='en'):
        """
        Run Monte Carlo simulation with correlated asset returns - FIXED VERSION
        """
        
        # Prepare asset data
        acc_asset_names = [asset['name'] for asset in accumulation_assets]
        ret_asset_names = [asset['name'] for asset in retirement_assets]
        
        # Set up correlation matrices
        acc_correlation_matrix = None
        ret_correlation_matrix = None
        
        if self.correlation_matrix is not None:
            # Use the same correlation structure for both phases
            # This assumes the same asset universe
            all_asset_names = list(set(acc_asset_names + ret_asset_names))
            
            # Create sub-matrices for each phase
            acc_indices = [all_asset_names.index(name) for name in acc_asset_names if name in all_asset_names]
            ret_indices = [all_asset_names.index(name) for name in ret_asset_names if name in all_asset_names]
            
            if len(acc_indices) == len(acc_asset_names):
                acc_correlation_matrix = self.correlation_matrix[np.ix_(acc_indices, acc_indices)]
            if len(ret_indices) == len(ret_asset_names):
                ret_correlation_matrix = self.correlation_matrix[np.ix_(ret_indices, ret_indices)]
        
        # If no correlation matrix set, create default ones
        if acc_correlation_matrix is None:
            temp_sim = CorrelatedMonteCarloSimulator()
            temp_sim.set_correlation_matrix(acc_asset_names)
            acc_correlation_matrix = temp_sim.correlation_matrix
            
        if ret_correlation_matrix is None:
            temp_sim = CorrelatedMonteCarloSimulator()
            temp_sim.set_correlation_matrix(ret_asset_names)
            ret_correlation_matrix = temp_sim.correlation_matrix
        
        # Prepare data arrays
        acc_mean_returns = [asset['return'] / 100 for asset in accumulation_assets]
        acc_volatilities = [asset['volatility'] / 100 for asset in accumulation_assets]
        acc_allocations = [asset['allocation'] / 100 for asset in accumulation_assets]
        acc_min_returns = [asset['min_return'] / 100 for asset in accumulation_assets]
        acc_max_returns = [asset['max_return'] / 100 for asset in accumulation_assets]
        acc_ters = [asset['ter'] / 100 for asset in accumulation_assets]
        
        ret_mean_returns = [asset['return'] / 100 for asset in retirement_assets]
        ret_volatilities = [asset['volatility'] / 100 for asset in retirement_assets]
        ret_allocations = [asset['allocation'] / 100 for asset in retirement_assets]
        ret_min_returns = [asset['min_return'] / 100 for asset in retirement_assets]
        ret_max_returns = [asset['max_return'] / 100 for asset in retirement_assets]
        ret_ters = [asset['ter'] / 100 for asset in retirement_assets]
        
        # Results storage
        accumulation_balances = []
        accumulation_balances_nominal = []
        final_results = []
        detailed_tax_results = []
        real_withdrawal_amounts = []
        
        for sim in range(n_simulations):
            # Update progress with safe status_text handling
            if progress_bar and sim % 100 == 0:
                progress_bar.progress((sim + 1) / n_simulations)
                if status_text and hasattr(status_text, 'text'):
                    status_text.text(get_text('simulation_step', lang).format(sim + 1, n_simulations))
            
            # Run single simulation with correlation - FIXED
            result = self._run_single_simulation_with_correlation_fixed(
                acc_mean_returns, acc_volatilities, acc_allocations, acc_min_returns, 
                acc_max_returns, acc_ters, acc_correlation_matrix,
                ret_mean_returns, ret_volatilities, ret_allocations, ret_min_returns, 
                ret_max_returns, ret_ters, ret_correlation_matrix,
                initial_amount, years_to_retirement, years_retired,
                annual_contribution, adjust_contribution_inflation, inflation, withdrawal, 
                capital_gains_tax_rate, use_real_withdrawal
            )
            
            accumulation_balances.append(result['accumulation_real'])
            accumulation_balances_nominal.append(result['accumulation_nominal'])
            final_results.append(result['final'])
            detailed_tax_results.append(result['tax_details'])
            real_withdrawal_amounts.append(result.get('real_withdrawal', withdrawal))
        
        # Update final progress with safe status_text handling
        if progress_bar:
            progress_bar.progress(1.0)
            if status_text and hasattr(status_text, 'text'):
                status_text.text(get_text('simulation_completed', lang))
        
        self.results = {
            'accumulation': accumulation_balances,
            'accumulation_nominal': accumulation_balances_nominal,
            'final': final_results,
            'real_withdrawal': real_withdrawal_amounts,
            'tax_details': detailed_tax_results,
            'use_real_withdrawal': use_real_withdrawal
        }
        
        return self.results
    
    def _run_single_simulation_with_correlation_fixed(self, acc_mean_returns, acc_volatilities, acc_allocations, 
                                              acc_min_returns, acc_max_returns, acc_ters, acc_correlation_matrix,
                                              ret_mean_returns, ret_volatilities, ret_allocations,
                                              ret_min_returns, ret_max_returns, ret_ters, ret_correlation_matrix,
                                              initial_amount, years_to_retirement, years_retired, 
                                              annual_contribution, adjust_contribution_inflation, 
                                              inflation, base_withdrawal, capital_gains_tax_rate, use_real_withdrawal):
        """Run a single simulation with correlated returns - FIXED VERSION"""
        
        try:
            from tax_engine import EnhancedTaxEngine
        except ImportError:
            # Fallback to simple method if tax_engine is not available
            return self._run_single_simulation_simple_with_correlation_fixed(
                acc_mean_returns, acc_volatilities, acc_allocations, acc_min_returns, 
                acc_max_returns, acc_ters, acc_correlation_matrix,
                ret_mean_returns, ret_volatilities, ret_allocations, ret_min_returns, 
                ret_max_returns, ret_ters, ret_correlation_matrix,
                initial_amount, years_to_retirement, years_retired,
                annual_contribution, adjust_contribution_inflation, inflation, base_withdrawal, 
                capital_gains_tax_rate, use_real_withdrawal
            )
        
        # Initialize tax engine
        tax_engine = EnhancedTaxEngine(capital_gains_tax_rate)
        
        # Add initial contribution
        if initial_amount > 0:
            tax_engine.add_contribution(initial_amount, 0)
        
        current_contribution = annual_contribution
        
        # Generate correlated returns for accumulation phase
        acc_correlated_returns = self._generate_correlated_returns(
            acc_mean_returns, acc_volatilities, acc_correlation_matrix, 
            int(years_to_retirement)
        )
        
        # Accumulation phase with correlated returns
        for year in range(int(years_to_retirement)):
            # Use pre-generated correlated returns for this year
            annual_returns = acc_correlated_returns[year]
            
            # Apply caps and TER
            capped_returns = [max(min(annual_returns[i], acc_max_returns[i]), acc_min_returns[i]) 
                            for i in range(len(annual_returns))]
            net_returns = [capped_returns[i] - acc_ters[i] for i in range(len(capped_returns))]
            annual_return_nominal = sum(net_returns[i] * acc_allocations[i] 
                                      for i in range(len(net_returns)))
            
            # Apply returns to tax engine
            tax_engine.apply_returns(annual_return_nominal, year + 1)
            
            # Add contribution
            if current_contribution > 0:
                tax_engine.add_contribution(current_contribution, year + 1)
            
            if adjust_contribution_inflation:
                current_contribution *= (1 + inflation)
        
        # Get portfolio status at end of accumulation
        portfolio_status = tax_engine.get_portfolio_status()
        accumulation_nominal = portfolio_status['total_portfolio_value']
        
        # Convert to real value
        balance_real = accumulation_nominal / ((1 + inflation) ** years_to_retirement)
        accumulation_real = balance_real
        
        # Generate correlated returns for retirement phase
        ret_correlated_returns = self._generate_correlated_returns(
            ret_mean_returns, ret_volatilities, ret_correlation_matrix, 
            int(years_retired)
        )
        
        # FIXED: Retirement phase with corrected withdrawal calculations
        annual_taxes_paid = []
        annual_net_withdrawals = []
        annual_gross_withdrawals = []
        annual_capital_gains = []
        total_real_withdrawals = 0
        withdrawal_count = 0
        
        for year in range(int(years_retired)):
            # Use pre-generated correlated returns for this year
            if year < len(ret_correlated_returns):
                annual_returns = ret_correlated_returns[year]
            else:
                # Fallback to independent returns if we run out
                annual_returns = [np.random.normal(ret_mean_returns[i], ret_volatilities[i]) 
                                for i in range(len(ret_mean_returns))]
            
            # Apply caps and TER
            capped_returns = [max(min(annual_returns[i], ret_max_returns[i]), ret_min_returns[i]) 
                            for i in range(len(annual_returns))]
            net_returns = [capped_returns[i] - ret_ters[i] for i in range(len(capped_returns))]
            annual_return_nominal = sum(net_returns[i] * ret_allocations[i] 
                                      for i in range(len(net_returns)))
            
            # FIXED: Calculate real return correctly
            annual_return_real = (1 + annual_return_nominal) / (1 + inflation) - 1
            
            # Apply returns to portfolio
            tax_engine.apply_returns(annual_return_real, years_to_retirement + year + 1)
            
            # Check current portfolio status
            current_status = tax_engine.get_portfolio_status()
            current_portfolio_value = current_status['total_portfolio_value']
            
            if current_portfolio_value <= 0:
                break
            
            # FIXED: Calculate withdrawal amount based on real vs nominal choice (same logic as simulation_engine.py)
            if use_real_withdrawal:
                # REAL withdrawal: Maintain constant purchasing power
                # Total inflation years from today = years_to_retirement + current_year
                total_inflation_years = years_to_retirement + year
                withdrawal_amount = base_withdrawal * ((1 + inflation) ** total_inflation_years)
            else:
                # NOMINAL withdrawal: Keep same amount every year (no adjustment)
                withdrawal_amount = base_withdrawal
            
            # Limit to available portfolio
            actual_withdrawal_amount = min(withdrawal_amount, current_portfolio_value)
            
            # Execute withdrawal with tax calculation
            withdrawal_result = tax_engine.calculate_withdrawal_tax(actual_withdrawal_amount)
            
            annual_gross_withdrawals.append(withdrawal_result['gross_withdrawal'])
            annual_net_withdrawals.append(withdrawal_result['net_withdrawal'])
            annual_taxes_paid.append(withdrawal_result['taxes_owed'])
            annual_capital_gains.append(withdrawal_result['capital_gains'])
            
            # Track withdrawals for statistics
            total_real_withdrawals += withdrawal_result['net_withdrawal']
            withdrawal_count += 1
            
            # Check if portfolio is depleted
            final_status = tax_engine.get_portfolio_status()
            if final_status['total_portfolio_value'] <= 0:
                break
        
        # Get final portfolio status
        final_status = tax_engine.get_portfolio_status()
        final_portfolio_value = final_status['total_portfolio_value']
        
        # Calculate average real withdrawal
        avg_real_withdrawal = total_real_withdrawals / withdrawal_count if withdrawal_count > 0 else base_withdrawal
        
        # Prepare tax details
        tax_details = {
            'total_contributions': final_status['total_contributions'],
            'total_withdrawals': final_status['total_withdrawals'],
            'total_taxes_paid': final_status['total_taxes_paid'],
            'total_capital_gains_realized': final_status.get('total_capital_gains_realized', 0),
            'average_annual_tax': np.mean(annual_taxes_paid) if annual_taxes_paid else 0,
            'total_years_with_withdrawals': len(annual_taxes_paid),
            'use_real_withdrawal': use_real_withdrawal,
            'base_withdrawal': base_withdrawal,
            'final_withdrawal': (base_withdrawal * ((1 + inflation) ** (years_to_retirement + years_retired - 1)) 
                               if use_real_withdrawal and years_retired > 0 else base_withdrawal)
        }
        
        return {
            'accumulation_nominal': accumulation_nominal,
            'accumulation_real': accumulation_real,
            'final': final_portfolio_value,
            'real_withdrawal': avg_real_withdrawal,
            'tax_details': tax_details
        }
    
    def _run_single_simulation_simple_with_correlation_fixed(self, acc_mean_returns, acc_volatilities, acc_allocations, 
                                                     acc_min_returns, acc_max_returns, acc_ters, acc_correlation_matrix,
                                                     ret_mean_returns, ret_volatilities, ret_allocations,
                                                     ret_min_returns, ret_max_returns, ret_ters, ret_correlation_matrix,
                                                     initial_amount, years_to_retirement, years_retired, 
                                                     annual_contribution, adjust_contribution_inflation, 
                                                     inflation, base_withdrawal, capital_gains_tax_rate, use_real_withdrawal):
        """Simplified simulation with correlation - FIXED VERSION"""
        
        balance_nominal = initial_amount
        total_deposited = initial_amount
        current_contribution = annual_contribution
        
        # Generate correlated returns for accumulation phase
        acc_correlated_returns = self._generate_correlated_returns(
            acc_mean_returns, acc_volatilities, acc_correlation_matrix, 
            int(years_to_retirement)
        )
        
        # Accumulation phase
        for year in range(int(years_to_retirement)):
            annual_returns = acc_correlated_returns[year]
            capped_returns = [max(min(annual_returns[i], acc_max_returns[i]), acc_min_returns[i]) 
                            for i in range(len(annual_returns))]
            net_returns = [capped_returns[i] - acc_ters[i] for i in range(len(capped_returns))]
            annual_return_nominal = sum(net_returns[i] * acc_allocations[i] 
                                      for i in range(len(net_returns)))
            
            balance_nominal *= (1 + annual_return_nominal)
            balance_nominal += current_contribution
            total_deposited += current_contribution
            
            if adjust_contribution_inflation:
                current_contribution *= (1 + inflation)
        
        accumulation_nominal = balance_nominal
        balance_real = balance_nominal / ((1 + inflation) ** years_to_retirement)
        accumulation_real = balance_real
        
        # Calculate tax effects
        total_deposited_real = total_deposited / ((1 + inflation) ** years_to_retirement)
        capital_gains = max(0, accumulation_real - total_deposited_real)
        capital_gains_percentage = capital_gains / accumulation_real if accumulation_real > 0 else 0
        
        tax_rate_decimal = capital_gains_tax_rate / 100
        effective_tax_rate = tax_rate_decimal * capital_gains_percentage
        
        # Generate correlated returns for retirement phase
        ret_correlated_returns = self._generate_correlated_returns(
            ret_mean_returns, ret_volatilities, ret_correlation_matrix, 
            int(years_retired)
        )
        
        # FIXED: Retirement phase with same logic as simulation_engine.py
        balance = balance_real
        total_real_withdrawals = 0
        withdrawal_count = 0
        
        for year in range(int(years_retired)):
            if year < len(ret_correlated_returns):
                annual_returns = ret_correlated_returns[year]
            else:
                annual_returns = [np.random.normal(ret_mean_returns[i], ret_volatilities[i]) 
                                for i in range(len(ret_mean_returns))]
            
            capped_returns = [max(min(annual_returns[i], ret_max_returns[i]), ret_min_returns[i]) 
                            for i in range(len(ret_mean_returns))]
            net_returns = [capped_returns[i] - ret_ters[i] for i in range(len(capped_returns))]
            annual_return_nominal = sum(net_returns[i] * ret_allocations[i] 
                                      for i in range(len(net_returns)))
            
            # FIXED: Calculate real return correctly
            annual_return_real = (1 + annual_return_nominal) / (1 + inflation) - 1
            
            balance *= (1 + annual_return_real)
            
            # FIXED: Calculate withdrawal amount based on real vs nominal choice (same logic as simulation_engine.py)
            if use_real_withdrawal:
                # REAL withdrawal: Maintain constant purchasing power
                # Total inflation years from today = years_to_retirement + current_year
                total_inflation_years = years_to_retirement + year
                withdrawal_amount = base_withdrawal * ((1 + inflation) ** total_inflation_years)
            else:
                # NOMINAL withdrawal: Keep same amount every year (no adjustment)
                withdrawal_amount = base_withdrawal
            
            # Apply tax effects to withdrawal
            real_withdrawal_multiplier = 1 - effective_tax_rate
            after_tax_withdrawal = withdrawal_amount * real_withdrawal_multiplier
            
            balance -= after_tax_withdrawal
            
            # Track withdrawals for statistics
            total_real_withdrawals += after_tax_withdrawal
            withdrawal_count += 1
            
            if balance < 0:
                balance = 0
                break
        
        # Calculate average real withdrawal
        avg_real_withdrawal = total_real_withdrawals / withdrawal_count if withdrawal_count > 0 else base_withdrawal
        
        return {
            'accumulation_nominal': accumulation_nominal,
            'accumulation_real': accumulation_real,
            'final': balance,
            'real_withdrawal': avg_real_withdrawal,
            'tax_details': {
                'use_real_withdrawal': use_real_withdrawal,
                'base_withdrawal': base_withdrawal,
                'final_withdrawal': (base_withdrawal * ((1 + inflation) ** (years_to_retirement + years_retired - 1)) 
                                   if use_real_withdrawal and years_retired > 0 else base_withdrawal),
                'effective_tax_rate': effective_tax_rate,
                'total_years_with_withdrawals': withdrawal_count
            }
        }
    
    # Include all the other methods from the original class
    def get_correlation_matrix(self):
        """Get the current correlation matrix"""
        return self.correlation_matrix
    
    def calculate_success_rate(self):
        """Calculate success rate from simulation results"""
        if not self.results:
            return 0
        return sum(r > 0 for r in self.results['final']) / len(self.results['final']) * 100
    
    def get_statistics(self):
        """Get comprehensive statistics from simulation results"""
        if not self.results:
            return None
        
        stats = {}
        for phase in ['accumulation', 'accumulation_nominal', 'final', 'real_withdrawal']:
            if phase in self.results:
                data = self.results[phase]
                stats[phase] = {
                    'mean': np.mean(data),
                    'median': np.percentile(data, 50),
                    'p25': np.percentile(data, 25),
                    'p75': np.percentile(data, 75),
                    'p10': np.percentile(data, 10),
                    'p90': np.percentile(data, 90)
                }
        
        stats['success_rate'] = self.calculate_success_rate()
        return stats

    def get_tax_analysis(self) -> Dict:
        """Get tax analysis from simulation results - compatible with simulation_engine.py"""
        if not self.results or 'tax_details' not in self.results:
            return {}
        
        tax_data = self.results['tax_details']
        valid_tax_data = [detail for detail in tax_data if detail]
        
        if not valid_tax_data:
            return {}
        
        # Check if we have enhanced tax details
        has_enhanced_details = any('total_taxes_paid' in detail for detail in valid_tax_data)
        
        if has_enhanced_details:
            total_taxes_paid = [detail.get('total_taxes_paid', 0) for detail in valid_tax_data]
            total_withdrawals = [detail.get('total_withdrawals', 0) for detail in valid_tax_data]
            
            effective_tax_rates = []
            for i, detail in enumerate(valid_tax_data):
                if total_withdrawals[i] > 0:
                    effective_rate = (detail.get('total_taxes_paid', 0) / total_withdrawals[i]) * 100
                    effective_tax_rates.append(effective_rate)
                else:
                    effective_tax_rates.append(0.0)
            
            return {
                'total_taxes_statistics': {
                    'mean': np.mean(total_taxes_paid),
                    'median': np.percentile(total_taxes_paid, 50),
                    'min': np.min(total_taxes_paid),
                    'max': np.max(total_taxes_paid),
                    'std': np.std(total_taxes_paid)
                },
                'effective_tax_rate_statistics': {
                    'mean': np.mean(effective_tax_rates),
                    'median': np.percentile(effective_tax_rates, 50),
                    'min': np.min(effective_tax_rates),
                    'max': np.max(effective_tax_rates),
                    'std': np.std(effective_tax_rates)
                },
                'withdrawal_info': {
                    'use_real_withdrawal': valid_tax_data[0].get('use_real_withdrawal', False),
                    'base_withdrawal': valid_tax_data[0].get('base_withdrawal', 0),
                    'avg_final_withdrawal': np.mean([detail.get('final_withdrawal', 0) for detail in valid_tax_data])
                }
            }
        else:
            effective_rates = [detail.get('effective_tax_rate', 0) * 100 for detail in valid_tax_data]
            
            return {
                'effective_tax_rate_statistics': {
                    'mean': np.mean(effective_rates),
                    'median': np.percentile(effective_rates, 50),
                    'min': np.min(effective_rates),
                    'max': np.max(effective_rates),
                    'std': np.std(effective_rates)
                },
                'withdrawal_info': {
                    'use_real_withdrawal': valid_tax_data[0].get('use_real_withdrawal', False),
                    'base_withdrawal': valid_tax_data[0].get('base_withdrawal', 0),
                    'avg_final_withdrawal': np.mean([detail.get('final_withdrawal', 0) for detail in valid_tax_data])
                }
            }
