"""
Feature 20: Dynamic Fee Optimization
Source: web3-gas, eip-1559
"""
from web3 import Web3
import asyncio
import time
from typing import Dict, List
import statistics

class DynamicFeeOptimizer:
    def __init__(self, web3: Web3):
        self.web3 = web3
        self.fee_history = []
        self.network_conditions = {}
        self.max_history_size = 1000
        
    async def get_optimized_fee_parameters(self, transaction_type: str, urgency: str) -> Dict:
        """Get optimized fee parameters based on transaction type and urgency"""
        current_block = await self.web3.eth.get_block('latest')
        base_fee = current_block.get('baseFeePerGas', 0)
        
        # Get current network conditions
        network_conditions = await self._analyze_network_conditions()
        
        # Calculate optimal fees based on type and urgency
        if transaction_type == 'flash_loan_arbitrage':
            fees = self._calculate_arbitrage_fees(base_fee, urgency, network_conditions)
        elif transaction_type == 'liquidity_provision':
            fees = self._calculate_lp_fees(base_fee, urgency, network_conditions)
        elif transaction_type == 'governance':
            fees = self._calculate_governance_fees(base_fee, urgency, network_conditions)
        else:
            fees = self._calculate_general_fees(base_fee, urgency, network_conditions)
        
        # Update fee history
        self._update_fee_history(fees, transaction_type)
        
        return {
            'transaction_type': transaction_type,
            'urgency': urgency,
            'fee_parameters': fees,
            'network_conditions': network_conditions,
            'confidence_score': self._calculate_fee_confidence(),
            'timestamp': time.time()
        }
    
    async def _analyze_network_conditions(self) -> Dict:
        """Analyze current network conditions for fee optimization"""
        try:
            # Get recent blocks for analysis
            latest_block = await self.web3.eth.get_block('latest')
            block_number = latest_block.number
            
            # Analyze gas usage in recent blocks
            gas_usage_rates = []
            base_fee_trend = []
            
            for i in range(5):
                try:
                    block = await self.web3.eth.get_block(block_number - i)
                    gas_used = block.gasUsed
                    gas_limit = block.gasLimit
                    base_fee = block.get('baseFeePerGas', 0)
                    
                    gas_usage_rates.append(gas_used / gas_limit)
                    base_fee_trend.append(base_fee)
                except:
                    continue
            
            # Calculate network congestion
            avg_gas_usage = statistics.mean(gas_usage_rates) if gas_usage_rates else 0.5
            congestion_level = 'high' if avg_gas_usage > 0.8 else 'medium' if avg_gas_usage > 0.5 else 'low'
            
            # Analyze base fee trend
            if len(base_fee_trend) >= 2:
                fee_trend = 'increasing' if base_fee_trend[0] > base_fee_trend[-1] else 'decreasing'
                fee_change_percentage = abs(base_fee_trend[0] - base_fee_trend[-1]) / base_fee_trend[-1] if base_fee_trend[-1] > 0 else 0
            else:
                fee_trend = 'stable'
                fee_change_percentage = 0
            
            return {
                'congestion_level': congestion_level,
                'average_gas_usage': avg_gas_usage,
                'base_fee_trend': fee_trend,
                'fee_change_percentage': fee_change_percentage,
                'pending_transactions': await self._get_pending_tx_count(),
                'current_base_fee': base_fee_trend[0] if base_fee_trend else 0
            }
            
        except Exception as e:
            return {
                'congestion_level': 'unknown',
                'error': str(e)
            }
    
    def _calculate_arbitrage_fees(self, base_fee: int, urgency: str, network_conditions: Dict) -> Dict:
        """Calculate fees for arbitrage transactions (time-sensitive)"""
        base_multiplier = self._get_urgency_multiplier(urgency)
        
        # Arbitrage requires high priority to capture opportunities
        if urgency == 'critical':
            priority_multiplier = 2.0
            max_priority_fee = int(base_fee * 0.2)  # 20% of base fee
        elif urgency == 'high':
            priority_multiplier = 1.5
            max_priority_fee = int(base_fee * 0.15)  # 15% of base fee
        else:
            priority_multiplier = 1.2
            max_priority_fee = int(base_fee * 0.1)   # 10% of base fee
        
        max_fee_per_gas = int(base_fee * base_multiplier * priority_multiplier)
        
        return {
            'maxFeePerGas': max_fee_per_gas,
            'maxPriorityFeePerGas': max_priority_fee,
            'gasLimit': 500000,  # Higher limit for complex arbitrage
            'type': 2,
            'estimated_confirmation_time': self._estimate_confirmation_time(urgency, network_conditions)
        }
    
    def _calculate_lp_fees(self, base_fee: int, urgency: str, network_conditions: Dict) -> Dict:
        """Calculate fees for liquidity provision (less time-sensitive)"""
        base_multiplier = self._get_urgency_multiplier(urgency)
        
        # LP transactions can tolerate slower confirmation
        if urgency == 'high':
            max_priority_fee = int(base_fee * 0.1)   # 10% of base fee
        else:
            max_priority_fee = int(base_fee * 0.05)  # 5% of base fee
        
        max_fee_per_gas = int(base_fee * base_multiplier * 1.1)  # Lower multiplier for LP
        
        return {
            'maxFeePerGas': max_fee_per_gas,
            'maxPriorityFeePerGas': max_priority_fee,
            'gasLimit': 300000,
            'type': 2,
            'estimated_confirmation_time': self._estimate_confirmation_time(urgency, network_conditions)
        }
    
    def _calculate_governance_fees(self, base_fee: int, urgency: str, network_conditions: Dict) -> Dict:
        """Calculate fees for governance transactions (least time-sensitive)"""
        # Governance transactions can wait for low gas periods
        max_priority_fee = int(base_fee * 0.02)  # 2% of base fee
        max_fee_per_gas = int(base_fee * 1.05)   # Just above base fee
        
        return {
            'maxFeePerGas': max_fee_per_gas,
            'maxPriorityFeePerGas': max_priority_fee,
            'gasLimit': 200000,
            'type': 2,
            'estimated_confirmation_time': self._estimate_confirmation_time('low', network_conditions)
        }
    
    def _calculate_general_fees(self, base_fee: int, urgency: str, network_conditions: Dict) -> Dict:
        """Calculate fees for general transactions"""
        base_multiplier = self._get_urgency_multiplier(urgency)
        priority_multiplier = 0.1  # 10% of base fee for general transactions
        
        max_priority_fee = int(base_fee * priority_multiplier)
        max_fee_per_gas = int(base_fee * base_multiplier)
        
        return {
            'maxFeePerGas': max_fee_per_gas,
            'maxPriorityFeePerGas': max_priority_fee,
            'gasLimit': 21000,  # Standard transfer
            'type': 2,
            'estimated_confirmation_time': self._estimate_confirmation_time(urgency, network_conditions)
        }
    
    def _get_urgency_multiplier(self, urgency: str) -> float:
        """Get base fee multiplier based on urgency"""
        multipliers = {
            'critical': 2.0,  # Must confirm in next block
            'high': 1.5,      # Confirm within 2 blocks
            'medium': 1.2,    # Confirm within 5 blocks
            'low': 1.05       # Confirm when convenient
        }
        return multipliers.get(urgency, 1.2)
    
    def _estimate_confirmation_time(self, urgency: str, network_conditions: Dict) -> int:
        """Estimate transaction confirmation time in seconds"""
        base_times = {
            'critical': 12,   # Next block
            'high': 24,       # 2 blocks
            'medium': 60,     # 5 blocks
            'low': 180        # 15 blocks
        }
        
        base_time = base_times.get(urgency, 60)
        
        # Adjust for network congestion
        congestion = network_conditions.get('congestion_level', 'medium')
        if congestion == 'high':
            base_time *= 1.5
        elif congestion == 'low':
            base_time *= 0.8
        
        return int(base_time)
    
    async def _get_pending_tx_count(self) -> int:
        """Get number of pending transactions"""
        try:
            return await self.web3.eth.get_block_transaction_count('pending')
        except:
            return 0
    
    def _update_fee_history(self, fees: Dict, transaction_type: str):
        """Update fee history for analytics"""
        fee_record = {
            'timestamp': time.time(),
            'transaction_type': transaction_type,
            'max_fee_per_gas': fees['maxFeePerGas'],
            'max_priority_fee_per_gas': fees['maxPriorityFeePerGas'],
            'gas_limit': fees['gasLimit']
        }
        
        self.fee_history.append(fee_record)
        if len(self.fee_history) > self.max_history_size:
            self.fee_history.pop(0)
    
    def _calculate_fee_confidence(self) -> float:
        """Calculate confidence score for fee recommendations"""
        if len(self.fee_history) < 10:
            return 0.5
        
        recent_fees = self.fee_history[-10:]
        success_rate = sum(1 for fee in recent_fees if fee.get('success', True)) / len(recent_fees)
        
        return min(1.0, success_rate * 0.8 + 0.2)  # Base confidence with success weighting
    
    async def analyze_fee_efficiency(self, period_hours: int = 24) -> Dict:
        """Analyze fee efficiency over time"""
        if not self.fee_history:
            return {'error': 'Insufficient fee history'}
        
        recent_fees = [fee for fee in self.fee_history 
                      if time.time() - fee['timestamp'] <= period_hours * 3600]
        
        if not recent_fees:
            return {'error': 'No data for specified period'}
        
        total_gas_used = sum(fee['gas_limit'] for fee in recent_fees)
        total_fees_paid = sum(fee['max_fee_per_gas'] * fee['gas_limit'] for fee in recent_fees) / 1e18
        
        avg_fee_per_gas = statistics.mean(fee['max_fee_per_gas'] for fee in recent_fees)
        
        return {
            'analysis_period_hours': period_hours,
            'total_transactions': len(recent_fees),
            'total_gas_used': total_gas_used,
            'total_fees_paid_eth': total_fees_paid,
            'average_fee_per_gas': avg_fee_per_gas,
            'fee_efficiency_score': self._calculate_efficiency_score(recent_fees),
            'recommendations': self._generate_fee_recommendations(recent_fees)
        }
    
    def _calculate_efficiency_score(self, fees: List[Dict]) -> float:
        """Calculate overall fee efficiency score"""
        if not fees:
            return 0.0
        
        # Compare actual fees to network minimums
        efficiency_scores = []
        for fee in fees:
            # Simplified efficiency calculation
            efficiency = min(1.0, 1000000000 / fee['max_fee_per_gas'])  # Lower fees = higher efficiency
            efficiency_scores.append(efficiency)
        
        return statistics.mean(efficiency_scores) if efficiency_scores else 0.0
    
    def _generate_fee_recommendations(self, fees: List[Dict]) -> List[str]:
        """Generate fee optimization recommendations"""
        recommendations = []
        
        avg_fee = statistics.mean(f['max_fee_per_gas'] for f in fees)
        
        if avg_fee > 50000000000:  # 50 Gwei
            recommendations.append("Consider executing during off-peak hours to reduce fees")
        
        if len(fees) > 20:
            recommendations.append("Batch transactions where possible to save gas")
        
        high_priority_count = sum(1 for f in fees if f['max_priority_fee_per_gas'] > f['max_fee_per_gas'] * 0.2)
        if high_priority_count > len(fees) * 0.5:
            recommendations.append("Reduce priority fees for non-time-sensitive transactions")
        
        return recommendations
