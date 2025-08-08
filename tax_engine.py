"""
Enhanced Tax Engine for Monte Carlo Investment Simulator
Implements detailed capital gains taxation tracking - FIXED VERSION
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
        capital_gain = max(0, actual_withdrawal - cost_basis_sold)  # Only positive gains
        
        # Update remaining amounts
        self.remaining_amount -= actual_withdrawal
        self.remaining_basis -= cost_basis_sold
        
        return actual_withdrawal, cost_basis_sold, capital_gain


class EnhancedTaxEngine:
    """Enhanced tax engine with detailed capital gains tracking - CORRECTED"""
    
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
        self.total_capital_gains_realized = 0.0  # Track total gains realized
    
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
                # Cost basis remains unchanged - this is key!
    
    def calculate_withdrawal_tax(self, withdrawal_amount: float) -> Dict[str, float]:
        """
        Calculate tax on withdrawal using proportional method
        CORRECTED: Only taxes capital gains, not total withdrawal
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
        
        # Limit withdrawal to available portfolio value
        actual_withdrawal_amount = min(withdrawal_amount, total_portfolio_value)
        
        # Calculate proportional withdrawal from each lot
        total_capital_gains = 0.0
        total_cost_basis_sold = 0.0
        total_actually_withdrawn = 0.0
        
        # Get active lots
        active_lots = [lot for lot in self.tax_lots if lot.remaining_amount > 0]
        
        # Calculate proportional withdrawal from each lot
        for lot in active_lots:
            if total_actually_withdrawn >= actual_withdrawal_amount:
                break
                
            # Calculate this lot's proportion of total portfolio
            lot_proportion = lot.remaining_amount / total_portfolio_value
            
            # Calculate withdrawal from this lot
            lot_withdrawal = min(
                actual_withdrawal_amount * lot_proportion,
                lot.remaining_amount,
                actual_withdrawal_amount - total_actually_withdrawn
            )
            
            if lot_withdrawal > 0:
                actual_withdrawal, cost_basis_sold, capital_gain = lot.withdraw(lot_withdrawal)
                
                total_actually_withdrawn += actual_withdrawal
                total_cost_basis_sold += cost_basis_sold
                total_capital_gains += capital_gain
        
        # CORRECTED: Tax only the capital gains portion
        taxes_owed = total_capital_gains * self.capital_gains_tax_rate
        
        # Net withdrawal = gross withdrawal - taxes on gains
        net_withdrawal = total_actually_withdrawn - taxes_owed
        
        # Update tracking
        self.total_withdrawals += total_actually_withdrawn
        self.total_taxes_paid += taxes_owed
        self.total_capital_gains_realized += total_capital_gains
        
        # Sanity check: taxes should never exceed withdrawal
        if taxes_owed > total_actually_withdrawn:
            print(f"WARNING: Taxes ({taxes_owed:.2f}) exceed withdrawal ({total_actually_withdrawn:.2f})")
            taxes_owed = total_capital_gains * self.capital_gains_tax_rate  # Should be correct
            net_withdrawal = total_actually_withdrawn - taxes_owed
        
        return {
            'gross_withdrawal': total_actually_withdrawn,
            'net_withdrawal': max(0, net_withdrawal),  # Ensure non-negative
            'capital_gains': total_capital_gains,
            'taxes_owed': taxes_owed,
            'cost_basis_sold': total_cost_basis_sold
        }
    
    def get_portfolio_status(self) -> Dict[str, float]:
        """Get current portfolio status"""
        total_value = sum(lot.remaining_amount for lot in self.tax_lots)
        total_basis = sum(lot.remaining_basis for lot in self.tax_lots)
        unrealized_gains = max(0, total_value - total_basis)  # Only positive gains
        
        return {
            'total_portfolio_value': total_value,
            'total_cost_basis': total_basis,
            'unrealized_capital_gains': unrealized_gains,
            'unrealized_gain_percentage': unrealized_gains / total_value if total_value > 0 else 0,
            'total_contributions': self.total_contributions,
            'total_withdrawals': self.total_withdrawals,
            'total_taxes_paid': self.total_taxes_paid,
            'total_capital_gains_realized': self.total_capital_gains_realized
        }
    
    def calculate_required_gross_withdrawal(self, desired_net_amount: float, 
                                          max_iterations: int = 10) -> float:
        """
        Calculate how much needs to be withdrawn gross to get desired net amount
        CORRECTED: More conservative estimate
        """
        if desired_net_amount <= 0:
            return 0.0
        
        # Get current portfolio composition to estimate tax impact
        total_value = sum(lot.remaining_amount for lot in self.tax_lots)
        total_basis = sum(lot.remaining_basis for lot in self.tax_lots)
        
        if total_value <= 0:
            return 0.0
        
        # Estimate average gain percentage
        avg_gain_percentage = max(0, (total_value - total_basis) / total_value)
        
        # Estimate tax on this withdrawal
        estimated_tax_rate = avg_gain_percentage * self.capital_gains_tax_rate
        
        # Simple estimate: desired_net / (1 - tax_rate)
        estimated_gross = desired_net_amount / (1 - estimated_tax_rate) if estimated_tax_rate < 1 else desired_net_amount * 1.1
        
        # Limit to available portfolio value
        estimated_gross = min(estimated_gross, total_value)
        
        # For simplicity, use this estimate without iteration to avoid complexity
        return estimated_gross
