"""
Feature 12: Capital Velocity Optimization
Source: numpy, pandas, scipy
"""
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Dict, List
import asyncio

class CapitalVelocityOptimizer:
    def __init__(self):
        self.capital_history = []
        self.velocity_target = 5.0  # Target: 5x capital turnover per day
        
    async def optimize_capital_allocation(self, strategies: List[Dict], available_capital: float) -> Dict:
        """Optimize capital allocation across strategies for maximum velocity"""
        # Create strategy DataFrame
        strategy_df = pd.DataFrame(strategies)
        
        if strategy_df.empty:
            return {'allocations': {}, 'expected_velocity': 0.0}
        
        # Calculate expected returns and velocities
        strategy_df['expected_hourly_return'] = strategy_df['expected_profit'] / strategy_df['duration_hours']
        strategy_df['capital_velocity'] = strategy_df['expected_hourly_return'] / strategy_df['capital_required']
        strategy_df['risk_adjusted_velocity'] = strategy_df['capital_velocity'] * (1 - strategy_df['risk_score'])
        
        # Use scipy optimization for capital allocation
        initial_guess = np.ones(len(strategy_df)) * (available_capital / len(strategy_df))
        bounds = [(0, min(available_capital, strat['capital_required'])) for strat in strategies]
        
        constraints = {
            'type': 'eq',
            'fun': lambda x: np.sum(x) - available_capital
        }
        
        def objective_function(allocations):
            # Maximize risk-adjusted velocity
            velocities = strategy_df['risk_adjusted_velocity'].values
            return -np.sum(allocations * velocities)
        
        result = minimize(
            objective_function,
            initial_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        # Prepare allocation results
        allocations = {}
        for i, strategy in enumerate(strategies):
            if result.success and result.x[i] > 0:
                allocations[strategy['id']] = {
                    'allocated_capital': result.x[i],
                    'expected_velocity': strategy_df.iloc[i]['capital_velocity'],
                    'expected_profit': strategy_df.iloc[i]['expected_hourly_return'] * result.x[i]
                }
        
        total_expected_velocity = sum(
            alloc['expected_velocity'] * alloc['allocated_capital'] 
            for alloc in allocations.values()
        ) / available_capital
        
        return {
            'allocations': allocations,
            'total_allocated': available_capital,
            'expected_velocity': total_expected_velocity,
            'optimization_success': result.success,
            'available_strategies': len(strategies)
        }
    
    def calculate_portfolio_velocity(self, portfolio: Dict) -> float:
        """Calculate current portfolio velocity"""
        if not portfolio.get('positions'):
            return 0.0
        
        total_capital = portfolio.get('total_capital', 1)
        daily_turnover = sum(
            position.get('turnover_rate', 0) * position.get('size', 0)
            for position in portfolio['positions']
        )
        
        return daily_turnover / total_capital
    
    async def rebalance_for_velocity(self, current_velocity: float, target_velocity: float) -> Dict:
        """Generate rebalancing recommendations to achieve target velocity"""
        velocity_gap = target_velocity - current_velocity
        
        if velocity_gap > 0:
            action = 'increase_allocation'
            recommendation = f"Increase capital allocation to high-velocity strategies by {velocity_gap * 100:.1f}%"
        else:
            action = 'decrease_allocation' 
            recommendation = f"Reduce exposure to low-velocity strategies by {abs(velocity_gap) * 100:.1f}%"
        
        return {
            'current_velocity': current_velocity,
            'target_velocity': target_velocity,
            'velocity_gap': velocity_gap,
            'action_required': action,
            'recommendation': recommendation,
            'rebalance_urgency': 'high' if abs(velocity_gap) > 1.0 else 'medium'
        }
