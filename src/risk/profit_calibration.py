"""
Feature 13: Advanced Risk-Profit Calibration
Source: pypfopt, scipy, numpy
"""
from pypfopt import EfficientFrontier, risk_models
from scipy.optimize import minimize_scalar
from scipy import stats
import numpy as np
from typing import Dict, List, Tuple

class ProfitCalibration:
    def __init__(self):
        self.historical_returns = []
        self.risk_free_rate = 0.02  # 2% annual risk-free rate
        
    def calibrate_risk_profit_profile(self, strategies: List[Dict]) -> Dict:
        """Calibrate optimal risk-profit balance using Modern Portfolio Theory"""
        if not strategies:
            return {'error': 'No strategies provided'}
        
        # Prepare expected returns and covariance matrix
        expected_returns = np.array([s['expected_annual_return'] for s in strategies])
        covariance_matrix = self._build_covariance_matrix(strategies)
        
        # Use PyPortfolioOpt for efficient frontier
        ef = EfficientFrontier(expected_returns, covariance_matrix)
        ef.max_sharpe(risk_free_rate=self.risk_free_rate)
        weights = ef.clean_weights()
        
        # Calculate portfolio metrics
        expected_return, volatility, sharpe_ratio = ef.portfolio_performance()
        
        # Optimize position sizing using Kelly Criterion
        kelly_weights = self._calculate_kelly_weights(strategies)
        
        return {
            'optimal_weights': weights,
            'kelly_weights': kelly_weights,
            'expected_annual_return': expected_return,
            'expected_volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown_estimate': self._estimate_max_drawdown(volatility, expected_return),
            'var_95': self._calculate_var(volatility, expected_return),
            'calibration_timestamp': self._get_timestamp()
        }
    
    def _build_covariance_matrix(self, strategies: List[Dict]) -> np.ndarray:
        """Build covariance matrix from strategy correlations"""
        n = len(strategies)
        cov_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    cov_matrix[i][j] = strategies[i]['volatility'] ** 2
                else:
                    # Use strategy correlations if available, else assume low correlation
                    correlation = strategies[i].get('correlation_with_' + strategies[j]['id'], 0.2)
                    cov_matrix[i][j] = (strategies[i]['volatility'] * 
                                      strategies[j]['volatility'] * 
                                      correlation)
        return cov_matrix
    
    def _calculate_kelly_weights(self, strategies: List[Dict]) -> Dict:
        """Calculate position sizes using Kelly Criterion"""
        kelly_weights = {}
        total_capital = sum(s['allocated_capital'] for s in strategies)
        
        for strategy in strategies:
            win_rate = strategy.get('win_rate', 0.55)
            avg_win = strategy.get('avg_win_percent', 0.15)
            avg_loss = strategy.get('avg_loss_percent', 0.05)
            
            # Kelly formula: f = (bp - q) / b
            b = avg_win / avg_loss  # win/loss ratio
            p = win_rate  # win probability
            q = 1 - p     # loss probability
            
            kelly_fraction = (b * p - q) / b if b > 0 else 0
            # Use half-kelly for conservative approach
            conservative_fraction = kelly_fraction * 0.5
            
            kelly_weights[strategy['id']] = {
                'kelly_fraction': max(0, kelly_fraction),
                'conservative_fraction': max(0, conservative_fraction),
                'suggested_allocation': conservative_fraction * total_capital
            }
        
        return kelly_weights
    
    def _estimate_max_drawdown(self, volatility: float, expected_return: float) -> float:
        """Estimate maximum drawdown using volatility and returns"""
        # Simplified formula: MDD ≈ (volatility^2) / (4 * return)
        if expected_return > 0:
            return (volatility ** 2) / (4 * expected_return)
        return volatility * 2  # Conservative estimate for negative returns
    
    def _calculate_var(self, volatility: float, expected_return: float, confidence: float = 0.95) -> float:
        """Calculate Value at Risk"""
        z_score = stats.norm.ppf(1 - confidence)
        return expected_return + z_score * volatility
    
    def _get_timestamp(self) -> int:
        import time
        return int(time.time())
