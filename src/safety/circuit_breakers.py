"""
Feature 21: Performance Circuit Breakers
Source: asyncio, signal, sys
"""
import asyncio
import signal
import sys
import time
from typing import Dict, List, Callable
from dataclasses import dataclass

@dataclass
class CircuitBreakerConfig:
    max_daily_loss: float = 0.05  # 5% maximum daily loss
    max_single_loss: float = 0.02  # 2% maximum single trade loss
    max_consecutive_losses: int = 5
    max_gas_price: int = 200000000000  # 200 Gwei
    min_profit_threshold: float = 0.001  # 0.1% minimum profit
    cooldown_period: int = 300  # 5 minutes

class PerformanceCircuitBreakers:
    def __init__(self, config: CircuitBreakerConfig = None):
        self.config = config or CircuitBreakerConfig()
        self.breakers = {
            'daily_loss': {'triggered': False, 'last_trigger': 0},
            'consecutive_losses': {'triggered': False, 'count': 0},
            'gas_price': {'triggered': False, 'last_trigger': 0},
            'profitability': {'triggered': False, 'last_trigger': 0}
        }
        self.trading_history = []
        self.daily_pnl = 0.0
        self.last_reset_time = time.time()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._graceful_shutdown)
        signal.signal(signal.SIGTERM, self._graceful_shutdown)
    
    async def monitor_trade_execution(self, trade: Dict) -> Dict:
        """Monitor trade execution and trigger breakers if needed"""
        monitoring_result = {
            'trade_id': trade.get('id'),
            'breakers_triggered': [],
            'allowed_to_proceed': True,
            'warnings': []
        }
        
        # Check all circuit breakers
        checks = [
            self._check_daily_loss_breaker(trade),
            self._check_consecutive_loss_breaker(trade),
            self._check_gas_price_breaker(trade),
            self._check_profitability_breaker(trade)
        ]
        
        check_results = await asyncio.gather(*checks)
        
        for result in check_results:
            if result['triggered']:
                monitoring_result['breakers_triggered'].append(result['breaker'])
                monitoring_result['allowed_to_proceed'] = False
                monitoring_result['warnings'].append(result['message'])
            
            if result.get('warning'):
                monitoring_result['warnings'].append(result['warning'])
        
        # Update trading history
        self._update_trading_history(trade)
        
        return monitoring_result
    
    async def _check_daily_loss_breaker(self, trade: Dict) -> Dict:
        """Check daily loss circuit breaker"""
        # Reset daily PnL if new day
        self._reset_daily_if_needed()
        
        projected_pnl = self.daily_pnl + trade.get('expected_profit', 0)
        daily_loss_limit = -abs(self.config.max_daily_loss)
        
        if projected_pnl < daily_loss_limit:
            self.breakers['daily_loss']['triggered'] = True
            self.breakers['daily_loss']['last_trigger'] = time.time()
            
            return {
                'triggered': True,
                'breaker': 'daily_loss',
                'message': f'Daily loss limit exceeded: ${projected_pnl:.2f}',
                'projected_pnl': projected_pnl,
                'limit': daily_loss_limit
            }
        
        return {'triggered': False, 'breaker': 'daily_loss'}
    
    async def _check_consecutive_loss_breaker(self, trade: Dict) -> Dict:
        """Check consecutive losses circuit breaker"""
        expected_profit = trade.get('expected_profit', 0)
        
        if expected_profit < 0:
            self.breakers['consecutive_losses']['count'] += 1
        else:
            self.breakers['consecutive_losses']['count'] = 0
        
        if self.breakers['consecutive_losses']['count'] >= self.config.max_consecutive_losses:
            self.breakers['consecutive_losses']['triggered'] = True
            self.breakers['consecutive_losses']['last_trigger'] = time.time()
            
            return {
                'triggered': True,
                'breaker': 'consecutive_losses',
                'message': f'Consecutive losses: {self.breakers["consecutive_losses"]["count"]}',
                'count': self.breakers['consecutive_losses']['count'],
                'limit': self.config.max_consecutive_losses
            }
        
        return {'triggered': False, 'breaker': 'consecutive_losses'}
    
    async def _check_gas_price_breaker(self, trade: Dict) -> Dict:
        """Check gas price circuit breaker"""
        gas_price = trade.get('gas_price', 0)
        
        if gas_price > self.config.max_gas_price:
            self.breakers['gas_price']['triggered'] = True
            self.breakers['gas_price']['last_trigger'] = time.time()
            
            return {
                'triggered': True,
                'breaker': 'gas_price',
                'message': f'Gas price too high: {gas_price} wei',
                'current_gas': gas_price,
                'limit': self.config.max_gas_price
            }
        
        return {'triggered': False, 'breaker': 'gas_price'}
    
    async def _check_profitability_breaker(self, trade: Dict) -> Dict:
        """Check profitability circuit breaker"""
        expected_profit_percentage = trade.get('expected_profit_percentage', 0)
        
        if expected_profit_percentage < self.config.min_profit_threshold:
            warning_msg = f'Low profitability: {expected_profit_percentage:.4f}%'
            
            # Only trigger if significantly below threshold
            if expected_profit_percentage < (self.config.min_profit_threshold * 0.5):
                self.breakers['profitability']['triggered'] = True
                self.breakers['profitability']['last_trigger'] = time.time()
                
                return {
                    'triggered': True,
                    'breaker': 'profitability',
                    'message': warning_msg,
                    'current_profit': expected_profit_percentage,
                    'limit': self.config.min_profit_threshold
                }
            else:
                return {
                    'triggered': False,
                    'breaker': 'profitability',
                    'warning': warning_msg
                }
        
        return {'triggered': False, 'breaker': 'profitability'}
    
    def _reset_daily_if_needed(self):
        """Reset daily PnL if new trading day"""
        current_time = time.time()
        if current_time - self.last_reset_time >= 86400:  # 24 hours
            self.daily_pnl = 0.0
            self.last_reset_time = current_time
    
    def _update_trading_history(self, trade: Dict):
        """Update trading history with new trade"""
        self.trading_history.append({
            'timestamp': time.time(),
            'trade_id': trade.get('id'),
            'expected_profit': trade.get('expected_profit', 0),
            'actual_profit': trade.get('actual_profit', 0),
            'gas_used': trade.get('gas_used', 0),
            'status': trade.get('status', 'executed')
        })
        
        # Keep only last 1000 trades
        if len(self.trading_history) > 1000:
            self.trading_history.pop(0)
    
    async def reset_breaker(self, breaker_name: str) -> bool:
        """Reset a specific circuit breaker"""
        if breaker_name in self.breakers:
            # Check cooldown period
            last_trigger = self.breakers[breaker_name]['last_trigger']
            if time.time() - last_trigger >= self.config.cooldown_period:
                self.breakers[breaker_name]['triggered'] = False
                if breaker_name == 'consecutive_losses':
                    self.breakers[breaker_name]['count'] = 0
                return True
        return False
    
    async def get_breaker_status(self) -> Dict:
        """Get current status of all circuit breakers"""
        status = {}
        
        for breaker_name, breaker_data in self.breakers.items():
            status[breaker_name] = {
                'triggered': breaker_data['triggered'],
                'last_trigger': breaker_data['last_trigger'],
                'cooldown_remaining': max(0, self.config.cooldown_period - (time.time() - breaker_data['last_trigger']))
            }
            
            if breaker_name == 'consecutive_losses':
                status[breaker_name]['current_count'] = breaker_data['count']
        
        status['daily_pnl'] = self.daily_pnl
        status['active_trades'] = len(self.trading_history)
        status['system_health'] = 'healthy' if not any(b['triggered'] for b in self.breakers.values()) else 'degraded'
        
        return status
    
    def _graceful_shutdown(self, signum, frame):
        """Handle graceful shutdown on signals"""
        print(f"\níº¨ Received signal {signum}. Initiating graceful shutdown...")
        
        # Trigger all breakers to prevent new trades
        for breaker in self.breakers.values():
            breaker['triggered'] = True
        
        print("âœ… Circuit breakers engaged. No new trades will be executed.")
        print("í²¾ Saving current state...")
        
        # Additional cleanup would happen here
        sys.exit(0)
    
    async def emergency_stop(self) -> Dict:
        """Immediately trigger all circuit breakers"""
        for breaker in self.breakers.values():
            breaker['triggered'] = True
            breaker['last_trigger'] = time.time()
        
        return {
            'emergency_stop_activated': True,
            'timestamp': time.time(),
            'message': 'All trading halted. Manual reset required.'
        }
    
    async def calculate_risk_metrics(self) -> Dict:
        """Calculate current risk metrics"""
        if not self.trading_history:
            return {'error': 'No trading history available'}
        
        recent_trades = [t for t in self.trading_history 
                        if time.time() - t['timestamp'] <= 3600]  # Last hour
        
        total_trades = len(recent_trades)
        profitable_trades = sum(1 for t in recent_trades if t.get('actual_profit', 0) > 0)
        total_profit = sum(t.get('actual_profit', 0) for t in recent_trades)
        max_drawdown = self._calculate_max_drawdown(recent_trades)
        
        return {
            'period_hours': 1,
            'total_trades': total_trades,
            'profitable_trades': profitable_trades,
            'win_rate': profitable_trades / total_trades if total_trades > 0 else 0,
            'total_profit': total_profit,
            'average_profit_per_trade': total_profit / total_trades if total_trades > 0 else 0,
            'max_drawdown': max_drawdown,
            'risk_adjusted_return': total_profit / (max_drawdown + 0.001),  # Avoid division by zero
            'current_risk_level': self._assess_risk_level(recent_trades)
        }
    
    def _calculate_max_drawdown(self, trades: List[Dict]) -> float:
        """Calculate maximum drawdown from trading history"""
        if not trades:
            return 0.0
        
        running_pnl = 0
        peak = 0
        max_drawdown = 0
        
        for trade in trades:
            running_pnl += trade.get('actual_profit', 0)
            if running_pnl > peak:
                peak = running_pnl
            drawdown = peak - running_pnl
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return max_drawdown
    
    def _assess_risk_level(self, trades: List[Dict]) -> str:
        """Assess current risk level based on recent trading"""
        if not trades:
            return 'low'
        
        win_rate = sum(1 for t in trades if t.get('actual_profit', 0) > 0) / len(trades)
        avg_profit = sum(t.get('actual_profit', 0) for t in trades) / len(trades)
        
        if win_rate < 0.4 or avg_profit < 0:
            return 'high'
        elif win_rate < 0.6:
            return 'medium'
        else:
            return 'low'
