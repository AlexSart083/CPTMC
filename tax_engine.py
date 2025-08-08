"""
Enhanced Tax Engine for Monte Carlo Investment Simulator
Implements detailed capital gains taxation tracking
"""

import numpy as np
from typing import List, Dict, Tuple, Optional


class TaxLot:
    """Represents a tax lot for capital gains tracking"""
    
    def __init__(self, amount: float, cost_basis: float, purchase_year: int):
        self.amount = amount  # Current value
        self.cost_basis = cost_basis  # Original investment
        self.purchase_year = purchase_year
        self.remaining_amount = amount
        self.remaining_basis = cost_basis
    
    def calculate_gain(self) -> float:
        """Calculate total capital gain for this lot"""
        if self.remaining_amount <= 0:
            return 0.0
        return max(0, self.remaining_amount - self.remaining_basis)
    
    def calculate_gain_percentage(self) -> float:
        """Calculate gain as percentage of current value"""
        if self.remaining_amount <= 0:
            return 0.0
        return max(0, (self.remaining_amount - self.remaining_basis) / self.remaining_amount)
    
    def withdraw(self, withdrawal_amount: float) -> Tuple[float, float, float]:
        """
        Withdraw amount using proportional method
        Returns: (actual_withdrawal, cost_basis_sold, capital_gain)
        """
        if self.remaining_amount <= 0 or withdrawal_amount <= 0:
            return 0.0, 0.0, 0.0
        
        # Calculate withdrawal ratio
        withdrawal_ratio = min(1.0, withdrawal_amount / self.remaining_amount)
        
        # Calculate proportional amounts
        actual_withdrawal = self.remaining_amount * withdrawal_ratio
        cost_basis_sold = self.remaining_basis * withdrawal_ratio
        capital_gain = actual_withdrawal - cost_basis_sold
        
        # Update remaining amounts
        self.remaining_amount -= actual_withdrawal
        self.remaining_basis -= cost_basis_sold
        
        return actual_withdrawal, cost_basis_sold, max(0, capital_gain)


class EnhancedTaxEngine:
    """Enhanced tax engine with detailed capital gains tracking"""
    
    def __init__(self, capital_gains_tax_rate: float = 26.0):
        """
        Initialize tax engine
        
        Args:
            capital_gains_tax_rate: Tax rate as percentage (e.g., 26.0 for 26%)
        """
        self.capital_gains_tax_rate = capital_gains_tax_rate / 100.0  # Convert to decimal
        self.tax_lots: List[TaxLot] = []
        self.current_year = 0
        self.total_contributions = 0.0
        self.total_withdrawals = 0.0
        self.total_taxes_paid = 0.0
    
    def add_contribution(self, amount: float, year: int):
        """Add a contribution (creates a new tax lot with zero gain)"""
        if amount > 0:
            self.tax_lots.append(TaxLot(amount, amount, year))
            self.total_contributions += amount
    
    def apply_returns(self, annual_return: float, year: int):
        """Apply returns to all tax lots"""
        self.current_year = year
        for lot in self.tax_lots:
            if lot.remaining_amount > 0:
                lot.remaining_amount *= (1 + annual_return)
                # Cost basis remains unchanged
    
    def calculate_withdrawal_tax(self, withdrawal_amount: float) -> Dict[str, float]:
        """
        Calculate tax on withdrawal using proportional method
        
        Returns dict with:
        - gross_withdrawal: Amount needed to be sold
        - net_withdrawal: Amount received after tax
        - capital_gains: Total capital gains realized
        - taxes_owed: Total tax owed
        - cost_basis_sold: Cost basis of sold investments
        """
        if withdrawal_amount <= 0:
            return {
                'gross_withdrawal': 0.0,
                'net_withdrawal': 0.0,
                'capital_gains': 0.0,
                'taxes_owed': 0.0,
                'cost_basis_sold': 0.0
            }
        
        # Calculate total portfolio value
        total_portfolio_value = sum(lot.remaining_amount for lot in self.tax_lots)
        
        if total_portfolio_value <= 0:
            return {
                'gross_withdrawal': 0.0,
                'net_withdrawal': 0.0,
                'capital_gains': 0.0,
                'taxes_owed': 0.0,
                'cost_basis_sold': 0.0
            }
        
        # Calculate proportional withdrawal from each lot
        total_capital_gains = 0.0
        total_cost_basis_sold = 0.0
        total_actually_withdrawn = 0.0
        
        # Sort lots by remaining amount (optional: could use FIFO, LIFO, or other methods)
        active_lots = [lot for lot in self.tax_lots if lot.remaining_amount > 0]
        
        remaining_to_withdraw = withdrawal_amount
        
        for lot in active_lots:
            if remaining_to_withdraw <= 0:
                break
            
            # Calculate proportional withdrawal from this lot
            lot_withdrawal = min(remaining_to_withdraw, lot.remaining_amount)
            
            actual_withdrawal, cost_basis_sold, capital_gain = lot.withdraw(lot_withdrawal)
            
            total_actually_withdrawn += actual_withdrawal
            total_cost_basis_sold += cost_basis_sold
            total_capital_gains += capital_gain
            
            remaining_to_withdraw -= actual_withdrawal
        
        # Calculate tax
        taxes_owed = total_capital_gains * self.capital_gains_tax_rate
        net_withdrawal = total_actually_withdrawn - taxes_owed
        
        # Update tracking
        self.total_withdrawals += total_actually_withdrawn
        self.total_taxes_paid += taxes_owed
        
        return {
            'gross_withdrawal': total_actually_withdrawn,
            'net_withdrawal': net_withdrawal,
            'capital_gains': total_capital_gains,
            'taxes_owed': taxes_owed,
            'cost_basis_sold': total_cost_basis_sold
        }
    
    def get_portfolio_status(self) -> Dict[str, float]:
        """Get current portfolio status"""
        total_value = sum(lot.remaining_amount for lot in self.tax_lots)
        total_basis = sum(lot.remaining_basis for lot in self.tax_lots)
        unrealized_gains = total_value - total_basis
        
        return {
            'total_portfolio_value': total_value,
            'total_cost_basis': total_basis,
            'unrealized_capital_gains': max(0, unrealized_gains),
            'unrealized_gain_percentage': unrealized_gains / total_value if total_value > 0 else 0,
            'total_contributions': self.total_contributions,
            'total_withdrawals': self.total_withdrawals,
            'total_taxes_paid': self.total_taxes_paid
        }
    
    def calculate_required_gross_withdrawal(self, desired_net_amount: float, 
                                          max_iterations: int = 10) -> float:
        """
        Calculate how much needs to be withdrawn gross to get desired net amount
        Uses iterative approach since tax depends on amount withdrawn
        """
        if desired_net_amount <= 0:
            return 0.0
        
        # Start with simple estimate
        estimated_gross = desired_net_amount * 1.2  # 20% buffer
        
        # Create a copy of tax lots for simulation
        original_lots = []
        for lot in self.tax_lots:
            original_lots.append({
                'remaining_amount': lot.remaining_amount,
                'remaining_basis': lot.remaining_basis
            })
        
        best_gross = estimated_gross
        best_net = 0.0
        
        for iteration in range(max_iterations):
            # Restore original state
            for i, lot in enumerate(self.tax_lots):
                lot.remaining_amount = original_lots[i]['remaining_amount']
                lot.remaining_basis = original_lots[i]['remaining_basis']
            
            # Test this gross amount
            result = self.calculate_withdrawal_tax(estimated_gross)
            net_amount = result['net_withdrawal']
            
            if abs(net_amount - desired_net_amount) < 1.0:  # Within €1
                best_gross = estimated_gross
                break
            
            # Adjust estimate
            if net_amount < desired_net_amount:
                # Need more gross
                estimated_gross *= (desired_net_amount / net_amount) * 1.01
            else:
                # Need less gross
                estimated_gross *= (desired_net_amount / net_amount) * 0.99
            
            if abs(net_amount - desired_net_amount) < abs(best_net - desired_net_amount):
                best_gross = estimated_gross
                best_net = net_amount
        
        # Restore original state
        for i, lot in enumerate(self.tax_lots):
            lot.remaining_amount = original_lots[i]['remaining_amount']
            lot.remaining_basis = original_lots[i]['remaining_basis']
        
        return best_gross
    
    def simulate_withdrawal_scenarios(self, withdrawal_amounts: List[float]) -> List[Dict]:
        """Simulate multiple withdrawal scenarios without affecting actual state"""
        results = []
        
        # Save original state
        original_lots = []
        for lot in self.tax_lots:
            original_lots.append({
                'remaining_amount': lot.remaining_amount,
                'remaining_basis': lot.remaining_basis
            })
        
        for amount in withdrawal_amounts:
            # Restore state
            for i, lot in enumerate(self.tax_lots):
                lot.remaining_amount = original_lots[i]['remaining_amount']
                lot.remaining_basis = original_lots[i]['remaining_basis']
            
            # Calculate withdrawal
            result = self.calculate_withdrawal_tax(amount)
            result['withdrawal_amount'] = amount
            results.append(result)
        
        # Restore final state
        for i, lot in enumerate(self.tax_lots):
            lot.remaining_amount = original_lots[i]['remaining_amount']
            lot.remaining_basis = original_lots[i]['remaining_basis']
        
        return results
