"""
Feature 17: Auto-Compounding Profit Engine
Source: web3.py, defi-protocols
"""
from web3 import Web3
import asyncio
from typing import Dict, List
import time
from decimal import Decimal

class AutoCompoundingEngine:
    def __init__(self, web3: Web3):
        self.web3 = web3
        self.compounding_strategies = {}
        self.profit_reinvestment_rate = 0.8  # Reinvest 80% of profits
        
    async def auto_compound_profits(self, strategy_id: str, profits: List[Dict]) -> Dict:
        """Automatically compound profits back into strategies"""
        try:
            total_profits = sum(profit['amount'] for profit in profits)
            reinvestment_amount = total_profits * self.profit_reinvestment_rate
            
            # Distribute reinvestment across strategies
            allocation_plan = await self._calculate_reinvestment_allocation(strategy_id, reinvestment_amount)
            
            # Execute reinvestment transactions
            reinvestment_results = await self._execute_reinvestments(allocation_plan)
            
            # Update compounding history
            await self._update_compounding_history(strategy_id, total_profits, reinvestment_amount, reinvestment_results)
            
            return {
                'strategy_id': strategy_id,
                'total_profits': total_profits,
                'reinvestment_amount': reinvestment_amount,
                'reinvestment_rate': self.profit_reinvestment_rate,
                'allocation_plan': allocation_plan,
                'execution_results': reinvestment_results,
                'compounding_cycle': self._get_compounding_cycle(strategy_id),
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'strategy_id': strategy_id,
                'success': False,
                'error': str(e)
            }
    
    async def _calculate_reinvestment_allocation(self, strategy_id: str, total_amount: float) -> Dict:
        """Calculate optimal allocation for profit reinvestment"""
        strategy_performance = await self._get_strategy_performance(strategy_id)
        
        allocations = {}
        remaining_amount = total_amount
        
        # Allocate based on performance metrics
        for strategy in strategy_performance:
            allocation_score = self._calculate_allocation_score(strategy)
            allocation_percentage = allocation_score / sum(s['allocation_score'] for s in strategy_performance)
            
            allocated_amount = total_amount * allocation_percentage
            allocations[strategy['id']] = {
                'amount': allocated_amount,
                'percentage': allocation_percentage * 100,
                'score': allocation_score,
                'rationale': strategy.get('rationale', 'performance_based')
            }
            remaining_amount -= allocated_amount
        
        # Distribute any remaining amount to top performer
        if remaining_amount > 0 and allocations:
            top_strategy = max(allocations.items(), key=lambda x: x[1]['score'])
            allocations[top_strategy[0]]['amount'] += remaining_amount
        
        return allocations
    
    def _calculate_allocation_score(self, strategy: Dict) -> float:
        """Calculate allocation score based on multiple factors"""
        score = 0.0
        
        # Sharpe ratio component (30%)
        sharpe_weight = 0.3
        sharpe_score = min(strategy.get('sharpe_ratio', 0) / 2.0, 1.0)  # Normalize to 0-1
        score += sharpe_score * sharpe_weight
        
        # Win rate component (25%)
        win_rate_weight = 0.25
        win_rate_score = strategy.get('win_rate', 0) / 100.0
        score += win_rate_score * win_rate_weight
        
        # Recent performance component (20%)
        recent_perf_weight = 0.2
        recent_perf = min(strategy.get('recent_profit_percentage', 0) / 50.0, 1.0)
        score += recent_perf * recent_perf_weight
        
        # Risk-adjusted return component (25%)
        risk_adj_weight = 0.25
        risk_adj_score = strategy.get('risk_adjusted_return', 0) / 10.0
        score += risk_adj_score * risk_adj_weight
        
        return max(0.0, min(1.0, score))
    
    async def _execute_reinvestments(self, allocation_plan: Dict) -> Dict:
        """Execute reinvestment transactions on blockchain"""
        results = {}
        
        for strategy_id, allocation in allocation_plan.items():
            if allocation['amount'] > 0:
                try:
                    # Execute the reinvestment transaction
                    tx_result = await self._execute_reinvestment_tx(strategy_id, allocation['amount'])
                    results[strategy_id] = {
                        'success': True,
                        'transaction_hash': tx_result['hash'],
                        'amount': allocation['amount'],
                        'gas_used': tx_result.get('gas_used', 0),
                        'timestamp': time.time()
                    }
                except Exception as e:
                    results[strategy_id] = {
                        'success': False,
                        'error': str(e),
                        'amount': allocation['amount']
                    }
        
        return results
    
    async def _execute_reinvestment_tx(self, strategy_id: str, amount: float) -> Dict:
        """Execute single reinvestment transaction"""
        # This would interact with actual DeFi protocols
        # Simplified for example
        
        return {
            'hash': f"0x{hash(f'{strategy_id}{amount}{time.time()}')}",
            'gas_used': 150000,
            'status': 'success'
        }
    
    async def _get_strategy_performance(self, strategy_id: str) -> List[Dict]:
        """Get performance data for all strategies"""
        # Mock data - in production would query database or on-chain data
        return [
            {
                'id': 'flash_loan_arbitrage',
                'sharpe_ratio': 2.1,
                'win_rate': 85.5,
                'recent_profit_percentage': 12.3,
                'risk_adjusted_return': 8.7,
                'rationale': 'High frequency arbitrage with consistent returns'
            },
            {
                'id': 'liquidity_provision',
                'sharpe_ratio': 1.8,
                'win_rate': 92.0,
                'recent_profit_percentage': 8.9,
                'risk_adjusted_return': 7.2,
                'rationale': 'Stable fee income from LP positions'
            },
            {
                'id': 'yield_farming',
                'sharpe_ratio': 1.5,
                'win_rate': 78.0,
                'recent_profit_percentage': 15.2,
                'risk_adjusted_return': 6.8,
                'rationale': 'High yield opportunities with impermanent loss risk'
            }
        ]
    
    async def _update_compounding_history(self, strategy_id: str, total_profits: float, reinvested: float, results: Dict):
        """Update compounding history for analytics"""
        successful_reinvestments = sum(1 for r in results.values() if r['success'])
        
        self.compounding_strategies[strategy_id] = {
            'last_compounded': time.time(),
            'total_profits_compounded': total_profits,
            'reinvestment_rate': self.profit_reinvestment_rate,
            'successful_reinvestments': successful_reinvestments,
            'total_reinvestment_count': len(results)
        }
    
    def _get_compounding_cycle(self, strategy_id: str) -> int:
        """Get current compounding cycle for strategy"""
        if strategy_id in self.compounding_strategies:
            return self.compounding_strategies[strategy_id].get('cycle', 0) + 1
        return 1
    
    def calculate_compounding_growth(self, initial_capital: float, periods: int, avg_return: float) -> Dict:
        """Calculate potential growth with compounding"""
        final_amount = initial_capital * ((1 + avg_return) ** periods)
        total_profit = final_amount - initial_capital
        annualized_return = ((final_amount / initial_capital) ** (1 / periods)) - 1
        
        return {
            'initial_capital': initial_capital,
            'periods': periods,
            'final_amount': final_amount,
            'total_profit': total_profit,
            'annualized_return': annualized_return,
            'compounding_multiplier': final_amount / initial_capital
        }
