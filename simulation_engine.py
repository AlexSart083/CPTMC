"""
Enhanced Monte Carlo simulation engine with detailed capital gains taxation
"""

import numpy as np
from typing import List, Dict, Tuple
from translations import get_text


class MonteCarloSimulator:
    """Monte Carlo simulation engine with detailed capital gains tax tracking"""
    
    def __init__(self):
        self.results = None
        self.use_enhanced_tax = True  # Flag to enable enhanced tax calculation
    
    def run_simulation(self, accumulation_assets, retirement_assets, initial_amount, years_to_retirement, 
                      years_retired, annual_contribution, adjust_contribution_inflation,
                      inflation, withdrawal, capital_gains_tax_rate, n_simulations,
                      progress_bar=None, status_text=None, lang='en'):
        """
        Run Monte Carlo simulation with enhanced capital gains taxation
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
        detailed_tax_results = []  # New: detailed tax information
        real_withdrawal_amounts = []  # Keep for compatibility
        
        for sim in range(n_simulations):
            # Update progress
            if progress_bar and sim % 100 == 0:
                progress_bar.progress((sim + 1) / n_simulations)
                if status_text:
                    status_text.text(get_text('simulation_step', lang).format(sim + 1, n_simulations))
            
            # Choose simulation method based on flag
            if self.use_enhanced_tax:
                result = self._run_single_simulation_with_detailed_tax(
                    acc_mean_returns, acc_volatilities, acc_allocations, acc_min_returns, acc_max_returns, acc_ters,
                    ret_mean_returns, ret_volatilities, ret_allocations, ret_min_returns, ret_max_returns, ret_ters,
                    initial_amount, years_to_retirement, years_retired,
                    annual_gross_withdrawals.append(withdrawal_result['gross_withdrawal'])
            annual_net_withdrawals.append(withdrawal_result['net_withdrawal'])
            annual_taxes_paid.append(withdrawal_result['taxes_owed'])
            annual_capital_gains.append(withdrawal_result['capital_gains'])
            
            # DEBUGGING: Check for unreasonable values
            if withdrawal_result['taxes_owed'] > withdrawal_result['gross_withdrawal']:
                print(f"ERROR: Taxes ({withdrawal_result['taxes_owed']:.2f}) > Withdrawal ({withdrawal_result['gross_withdrawal']:.2f})")
                print(f"Capital gains: {withdrawal_result['capital_gains']:.2f}, Tax rate: {capital_gains_tax_rate}%")
            
            # Check if portfolio is depleted after withdrawal
            final_status = tax_engine.get_portfolio_status()
            if final_status['total_portfolio_value'] <= 0:
                break
        
        # Get final portfolio status
        final_status = tax_engine.get_portfolio_status()
        final_portfolio_value = final_status['total_portfolio_value']
        
        # Calculate average real withdrawal for compatibility
        avg_real_withdrawal = np.mean(annual_net_withdrawals) if annual_net_withdrawals else withdrawal
        
        # Sanity checks
        total_taxes = sum(annual_taxes_paid)
        total_gains = sum(annual_capital_gains)
        
        # CORRECTED: Ensure taxes don't exceed reasonable bounds
        max_reasonable_taxes = total_gains * (capital_gains_tax_rate / 100)
        if total_taxes > max_reasonable_taxes * 1.1:  # 10% tolerance
            print(f"WARNING: Total taxes ({total_taxes:.0f}) seem high for gains ({total_gains:.0f})")
        
        # Prepare detailed tax information
        tax_details = {
            'total_contributions': final_status['total_contributions'],
            'total_withdrawals': final_status['total_withdrawals'],
            'total_taxes_paid': final_status['total_taxes_paid'],
            'total_capital_gains_realized': final_status.get('total_capital_gains_realized', 0),
            'annual_taxes': annual_taxes_paid,
            'annual_net_withdrawals': annual_net_withdrawals,
            'annual_gross_withdrawals': annual_gross_withdrawals,
            'annual_capital_gains': annual_capital_gains,
            'final_unrealized_gains': final_status['unrealized_capital_gains'],
            'average_annual_tax': np.mean(annual_taxes_paid) if annual_taxes_paid else 0,
            'total_years_with_withdrawals': len(annual_taxes_paid)
        }
        
        return {
            'accumulation_nominal': accumulation_nominal,
            'accumulation_real': accumulation_real,
            'final': final_portfolio_value,
            'real_withdrawal': avg_real_withdrawal,  # For compatibility
            'tax_details': tax_details
        }contribution, adjust_contribution_inflation, inflation, withdrawal, 
                    capital_gains_tax_rate
                )
                detailed_tax_results.append(result['tax_details'])
            else:
                # Fallback to simple method for compatibility
                result = self._run_single_simulation_with_simple_tax(
                    acc_mean_returns, acc_volatilities, acc_allocations, acc_min_returns, acc_max_returns, acc_ters,
                    ret_mean_returns, ret_volatilities, ret_allocations, ret_min_returns, ret_max_returns, ret_ters,
                    initial_amount, years_to_retirement, years_retired,
                    annual_contribution, adjust_contribution_inflation, inflation, withdrawal, 
                    capital_gains_tax_rate
                )
                detailed_tax_results.append({})  # Empty tax details for simple method
            
            accumulation_balances.append(result['accumulation_real'])
            accumulation_balances_nominal.append(result['accumulation_nominal'])
            final_results.append(result['final'])
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
            'tax_details': detailed_tax_results  # New: detailed tax information
        }
        
        return self.results
    
    def _run_single_simulation_with_detailed_tax(self, acc_mean_returns, acc_volatilities, acc_allocations, 
                                               acc_min_returns, acc_max_returns, acc_ters,
                                               ret_mean_returns, ret_volatilities, ret_allocations,
                                               ret_min_returns, ret_max_returns, ret_ters,
                                               initial_amount, years_to_retirement, years_retired, 
                                               annual_contribution, adjust_contribution_inflation, 
                                               inflation, withdrawal, capital_gains_tax_rate):
        """Run a single simulation with detailed capital gains tax calculation - CORRECTED"""
        
        try:
            from tax_engine import EnhancedTaxEngine
        except ImportError:
            # Fallback to simple method if tax_engine is not available
            return self._run_single_simulation_with_simple_tax(
                acc_mean_returns, acc_volatilities, acc_allocations, acc_min_returns, acc_max_returns, acc_ters,
                ret_mean_returns, ret_volatilities, ret_allocations, ret_min_returns, ret_max_returns, ret_ters,
                initial_amount, years_to_retirement, years_retired,
                annual_contribution, adjust_contribution_inflation, inflation, withdrawal, 
                capital_gains_tax_rate
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
        
        # Convert to real value
        balance_real = accumulation_nominal / ((1 + inflation) ** years_to_retirement)
        accumulation_real = balance_real
        
        # Retirement phase with detailed tax calculations
        annual_taxes_paid = []
        annual_net_withdrawals = []
        annual_gross_withdrawals = []
        annual_capital_gains = []
        
        for year in range(int(years_retired)):
            # Calculate returns for retirement phase
            annual_returns = [np.random.normal(ret_mean_returns[i], ret_volatilities[i]) 
                            for i in range(len(ret_mean_returns))]
            capped_returns = [max(min(annual_returns[i], ret_max_returns[i]), ret_min_returns[i]) 
                            for i in range(len(ret_mean_returns))]
            net_returns = [capped_returns[i] - ret_ters[i] for i in range(len(capped_returns))]
            annual_return_nominal = sum(net_returns[i] * ret_allocations[i] 
                                      for i in range(len(net_returns)))
            
            # Calculate real return
            annual_return_real = annual_return_nominal - inflation
            
            # Apply returns to portfolio
            tax_engine.apply_returns(annual_return_real, years_to_retirement + year + 1)
            
            # Check current portfolio status
            current_status = tax_engine.get_portfolio_status()
            current_portfolio_value = current_status['total_portfolio_value']
            
            if current_portfolio_value <= 0:
                # Portfolio depleted
                break
            
            # Calculate withdrawal amount (limited by available portfolio)
            actual_withdrawal_amount = min(withdrawal, current_portfolio_value)
            
            # Execute withdrawal with tax calculation
            withdrawal_result = tax_engine.calculate_withdrawal_tax(actual_withdrawal_amount)
            
            annual_gross_withdrawals.append(withdrawal_result['gross_withdrawal'])
            annual_net_withdrawals.append(withdrawal_result['net_withdrawal'])
            annual_taxes_paid.append(withdrawal_result['taxes_owed'])
            annual_capital_gains.append(withdrawal_result['capital_gains'])
            
            # DEBUGGING: Check for unreasonable values
            if withdrawal_result['taxes_owed'] > withdrawal_result['gross_withdrawal']:
                print(f"ERROR: Taxes ({withdrawal_result['taxes_owed']:.2f}) > Withdrawal ({withdrawal_result['gross_withdrawal']:.2f})")
                print(f"Capital gains: {withdrawal_result['capital_gains']:.2f}, Tax rate: {capital_gains_tax_rate}%")
            
            # Check if portfolio is depleted after withdrawal
            final_status = tax_engine.get_portfolio_status()
            if final_status['total_portfolio_value'] <= 0:
                break
        
        # Get final portfolio status
        final_status = tax_engine.get_portfolio_status()
        final_portfolio_value = final_status['total_portfolio_value']
        
        # Calculate average real withdrawal for compatibility
        avg_real_withdrawal = np.mean(annual_net_withdrawals) if annual_net_withdrawals else withdrawal
        
        # Sanity checks
        total_taxes = sum(annual_taxes_paid)
        total_gains = sum(annual_capital_gains)
        
        # CORRECTED: Ensure taxes don't exceed reasonable bounds
        max_reasonable_taxes = total_gains * (capital_gains_tax_rate / 100)
        if total_taxes > max_reasonable_taxes * 1.1:  # 10% tolerance
            print(f"WARNING: Total taxes ({total_taxes:.0f}) seem high for gains ({total_gains:.0f})")
        
        # Prepare detailed tax information
        tax_details = {
            'total_contributions': final_status['total_contributions'],
            'total_withdrawals': final_status['total_withdrawals'],
            'total_taxes_paid': final_status['total_taxes_paid'],
            'total_capital_gains_realized': final_status.get('total_capital_gains_realized', 0),
            'annual_taxes': annual_taxes_paid,
            'annual_net_withdrawals': annual_net_withdrawals,
            'annual_gross_withdrawals': annual_gross_withdrawals,
            'annual_capital_gains': annual_capital_gains,
            'final_unrealized_gains': final_status['unrealized_capital_gains'],
            'average_annual_tax': np.mean(annual_taxes_paid) if annual_taxes_paid else 0,
            'total_years_with_withdrawals': len(annual_taxes_paid)
        }
        
        return {
            'accumulation_nominal': accumulation_nominal,
            'accumulation_real': accumulation_real,
            'final': final_portfolio_value,
            'real_withdrawal': avg_real_withdrawal,  # For compatibility
            'tax_details': tax_details
        }gross_withdrawals.append(withdrawal_result['gross_withdrawal'])
            annual_net_withdrawals.append(withdrawal_result['net_withdrawal'])
            annual_taxes_paid.append(withdrawal_result['taxes_owed'])
            
            # Check if portfolio is depleted
            current_portfolio_status = tax_engine.get_portfolio_status()
            if current_portfolio_status['total_portfolio_value'] <= 0:
                break
        
        # Get final portfolio status
        final_status = tax_engine.get_portfolio_status()
        final_portfolio_value = final_status['total_portfolio_value']
        
        # Calculate average real withdrawal for compatibility
        avg_real_withdrawal = np.mean(annual_net_withdrawals) if annual_net_withdrawals else withdrawal
        
        # Prepare detailed tax information
        tax_details = {
            'total_contributions': final_status['total_contributions'],
            'total_withdrawals': final_status['total_withdrawals'],
            'total_taxes_paid': final_status['total_taxes_paid'],
            'annual_taxes': annual_taxes_paid,
            'annual_net_withdrawals': annual_net_withdrawals,
            'annual_gross_withdrawals': annual_gross_withdrawals,
            'final_unrealized_gains': final_status['unrealized_capital_gains'],
            'average_annual_tax': np.mean(annual_taxes_paid) if annual_taxes_paid else 0,
            'total_years_with_withdrawals': len(annual_taxes_paid)
        }
        
        return {
            'accumulation_nominal': accumulation_nominal,
            'accumulation_real': accumulation_real,
            'final': final_portfolio_value,
            'real_withdrawal': avg_real_withdrawal,  # For compatibility
            'tax_details': tax_details
        }
    
    def _run_single_simulation_with_simple_tax(self, acc_mean_returns, acc_volatilities, acc_allocations, 
                                              acc_min_returns, acc_max_returns, acc_ters,
                                              ret_mean_returns, ret_volatilities, ret_allocations,
                                              ret_min_returns, ret_max_returns, ret_ters,
                                              initial_amount, years_to_retirement, years_retired, 
                                              annual_contribution, adjust_contribution_inflation, 
                                              inflation, withdrawal, capital_gains_tax_rate):
        """Run a single simulation with simplified capital gains tax calculation (original method)"""
        
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
        real_withdrawal_multiplier = 1 - effective_tax_rate
        real_withdrawal = withdrawal * real_withdrawal_multiplier
        
        # Retirement phase - use the real (after-tax) withdrawal amount
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
            
            # Apply return and subtract the real (after-tax) withdrawal
            balance *= (1 + annual_return_real)
            balance -= real_withdrawal
            
            if balance < 0:
                balance = 0
                break
        
        return {
            'accumulation_nominal': accumulation_nominal,
            'accumulation_real': accumulation_real,
            'final': balance,
            'real_withdrawal': real_withdrawal
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
        
        # Calculate tax statistics if available
        if self.use_enhanced_tax and 'tax_details' in self.results:
            tax_data = self.results['tax_details']
            
            # Filter out empty tax details
            valid_tax_data = [detail for detail in tax_data if detail]
            
            if valid_tax_data:
                total_taxes = [detail['total_taxes_paid'] for detail in valid_tax_data]
                avg_annual_taxes = [detail['average_annual_tax'] for detail in valid_tax_data]
                
                stats['tax_statistics'] = {
                    'total_taxes_paid': {
                        'mean': np.mean(total_taxes),
                        'median': np.percentile(total_taxes, 50),
                        'p25': np.percentile(total_taxes, 25),
                        'p75': np.percentile(total_taxes, 75)
                    },
                    'average_annual_tax': {
                        'mean': np.mean(avg_annual_taxes),
                        'median': np.percentile(avg_annual_taxes, 50),
                        'p25': np.percentile(avg_annual_taxes, 25),
                        'p75': np.percentile(avg_annual_taxes, 75)
                    }
                }
        
        stats['success_rate'] = self.calculate_success_rate()
        
        return stats
    
    def get_tax_analysis(self) -> Dict:
        """Get detailed tax analysis from simulation results"""
        if not self.results or 'tax_details' not in self.results or not self.use_enhanced_tax:
            return {}
        
        tax_data = self.results['tax_details']
        
        # Filter out empty tax details
        valid_tax_data = [detail for detail in tax_data if detail]
        
        if not valid_tax_data:
            return {}
        
        # Calculate comprehensive tax statistics
        total_taxes_paid = [detail['total_taxes_paid'] for detail in valid_tax_data]
        total_contributions = [detail['total_contributions'] for detail in valid_tax_data]
        total_withdrawals = [detail['total_withdrawals'] for detail in valid_tax_data]
        
        # Calculate effective tax rates
        effective_tax_rates = []
        for i, detail in enumerate(valid_tax_data):
            if total_withdrawals[i] > 0:
                effective_rate = (detail['total_taxes_paid'] / total_withdrawals[i]) * 100
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
            'tax_burden_analysis': {
                'scenarios_with_high_tax': sum(1 for rate in effective_tax_rates if rate > 20),
                'scenarios_with_low_tax': sum(1 for rate in effective_tax_rates if rate < 5),
                'percentage_high_tax': (sum(1 for rate in effective_tax_rates if rate > 20) / len(effective_tax_rates)) * 100,
                'percentage_low_tax': (sum(1 for rate in effective_tax_rates if rate < 5) / len(effective_tax_rates)) * 100
            }
        }
