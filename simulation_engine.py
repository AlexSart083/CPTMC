"""
Enhanced Monte Carlo simulation engine with simplified capital gains taxation
"""

import numpy as np
from translations import get_text


class MonteCarloSimulator:
    """Monte Carlo simulation engine with simplified capital gains tax"""
    
    def __init__(self):
        self.results = None
    
    def run_simulation(self, accumulation_assets, retirement_assets, initial_amount, years_to_retirement, 
                      years_retired, annual_contribution, adjust_contribution_inflation,
                      inflation, withdrawal, capital_gains_tax_rate, n_simulations,
                      progress_bar=None, status_text=None, lang='en'):
        """
        Run Monte Carlo simulation with simplified capital gains taxation
        
        Args:
            capital_gains_tax_rate: Tax rate on capital gains (as percentage, e.g., 26)
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
        
        accumulation_balances = []
        accumulation_balances_nominal = []
        final_results = []
        real_withdrawal_amounts = []  # New: track real withdrawal amounts
        
        for sim in range(n_simulations):
            # Update progress
            if progress_bar and sim % 100 == 0:
                progress_bar.progress((sim + 1) / n_simulations)
                if status_text:
                    status_text.text(get_text('simulation_step', lang).format(sim + 1, n_simulations))
            
            # Run single simulation with simplified tax calculation
            result = self._run_single_simulation_with_simple_tax(
                acc_mean_returns, acc_volatilities, acc_allocations, acc_min_returns, acc_max_returns, acc_ters,
                ret_mean_returns, ret_volatilities, ret_allocations, ret_min_returns, ret_max_returns, ret_ters,
                initial_amount, years_to_retirement, years_retired,
                annual_contribution, adjust_contribution_inflation, inflation, withdrawal, 
                capital_gains_tax_rate
            )
            
            accumulation_balances.append(result['accumulation_real'])
            accumulation_balances_nominal.append(result['accumulation_nominal'])
            final_results.append(result['final'])
            real_withdrawal_amounts.append(result['real_withdrawal'])
        
        # Update final progress
        if progress_bar:
            progress_bar.progress(1.0)
            if status_text:
                status_text.text(get_text('simulation_completed', lang))
        
        self.results = {
            'accumulation': accumulation_balances,
            'accumulation_nominal': accumulation_balances_nominal,
            'final': final_results,
            'real_withdrawal': real_withdrawal_amounts
        }
        
        return self.results
    
    def _run_single_simulation_with_simple_tax(self, acc_mean_returns, acc_volatilities, acc_allocations, 
                                              acc_min_returns, acc_max_returns, acc_ters,
                                              ret_mean_returns, ret_volatilities, ret_allocations,
                                              ret_min_returns, ret_max_returns, ret_ters,
                                              initial_amount, years_to_retirement, years_retired, 
                                              annual_contribution, adjust_contribution_inflation, 
                                              inflation, withdrawal, capital_gains_tax_rate):
        """Run a single simulation with simplified capital gains tax calculation"""
        
        balance_nominal = initial_amount
        total_deposited = initial_amount  # Track total contributions
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
        # Formula: Prelievo * (1 - (tassazione% * Capital Gain%))
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
            balance -= real_withdrawal  # Use the tax-adjusted withdrawal
            
            if balance < 0:
                balance = 0
                break
        
        return {
            'accumulation_nominal': accumulation_nominal,
            'accumulation_real': accumulation_real,
            'final': balance,
            'real_withdrawal': real_withdrawal  # Return the calculated real withdrawal
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
