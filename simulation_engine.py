"""
Enhanced Monte Carlo simulation engine with REAL withdrawal support - MODIFIED VERSION
Implements inflation-adjusted withdrawal amounts that maintain purchasing power
"""

import numpy as np
from typing import List, Dict, Tuple
from translations import get_text


class MonteCarloSimulator:
    """Monte Carlo simulation engine with REAL withdrawal support"""
    
    def __init__(self):
        self.results = None
        self.use_enhanced_tax = True  # Always use enhanced tax calculation
    
    def run_simulation(self, accumulation_assets, retirement_assets, initial_amount, years_to_retirement, 
                      years_retired, annual_contribution, adjust_contribution_inflation,
                      inflation, withdrawal, capital_gains_tax_rate, n_simulations,
                      use_real_withdrawal=True, progress_bar=None, status_text=None, lang='en'):
        """
        Run Monte Carlo simulation with enhanced capital gains taxation and REAL withdrawal support
        
        NEW PARAMETER:
        use_real_withdrawal: If True, withdrawal amount is adjusted annually for inflation to maintain purchasing power
        """
        
        # Prepare accumulation phase data
        acc_mean_returns = [asset['return'] / 100 for asset in accumulation_assets]
        acc_volatilities = [asset['volatility'] / 100 for asset in accumulation_assets]
        acc_allocations = [asset['allocation'] / 100 for asset in accumulation_assets]
        acc_min_returns = [asset['min_return'] / 100 for asset in accumulation_assets]
        acc_max_returns = [asset['max_return'] / 100 for asset in accumulation_assets]
        acc_ters = [asset['ter'] / 100 for asset in accumulation_assets]
        
        # Prepare retirement phase data
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
            # Update progress
            if progress_bar and sim % 100 == 0:
                progress_bar.progress((sim + 1) / n_simulations)
                if status_text:
                    status_text.text(get_text('simulation_step', lang).format(sim + 1, n_simulations))
            
            # Run single simulation with detailed tax calculation and real withdrawal
            result = self._run_single_simulation_with_real_withdrawal(
                acc_mean_returns, acc_volatilities, acc_allocations, acc_min_returns, acc_max_returns, acc_ters,
                ret_mean_returns, ret_volatilities, ret_allocations, ret_min_returns, ret_max_returns, ret_ters,
                initial_amount, years_to_retirement, years_retired,
                annual_contribution, adjust_contribution_inflation, inflation, withdrawal, 
                capital_gains_tax_rate, use_real_withdrawal
            )
            
            accumulation_balances.append(result['accumulation_real'])
            accumulation_balances_nominal.append(result['accumulation_nominal'])
            final_results.append(result['final'])
            detailed_tax_results.append(result['tax_details'])
            real_withdrawal_amounts.append(result.get('real_withdrawal', withdrawal))
        
        # Update final progress
        if progress_bar:
            progress_bar.progress(1.0)
            if status_text:
                status_text.text(get_text('simulation_completed', lang))
        
        self.results = {
            'accumulation': accumulation_balances,
            'accumulation_nominal': accumulation_balances_nominal,
            'final': final_results,
            'real_withdrawal': real_withdrawal_amounts,
            'tax_details': detailed_tax_results,
            'use_real_withdrawal': use_real_withdrawal  # Store this for results display
        }
        
        return self.results
    
    def _run_single_simulation_with_real_withdrawal(self, acc_mean_returns, acc_volatilities, acc_allocations, 
                                                  acc_min_returns, acc_max_returns, acc_ters,
                                                  ret_mean_returns, ret_volatilities, ret_allocations,
                                                  ret_min_returns, ret_max_returns, ret_ters,
                                                  initial_amount, years_to_retirement, years_retired, 
                                                  annual_contribution, adjust_contribution_inflation, 
                                                  inflation, base_withdrawal, capital_gains_tax_rate, 
                                                  use_real_withdrawal):
        """Run a single simulation with REAL withdrawal support"""
        
        try:
            from tax_engine import EnhancedTaxEngine
        except ImportError:
            # Fallback to simple method if tax_engine is not available
            return self._run_single_simulation_simple_with_real_withdrawal(
                acc_mean_returns, acc_volatilities, acc_allocations, acc_min_returns, acc_max_returns, acc_ters,
                ret_mean_returns, ret_volatilities, ret_allocations, ret_min_returns, ret_max_returns, ret_ters,
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
        
        # Accumulation phase
        for year in range(int(years_to_retirement)):
            # Calculate annual returns
            annual_returns = [np.random.normal(acc_mean_returns[i], acc_volatilities[i]) 
                            for i in range(len(acc_mean_returns))]
            capped_returns = [max(min(annual_returns[i], acc_max_returns[i]), acc_min_returns[i]) 
                            for i in range(len(acc_mean_returns))]
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
        
        # Convert to real value (adjusted for inflation during accumulation)
        balance_real = accumulation_nominal / ((1 + inflation) ** years_to_retirement)
        accumulation_real = balance_real
        
        # NEW: Initialize withdrawal tracking for real withdrawal
        current_withdrawal = base_withdrawal  # Start with user's input amount
        total_real_withdrawals = 0
        withdrawal_count = 0
        
        # Retirement phase with REAL withdrawal calculations
        annual_taxes_paid = []
        annual_net_withdrawals = []
        annual_gross_withdrawals = []
        annual_capital_gains = []
        annual_withdrawal_amounts = []  # Track actual withdrawal amounts
        
        for year in range(int(years_retired)):
            # Calculate returns for retirement phase
            annual_returns = [np.random.normal(ret_mean_returns[i], ret_volatilities[i]) 
                            for i in range(len(ret_mean_returns))]
            capped_returns = [max(min(annual_returns[i], ret_max_returns[i]), ret_min_returns[i]) 
                            for i in range(len(ret_mean_returns))]
            net_returns = [capped_returns[i] - ret_ters[i] for i in range(len(capped_returns))]
            annual_return_nominal = sum(net_returns[i] * ret_allocations[i] 
                                      for i in range(len(net_returns)))
            
            # Calculate real return (adjusted for inflation)
            annual_return_real = annual_return_nominal - inflation
            
            # Apply returns to portfolio
            tax_engine.apply_returns(annual_return_real, years_to_retirement + year + 1)
            
            # Check current portfolio status
            current_status = tax_engine.get_portfolio_status()
            current_portfolio_value = current_status['total_portfolio_value']
            
            if current_portfolio_value <= 0:
                # Portfolio depleted
                break
            
            # NEW: Calculate withdrawal amount based on real vs nominal choice
            if use_real_withdrawal:
                # REAL withdrawal: Adjust for inflation to maintain purchasing power
                # Each year, increase withdrawal by inflation rate
                if year > 0:  # Don't adjust in first year
                    current_withdrawal *= (1 + inflation)
                withdrawal_amount = current_withdrawal
            else:
                # NOMINAL withdrawal: Keep same amount every year (original behavior)
                withdrawal_amount = base_withdrawal
            
            # Limit withdrawal to available portfolio
            actual_withdrawal_amount = min(withdrawal_amount, current_portfolio_value)
            
            # Execute withdrawal with tax calculation
            withdrawal_result = tax_engine.calculate_withdrawal_tax(actual_withdrawal_amount)
            
            annual_gross_withdrawals.append(withdrawal_result['gross_withdrawal'])
            annual_net_withdrawals.append(withdrawal_result['net_withdrawal'])
            annual_taxes_paid.append(withdrawal_result['taxes_owed'])
            annual_capital_gains.append(withdrawal_result['capital_gains'])
            annual_withdrawal_amounts.append(actual_withdrawal_amount)
            
            # Track total real withdrawals for statistics
            total_real_withdrawals += withdrawal_result['net_withdrawal']
            withdrawal_count += 1
            
            # Check if portfolio is depleted after withdrawal
            final_status = tax_engine.get_portfolio_status()
            if final_status['total_portfolio_value'] <= 0:
                break
        
        # Get final portfolio status
        final_status = tax_engine.get_portfolio_status()
        final_portfolio_value = final_status['total_portfolio_value']
        
        # Calculate average real withdrawal for compatibility
        avg_real_withdrawal = total_real_withdrawals / withdrawal_count if withdrawal_count > 0 else base_withdrawal
        
        # Prepare enhanced tax information with withdrawal tracking
        tax_details = {
            'total_contributions': final_status['total_contributions'],
            'total_withdrawals': final_status['total_withdrawals'],
            'total_taxes_paid': final_status['total_taxes_paid'],
            'total_capital_gains_realized': final_status.get('total_capital_gains_realized', 0),
            'average_annual_tax': np.mean(annual_taxes_paid) if annual_taxes_paid else 0,
            'total_years_with_withdrawals': len(annual_taxes_paid),
            'withdrawal_progression': annual_withdrawal_amounts,  # NEW: Track withdrawal amounts over time
            'use_real_withdrawal': use_real_withdrawal,  # NEW: Track withdrawal type
            'base_withdrawal': base_withdrawal,  # NEW: Original user input
            'final_withdrawal': current_withdrawal if use_real_withdrawal else base_withdrawal  # NEW: Final withdrawal amount
        }
        
        return {
            'accumulation_nominal': accumulation_nominal,
            'accumulation_real': accumulation_real,
            'final': final_portfolio_value,
            'real_withdrawal': avg_real_withdrawal,
            'tax_details': tax_details
        }
    
    def _run_single_simulation_simple_with_real_withdrawal(self, acc_mean_returns, acc_volatilities, acc_allocations, 
                                                         acc_min_returns, acc_max_returns, acc_ters,
                                                         ret_mean_returns, ret_volatilities, ret_allocations,
                                                         ret_min_returns, ret_max_returns, ret_ters,
                                                         initial_amount, years_to_retirement, years_retired, 
                                                         annual_contribution, adjust_contribution_inflation, 
                                                         inflation, base_withdrawal, capital_gains_tax_rate, 
                                                         use_real_withdrawal):
        """Simplified simulation with REAL withdrawal support (fallback method)"""
        
        balance_nominal = initial_amount
        total_deposited = initial_amount
        current_contribution = annual_contribution
        
        # Accumulation phase
        for year in range(int(years_to_retirement)):
            annual_returns = [np.random.normal(acc_mean_returns[i], acc_volatilities[i]) 
                            for i in range(len(acc_mean_returns))]
            capped_returns = [max(min(annual_returns[i], acc_max_returns[i]), acc_min_returns[i]) 
                            for i in range(len(acc_mean_returns))]
            net_returns = [capped_returns[i] - acc_ters[i] for i in range(len(capped_returns))]
            annual_return_nominal = sum(net_returns[i] * acc_allocations[i] 
                                      for i in range(len(net_returns)))
            
            balance_nominal *= (1 + annual_return_nominal)
            balance_nominal += current_contribution
            total_deposited += current_contribution
            
            if adjust_contribution_inflation:
                current_contribution *= (1 + inflation)
        
        # Store nominal accumulation value
        accumulation_nominal = balance_nominal
        
        # Convert to real value
        balance_real = balance_nominal / ((1 + inflation) ** years_to_retirement)
        accumulation_real = balance_real
        
        # Calculate capital gains percentage at end of accumulation
        total_deposited_real = total_deposited / ((1 + inflation) ** years_to_retirement)
        capital_gains = max(0, accumulation_real - total_deposited_real)
        capital_gains_percentage = capital_gains / accumulation_real if accumulation_real > 0 else 0
        
        # Calculate effective tax rate on withdrawals
        tax_rate_decimal = capital_gains_tax_rate / 100
        effective_tax_rate = tax_rate_decimal * capital_gains_percentage
        
        # NEW: Initialize withdrawal for real/nominal handling
        current_withdrawal = base_withdrawal
        total_real_withdrawals = 0
        withdrawal_count = 0
        
        # Retirement phase - NEW: with real withdrawal support
        balance = balance_real
        for year in range(int(years_retired)):
            annual_returns = [np.random.normal(ret_mean_returns[i], ret_volatilities[i]) 
                            for i in range(len(ret_mean_returns))]
            capped_returns = [max(min(annual_returns[i], ret_max_returns[i]), ret_min_returns[i]) 
                            for i in range(len(ret_mean_returns))]
            net_returns = [capped_returns[i] - ret_ters[i] for i in range(len(capped_returns))]
            annual_return_nominal = sum(net_returns[i] * ret_allocations[i] 
                                      for i in range(len(net_returns)))
            
            # Calculate real return
            annual_return_real = annual_return_nominal - inflation
            
            # Apply return to balance
            balance *= (1 + annual_return_real)
            
            # NEW: Calculate withdrawal amount based on real vs nominal choice
            if use_real_withdrawal:
                # REAL withdrawal: Adjust for inflation to maintain purchasing power
                if year > 0:  # Don't adjust in first year
                    current_withdrawal *= (1 + inflation)
                withdrawal_amount = current_withdrawal
            else:
                # NOMINAL withdrawal: Keep same amount every year (original behavior)
                withdrawal_amount = base_withdrawal
            
            # Apply tax effects to withdrawal
            real_withdrawal_multiplier = 1 - effective_tax_rate
            after_tax_withdrawal = withdrawal_amount * real_withdrawal_multiplier
            
            # Subtract the after-tax withdrawal
            balance -= after_tax_withdrawal
            
            # Track withdrawals for statistics
            total_real_withdrawals += after_tax_withdrawal
            withdrawal_count += 1
            
            if balance < 0:
                balance = 0
                break
        
        # Calculate average real withdrawal
        avg_real_withdrawal = total_real_withdrawals / withdrawal_count if withdrawal_count > 0 else base_withdrawal
        
        # Prepare simplified tax details
        tax_details = {
            'use_real_withdrawal': use_real_withdrawal,
            'base_withdrawal': base_withdrawal,
            'final_withdrawal': current_withdrawal if use_real_withdrawal else base_withdrawal,
            'effective_tax_rate': effective_tax_rate,
            'total_years_with_withdrawals': withdrawal_count
        }
        
        return {
            'accumulation_nominal': accumulation_nominal,
            'accumulation_real': accumulation_real,
            'final': balance,
            'real_withdrawal': avg_real_withdrawal,
            'tax_details': tax_details
        }
    
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
        """Get simplified tax analysis from simulation results"""
        if not self.results or 'tax_details' not in self.results:
            return {}
        
        tax_data = self.results['tax_details']
        
        # Filter out empty tax details
        valid_tax_data = [detail for detail in tax_data if detail]
        
        if not valid_tax_data:
            return {}
        
        # Check if we have enhanced tax details
        has_enhanced_details = any('total_taxes_paid' in detail for detail in valid_tax_data)
        
        if has_enhanced_details:
            # Calculate enhanced tax statistics
            total_taxes_paid = [detail.get('total_taxes_paid', 0) for detail in valid_tax_data]
            total_withdrawals = [detail.get('total_withdrawals', 0) for detail in valid_tax_data]
            
            # Calculate effective tax rates
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
            # Simplified tax analysis
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
