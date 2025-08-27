"""
Risk Metrics Calculator - VaR and CVaR calculations for Monte Carlo simulations
Calcolatore di metriche di rischio - Calcoli VaR e CVaR per simulazioni Monte Carlo
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional


class RiskMetricsCalculator:
    """Calculator for VaR and CVaR risk metrics"""
    
    @staticmethod
    def calculate_var(values: List[float], confidence_level: float = 0.95) -> float:
        """
        Calculate Value at Risk (VaR) at specified confidence level
        
        Args:
            values: List of portfolio values from simulation
            confidence_level: Confidence level (default 0.95 for 5% VaR)
            
        Returns:
            VaR value (the threshold below which losses occur with (1-confidence_level) probability)
        """
        if not values or len(values) == 0:
            return 0.0
        
        # Convert to numpy array for easier calculation
        values_array = np.array(values)
        
        # Calculate percentile (for 95% confidence, we want 5th percentile)
        percentile = (1 - confidence_level) * 100
        var_value = np.percentile(values_array, percentile)
        
        return var_value
    
    @staticmethod
    def calculate_cvar(values: List[float], confidence_level: float = 0.95) -> float:
        """
        Calculate Conditional Value at Risk (CVaR) at specified confidence level
        Also known as Expected Shortfall (ES)
        
        Args:
            values: List of portfolio values from simulation
            confidence_level: Confidence level (default 0.95 for 5% CVaR)
            
        Returns:
            CVaR value (expected value of losses beyond the VaR threshold)
        """
        if not values or len(values) == 0:
            return 0.0
        
        # First calculate VaR
        var_value = RiskMetricsCalculator.calculate_var(values, confidence_level)
        
        # Convert to numpy array
        values_array = np.array(values)
        
        # Find all values at or below the VaR threshold
        tail_values = values_array[values_array <= var_value]
        
        # CVaR is the mean of these tail values
        if len(tail_values) > 0:
            cvar_value = np.mean(tail_values)
        else:
            # If no values below VaR (rare case), use VaR itself
            cvar_value = var_value
        
        return cvar_value
    
    @staticmethod
    def calculate_risk_metrics_comprehensive(simulation_results: Dict, 
                                           confidence_levels: List[float] = [0.90, 0.95, 0.99]) -> Dict:
        """
        Calculate comprehensive risk metrics for all phases of simulation
        
        Args:
            simulation_results: Results dictionary from Monte Carlo simulation
            confidence_levels: List of confidence levels to calculate (default: 90%, 95%, 99%)
            
        Returns:
            Dictionary containing VaR and CVaR for all phases and confidence levels
        """
        risk_metrics = {}
        
        # Define phases to analyze
        phases = {
            'accumulation_nominal': 'Accumulation (Nominal)',
            'accumulation': 'Accumulation (Real)', 
            'final': 'Final Portfolio Value'
        }
        
        for phase_key, phase_name in phases.items():
            if phase_key in simulation_results:
                values = simulation_results[phase_key]
                
                risk_metrics[phase_key] = {
                    'phase_name': phase_name,
                    'var': {},
                    'cvar': {},
                    'statistics': {
                        'mean': np.mean(values),
                        'median': np.median(values),
                        'std': np.std(values),
                        'min': np.min(values),
                        'max': np.max(values),
                        'count': len(values)
                    }
                }
                
                # Calculate VaR and CVaR for each confidence level
                for conf_level in confidence_levels:
                    percentile_label = f"{(1-conf_level)*100:.0f}%"
                    
                    var_value = RiskMetricsCalculator.calculate_var(values, conf_level)
                    cvar_value = RiskMetricsCalculator.calculate_cvar(values, conf_level)
                    
                    risk_metrics[phase_key]['var'][percentile_label] = var_value
                    risk_metrics[phase_key]['cvar'][percentile_label] = cvar_value
        
        return risk_metrics
    
    @staticmethod
    def calculate_loss_probabilities(values: List[float], reference_value: float) -> Dict:
        """
        Calculate probability of losses relative to a reference value
        
        Args:
            values: Portfolio values from simulation
            reference_value: Reference value (e.g., total deposited amount)
            
        Returns:
            Dictionary with loss probability statistics
        """
        if not values or len(values) == 0:
            return {}
        
        values_array = np.array(values)
        
        # Calculate different loss thresholds
        loss_thresholds = [0.0, 0.1, 0.2, 0.3, 0.5]  # 0%, 10%, 20%, 30%, 50% loss
        loss_probabilities = {}
        
        for threshold in loss_thresholds:
            threshold_value = reference_value * (1 - threshold)
            prob = np.sum(values_array < threshold_value) / len(values_array) * 100
            loss_probabilities[f"loss_{threshold*100:.0f}%"] = {
                'threshold_value': threshold_value,
                'probability': prob,
                'count': int(np.sum(values_array < threshold_value))
            }
        
        # Calculate probability of any loss (value < reference)
        total_loss_prob = np.sum(values_array < reference_value) / len(values_array) * 100
        
        return {
            'reference_value': reference_value,
            'total_loss_probability': total_loss_prob,
            'loss_thresholds': loss_probabilities,
            'average_loss_when_loss_occurs': np.mean(values_array[values_array < reference_value]) if np.any(values_array < reference_value) else reference_value
        }
    
    @staticmethod
    def calculate_real_vs_nominal_risk_comparison(real_values: List[float], 
                                                nominal_values: List[float],
                                                confidence_level: float = 0.95) -> Dict:
        """
        Compare risk metrics between real and nominal values
        
        Args:
            real_values: Real (inflation-adjusted) portfolio values
            nominal_values: Nominal portfolio values
            confidence_level: Confidence level for VaR/CVaR calculation
            
        Returns:
            Dictionary comparing risk metrics
        """
        if not real_values or not nominal_values:
            return {}
        
        percentile_label = f"{(1-confidence_level)*100:.0f}%"
        
        # Calculate risk metrics for both
        real_var = RiskMetricsCalculator.calculate_var(real_values, confidence_level)
        real_cvar = RiskMetricsCalculator.calculate_cvar(real_values, confidence_level)
        
        nominal_var = RiskMetricsCalculator.calculate_var(nominal_values, confidence_level)
        nominal_cvar = RiskMetricsCalculator.calculate_cvar(nominal_values, confidence_level)
        
        # Calculate inflation impact on risk
        var_inflation_impact = (nominal_var - real_var) / nominal_var * 100 if nominal_var != 0 else 0
        cvar_inflation_impact = (nominal_cvar - real_cvar) / nominal_cvar * 100 if nominal_cvar != 0 else 0
        
        return {
            'confidence_level': confidence_level,
            'percentile_label': percentile_label,
            'real': {
                'var': real_var,
                'cvar': real_cvar,
                'mean': np.mean(real_values),
                'std': np.std(real_values)
            },
            'nominal': {
                'var': nominal_var,
                'cvar': nominal_cvar,
                'mean': np.mean(nominal_values),
                'std': np.std(nominal_values)
            },
            'inflation_impact': {
                'var_reduction_percent': var_inflation_impact,
                'cvar_reduction_percent': cvar_inflation_impact,
                'average_reduction_percent': (var_inflation_impact + cvar_inflation_impact) / 2
            }
        }
    
    @staticmethod
    def calculate_portfolio_risk_attribution(simulation_results: Dict, 
                                           asset_allocations: Dict,
                                           confidence_level: float = 0.95) -> Dict:
        """
        Calculate risk attribution by asset class (simplified approximation)
        
        Args:
            simulation_results: Monte Carlo simulation results
            asset_allocations: Dictionary of asset names and their allocations
            confidence_level: Confidence level for calculations
            
        Returns:
            Dictionary with risk attribution estimates
        """
        if 'final' not in simulation_results:
            return {}
        
        final_values = simulation_results['final']
        var_value = RiskMetricsCalculator.calculate_var(final_values, confidence_level)
        cvar_value = RiskMetricsCalculator.calculate_cvar(final_values, confidence_level)
        
        # Simplified risk attribution based on allocations
        # In reality, this would require tracking individual asset contributions
        total_allocation = sum(asset_allocations.values())
        
        risk_attribution = {}
        for asset_name, allocation in asset_allocations.items():
            if total_allocation > 0:
                weight = allocation / total_allocation
                
                risk_attribution[asset_name] = {
                    'allocation_weight': weight,
                    'estimated_var_contribution': var_value * weight,
                    'estimated_cvar_contribution': cvar_value * weight,
                    'allocation_percent': allocation
                }
        
        return {
            'total_var': var_value,
            'total_cvar': cvar_value,
            'attribution': risk_attribution,
            'note': 'Risk attribution is simplified approximation based on allocations'
        }
    
    @staticmethod
    def generate_risk_summary(risk_metrics: Dict, lang: str = 'en') -> Dict:
        """
        Generate a summary of key risk insights
        
        Args:
            risk_metrics: Comprehensive risk metrics from calculate_risk_metrics_comprehensive
            lang: Language for text ('en' or 'it')
            
        Returns:
            Dictionary with risk summary and insights
        """
        if not risk_metrics:
            return {}
        
        summary = {
            'key_insights': [],
            'risk_levels': {},
            'recommendations': []
        }
        
        # Analyze 5% VaR and CVaR for final values
        if 'final' in risk_metrics:
            final_metrics = risk_metrics['final']
            var_5 = final_metrics['var'].get('5%', 0)
            cvar_5 = final_metrics['cvar'].get('5%', 0)
            mean_value = final_metrics['statistics']['mean']
            
            # Risk level assessment
            if var_5 <= 0:
                risk_level = 'High' if lang == 'en' else 'Alto'
                risk_color = 'red'
            elif var_5 < mean_value * 0.5:
                risk_level = 'Moderate' if lang == 'en' else 'Moderato'
                risk_color = 'orange'
            else:
                risk_level = 'Low' if lang == 'en' else 'Basso'
                risk_color = 'green'
            
            summary['risk_levels']['overall'] = {
                'level': risk_level,
                'color': risk_color,
                'var_5_percent': var_5,
                'cvar_5_percent': cvar_5
            }
            
            # Generate insights based on values
            if lang == 'it':
                if var_5 <= 0:
                    summary['key_insights'].append(
                        f"⚠️ Alto rischio: VaR 5% = €{var_5:,.0f} indica possibilità significativa di perdite totali"
                    )
                else:
                    summary['key_insights'].append(
                        f"📊 VaR 5% = €{var_5:,.0f}: nel peggiore 5% dei casi, il portafoglio vale almeno questo importo"
                    )
                
                summary['key_insights'].append(
                    f"📉 CVaR 5% = €{cvar_5:,.0f}: valore medio nei peggiori 5% degli scenari"
                )
                
                if cvar_5 < var_5 * 0.8:
                    summary['key_insights'].append(
                        "⚡ Significativa concentrazione del rischio nella coda estrema della distribuzione"
                    )
            else:
                if var_5 <= 0:
                    summary['key_insights'].append(
                        f"⚠️ High risk: VaR 5% = €{var_5:,.0f} indicates significant possibility of total losses"
                    )
                else:
                    summary['key_insights'].append(
                        f"📊 VaR 5% = €{var_5:,.0f}: in the worst 5% of cases, portfolio is worth at least this amount"
                    )
                
                summary['key_insights'].append(
                    f"📉 CVaR 5% = €{cvar_5:,.0f}: average value in the worst 5% of scenarios"
                )
                
                if cvar_5 < var_5 * 0.8:
                    summary['key_insights'].append(
                        "⚡ Significant risk concentration in the extreme tail of the distribution"
                    )
        
        return summary
