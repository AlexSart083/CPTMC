"""
Monte Carlo simulation engine for investment portfolio analysis
"""

import numpy as np
from translations import get_text


class MonteCarloSimulator:
    """Monte Carlo simulation engine for investment portfolios"""
    
    def __init__(self):
        self.results = None
    
    def run_simulation(self, assets_data, initial_amount, years_to_retirement, 
                      years_retired, annual_contribution, adjust_contribution_inflation,
                      inflation, withdrawal, n_simulations, progress_bar=None, 
                      status_text=None, lang='en'):
        """
        Run Monte Carlo simulation for investment portfolio
        
        Args:
            assets_data: List of asset dictionaries with allocation, return, volatility, etc.
            initial_amount: Initial investment amount
            years_to_retirement: Years in accumulation phase
            years_retired: Years in retirement phase
            annual_contribution: Annual contribution amount
            adjust_contribution_inflation: Whether to adjust contributions for inflation
            inflation: Annual inflation rate (as decimal)
            withdrawal: Annual withdrawal in retirement
            n_simulations: Number of simulations to run
            progress_bar: Streamlit progress bar (optional)
            status_text: Streamlit status text (optional)
            lang: Language for status messages
        
        Returns:
            Dictionary with simulation results
        """
        
        mean_returns = [asset['return'] / 100 for asset in assets_data]
        volatilities = [asset['volatility'] / 100 for asset in assets_data]
        allocations = [asset['allocation'] / 100 for asset in assets_data]
        min_returns = [asset['min_return'] / 100 for asset in assets_data]
        max_returns = [asset['max_return'] / 100 for asset in assets_data]
        ters = [asset['ter'] / 100 for asset in assets_data]
        
        accumulation_balances = []
        accumulation_balances_nominal = []
        final_results = []
        
        for sim in range(n_simulations):
            # Update progress
            if progress_bar and sim % 100 == 0:
                progress_bar.progress((sim + 1) / n_simulations)
                if status_text:
                    status_text.text(get_text('simulation_step', lang).format(sim + 1, n_simulations))
            
            # Run single simulation
            result = self._run_single_simulation(
                mean_returns, volatilities, allocations, min_returns, max_returns, ters,
                initial_amount, years_to_retirement, years_retired,
                annual_contribution, adjust_contribution_inflation, inflation, withdrawal
            )
            
            accumulation_balances.append(result['accumulation_real'])
            accumulation_balances_nominal.append(result['accumulation_nominal'])
            final_results.append(result['final'])
        
        # Update final progress
        if progress_bar:
            progress_bar.progress(1.0)
            if status_text:
                status_text.text(get_text('simulation_completed', lang))
        
        self.results = {
            'accumulation': accumulation_balances,
            'accumulation_nominal': accumulation_balances_nominal,
            'final': final_results
        }
        
        return self.results
    
    def _run_single_simulation(self, mean_returns, volatilities, allocations, 
                              min_returns, max_returns, ters, initial_amount,
                              years_to_retirement, years_retired, annual_contribution,
                              adjust_contribution_inflation, inflation, withdrawal):
        """Run a single Monte Carlo simulation"""
        
        balance_nominal = initial_amount
        current_contribution = annual_contribution
        
        # Accumulation phase - calculate everything in NOMINAL terms
        for year in range(int(years_to_retirement)):
            annual_returns = [np.random.normal(mean_returns[i], volatilities[i]) 
                            for i in range(len(mean_returns))]
            capped_returns = [max(min(annual_returns[i], max_returns[i]), min_returns[i]) 
                            for i in range(len(mean_returns))]
            # Apply TER (subtract fees from returns)
            net_returns = [capped_returns[i] - ters[i] for i in range(len(capped_returns))]
            annual_return_nominal = sum(net_returns[i] * allocations[i] 
                                      for i in range(len(net_returns)))
            
            # Calculate nominal balance
            balance_nominal *= (1 + annual_return_nominal)
            balance_nominal += current_contribution
            
            # Update contribution for next year if inflation adjustment is enabled
            if adjust_contribution_inflation:
                current_contribution *= (1 + inflation)
        
        # Store nominal accumulation value
        accumulation_nominal = balance_nominal
        
        # Convert to real value by deflating for all years of inflation
        balance_real = balance_nominal / ((1 + inflation) ** years_to_retirement)
        accumulation_real = balance_real
        
        # Retirement phase - use REAL balance and REAL returns
        balance = balance_real  # Start retirement with real balance
        for year in range(int(years_retired)):
            annual_returns = [np.random.normal(mean_returns[i], volatilities[i]) 
                            for i in range(len(mean_returns))]
            capped_returns = [max(min(annual_returns[i], max_returns[i]), min_returns[i]) 
                            for i in range(len(mean_returns))]
            # Apply TER (subtract fees from returns)
            net_returns = [capped_returns[i] - ters[i] for i in range(len(capped_returns))]
            annual_return_nominal = sum(net_returns[i] * allocations[i] 
                                      for i in range(len(net_returns)))
            
            # Calculate real return for retirement phase
            annual_return_real = annual_return_nominal - inflation
            
            # Apply real return and subtract withdrawal (in real terms)
            balance *= (1 + annual_return_real)
            balance -= withdrawal
            if balance < 0:
                balance = 0
                break
        
        return {
            'accumulation_nominal': accumulation_nominal,
            'accumulation_real': accumulation_real,
            'final': balance
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
        
        for phase in ['accumulation', 'accumulation_nominal', 'final']:
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
