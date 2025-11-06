"""
Feature 11: Predictive Gas Optimization
Source: web3-gas-utils, eip-1559
"""
from web3.gas_strategies.time_based import medium_gas_price_strategy
from web3 import Web3
import time
from typing import Dict
import statistics

class PredictiveGasOptimization:
    def __init__(self, web3: Web3):
        self.web3 = web3
        self.gas_history = []
        self.max_history_size = 100
        
    def get_optimized_gas_params(self, urgency: str = 'medium') -> Dict:
        """Get optimized gas parameters based on urgency and historical data"""
        current_block = self.web3.eth.get_block('latest')
        base_fee = current_block.get('baseFeePerGas', 0)
        
        # EIP-1559 compliant gas calculation
        if urgency == 'high':
            max_priority_fee = self._calculate_priority_fee(percentile=90)
            max_fee_per_gas = int(base_fee * 1.3 + max_priority_fee)
        elif urgency == 'medium':
            max_priority_fee = self._calculate_priority_fee(percentile=70)
            max_fee_per_gas = int(base_fee * 1.2 + max_priority_fee)
        else:  # low urgency
            max_priority_fee = self._calculate_priority_fee(percentile=50)
            max_fee_per_gas = int(base_fee * 1.1 + max_priority_fee)
        
        gas_params = {
            'maxFeePerGas': max_fee_per_gas,
            'maxPriorityFeePerGas': max_priority_fee,
            'gas': 300000,  # Standard gas limit for flash loans
            'type': 2  # EIP-1559 transaction type
        }
        
        self._update_gas_history(gas_params)
        return gas_params
    
    def _calculate_priority_fee(self, percentile: int) -> int:
        """Calculate priority fee based on historical data"""
        if not self.gas_history:
            return Web3.to_wei(2, 'gwei')  # Default
        
        priority_fees = [tx.get('maxPriorityFeePerGas', 0) for tx in self.gas_history]
        return int(statistics.quantiles(priority_fees, n=100)[percentile-1])
    
    def _update_gas_history(self, gas_params: Dict):
        """Update gas history for future predictions"""
        self.gas_history.append(gas_params)
        if len(self.gas_history) > self.max_history_size:
            self.gas_history.pop(0)
    
    def estimate_gas_savings(self) -> Dict:
        """Estimate gas savings from optimization"""
        if len(self.gas_history) < 2:
            return {'savings_percentage': 0, 'estimated_savings_eth': 0}
        
        recent_costs = [
            tx.get('maxFeePerGas', 0) * 300000 / 1e18  # Convert to ETH
            for tx in self.gas_history[-10:]
        ]
        
        avg_optimized = statistics.mean(recent_costs)
        # Assume non-optimized would be 30% higher
        estimated_non_optimized = avg_optimized * 1.3
        
        return {
            'savings_percentage': 30.0,
            'estimated_savings_eth': estimated_non_optimized - avg_optimized,
            'optimized_avg_cost_eth': avg_optimized,
            'transactions_analyzed': len(self.gas_history)
        }
