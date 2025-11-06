"""
Feature 33: Stress Testing Module
Source: Monte Carlo, VAR, Extreme Value Theory
"""
import numpy as np
import pandas as pd
from scipy import stats
import asyncio
from typing import Dict, List, Tuple
import time
from dataclasses import dataclass
from enum import Enum

class ScenarioType(Enum):
    FLASH_CRASH = "flash_crash"
    GAS_SPIKE = "gas_spike" 
    EXCHANGE_OUTAGE = "exchange_outage"
    LIQUIDITY_CRISIS = "liquidity_crisis"
    REGULATORY_SHOCK = "regulatory_shock"
    NETWORK_CONGESTION = "network_congestion"

@dataclass
class StressScenario:
    name: str
    scenario_type: ScenarioType
    parameters: Dict
    probability: float
    severity: str  # low, medium, high, extreme

@dataclass
class StressTestResult:
    scenario: StressScenario
    portfolio_impact: float
    max_drawdown: float
    var_95: float
    expected_shortfall: float
    survival_probability: float
    recommendations: List[str]
    executed_at: float

class StressTesting:
    def __init__(self):
        self.scenarios = self._initialize_scenarios()
        self.historical_data = {}
        self.monte_carlo_iterations = 10000
        
    def _initialize_scenarios(self) -> List[StressScenario]:
        """Initialize predefined stress scenarios"""
        return [
            StressScenario(
                name="2020-style Flash Crash",
                scenario_type=ScenarioType.FLASH_CRASH,
                parameters={
                    'volatility_spike': 0.15,
                    'liquidity_drop': 0.8,
                    'price_decline': 0.35,
                    'recovery_time_hours': 6
                },
                probability=0.05,
                severity="extreme"
            ),
            StressScenario(
                name="Ethereum Gas Crisis",
                scenario_type=ScenarioType.GAS_SPIKE,
                parameters={
                    'gas_price_gwei': 500,
                    'network_congestion': 0.9,
                    'failed_transaction_rate': 0.3,
                    'duration_hours': 24
                },
                probability=0.15,
                severity="high"
            ),
            StressScenario(
                name="Major Exchange Outage",
                scenario_type=ScenarioType.EXCHANGE_OUTAGE,
                parameters={
                    'available_exchanges': 1,
                    'slippage_increase': 0.1,
                    'withdrawal_delay_hours': 12,
                    'affected_assets': ['ETH', 'BTC', 'USDC']
                },
                probability=0.08,
                severity="medium"
            ),
            StressScenario(
                name="DeFi Liquidity Crisis",
                scenario_type=ScenarioType.LIQUIDITY_CRISIS,
                parameters={
                    'tvl_drop': 0.6,
                    'yield_compression': 0.02,
                    'impermanent_loss_multiplier': 3.0,
                    'protocol_failures': 2
                },
                probability=0.12,
                severity="high"
            ),
            StressScenario(
                name="Regulatory Crackdown",
                scenario_type=ScenarioType.REGULATORY_SHOCK,
                parameters={
                    'jurisdiction_restrictions': 3,
                    'compliance_costs_multiplier': 2.5,
                    'market_confidence_drop': 0.4,
                    'legal_fees_millions': 5.0
                },
                probability=0.03,
                severity="extreme"
            )
        ]
    
    async def run_comprehensive_stress_tests(self, portfolio: Dict) -> Dict:
        """Run comprehensive stress testing across all scenarios"""
        start_time = time.time()
        results = {}
        
        # Run scenarios in parallel
        tasks = []
        for scenario in self.scenarios:
            task = self._run_single_scenario(scenario, portfolio)
            tasks.append(task)
        
        scenario_results = await asyncio.gather(*tasks)
        
        # Aggregate results
        for scenario, result in zip(self.scenarios, scenario_results):
            results[scenario.name] = result
        
        # Calculate overall metrics
        overall_metrics = self._calculate_overall_metrics(results)
        
        return {
            'stress_test_id': f"stress_test_{int(time.time())}",
            'execution_time': time.time() - start_time,
            'portfolio_value': portfolio.get('total_value', 0),
            'scenario_results': results,
            'overall_metrics': overall_metrics,
            'recommendations': self._generate_overall_recommendations(results, overall_metrics),
            'timestamp': time.time()
        }
    
    async def _run_single_scenario(self, scenario: StressScenario, portfolio: Dict) -> StressTestResult:
        """Run stress test for a single scenario"""
        try:
            if scenario.scenario_type == ScenarioType.FLASH_CRASH:
                impact_analysis = await self._simulate_flash_crash(scenario, portfolio)
            elif scenario.scenario_type == ScenarioType.GAS_SPIKE:
                impact_analysis = await self._simulate_gas_spike(scenario, portfolio)
            elif scenario.scenario_type == ScenarioType.EXCHANGE_OUTAGE:
                impact_analysis = await self._simulate_exchange_outage(scenario, portfolio)
            elif scenario.scenario_type == ScenarioType.LIQUIDITY_CRISIS:
                impact_analysis = await self._simulate_liquidity_crisis(scenario, portfolio)
            elif scenario.scenario_type == ScenarioType.REGULATORY_SHOCK:
                impact_analysis = await self._simulate_regulatory_shock(scenario, portfolio)
            else:
                impact_analysis = await self._simulate_generic_scenario(scenario, portfolio)
            
            # Calculate risk metrics
            risk_metrics = self._calculate_risk_metrics(impact_analysis)
            
            # Generate recommendations
            recommendations = self._generate_scenario_recommendations(scenario, risk_metrics)
            
            return StressTestResult(
                scenario=scenario,
                portfolio_impact=risk_metrics['portfolio_impact'],
                max_drawdown=risk_metrics['max_drawdown'],
                var_95=risk_metrics['var_95'],
                expected_shortfall=risk_metrics['expected_shortfall'],
                survival_probability=risk_metrics['survival_probability'],
                recommendations=recommendations,
                executed_at=time.time()
            )
            
        except Exception as e:
            # Return failed result
            return StressTestResult(
                scenario=scenario,
                portfolio_impact=0.0,
                max_drawdown=0.0,
                var_95=0.0,
                expected_shortfall=0.0,
                survival_probability=0.0,
                recommendations=[f"Stress test failed: {str(e)}"],
                executed_at=time.time()
            )
    
    async def _simulate_flash_crash(self, scenario: StressScenario, portfolio: Dict) -> Dict:
        """Simulate flash crash scenario using Monte Carlo"""
        params = scenario.parameters
        
        # Generate correlated asset returns with extreme moves
        n_assets = len(portfolio.get('positions', []))
        if n_assets == 0:
            n_assets = 1
        
        # Create correlation matrix (assets become highly correlated during crashes)
        base_correlation = 0.3
        crash_correlation = 0.8
        correlation_matrix = np.full((n_assets, n_assets), crash_correlation)
        np.fill_diagonal(correlation_matrix, 1.0)
        
        # Cholesky decomposition for correlated random numbers
        L = np.linalg.cholesky(correlation_matrix)
        
        # Monte Carlo simulation
        portfolio_values = []
        for _ in range(self.monte_carlo_iterations):
            # Generate correlated random shocks
            uncorrelated_shocks = np.random.normal(0, params['volatility_spike'], n_assets)
            correlated_shocks = L @ uncorrelated_shocks
            
            # Calculate portfolio impact
            portfolio_return = np.mean(correlated_shocks) * params['price_decline']
            liquidity_impact = (1 - params['liquidity_drop']) * 0.5  # Reduced execution capability
            
            total_impact = portfolio_return - liquidity_impact
            portfolio_value = portfolio.get('total_value', 1) * (1 + total_impact)
            portfolio_values.append(portfolio_value)
        
        return {
            'scenario_type': 'flash_crash',
            'portfolio_values': portfolio_values,
            'liquidity_impact': params['liquidity_drop'],
            'recovery_time': params['recovery_time_hours']
        }
    
    async def _simulate_gas_spike(self, scenario: StressScenario, portfolio: Dict) -> Dict:
        """Simulate gas price spike scenario"""
        params = scenario.parameters
        
        # Calculate transaction cost impact
        base_gas_price = 30  # Gwei
        spike_gas_price = params['gas_price_gwei']
        gas_cost_multiplier = spike_gas_price / base_gas_price
        
        # Estimate failed transactions
        failed_tx_rate = params['failed_transaction_rate']
        
        # Impact on flash loan profitability
        typical_flash_loan_gas = 500000  # gas units
        base_gas_cost_eth = typical_flash_loan_gas * base_gas_price * 1e-9
        spike_gas_cost_eth = typical_flash_loan_gas * spike_gas_price * 1e-9
        
        gas_cost_increase = spike_gas_cost_eth - base_gas_cost_eth
        gas_cost_increase_usd = gas_cost_increase * 1800  # Assuming $1800 ETH
        
        # Monte Carlo simulation for profitability impact
        profitability_impacts = []
        for _ in range(self.monte_carlo_iterations):
            # Random failed transactions
            failed_txs = np.random.binomial(10, failed_tx_rate)  # 10 transactions attempted
            
            # Profit reduction from gas costs and failed transactions
            gas_impact = gas_cost_increase_usd * 10  # 10 transactions
            failed_tx_impact = portfolio.get('avg_profit_per_trade', 1000) * failed_txs
            
            total_impact = gas_impact + failed_tx_impact
            profitability_impacts.append(total_impact)
        
        return {
            'scenario_type': 'gas_spike',
            'profitability_impacts': profitability_impacts,
            'gas_cost_increase_usd': gas_cost_increase_usd,
            'failed_tx_rate': failed_tx_rate,
            'duration_hours': params['duration_hours']
        }
    
    async def _simulate_exchange_outage(self, scenario: StressScenario, portfolio: Dict) -> Dict:
        """Simulate exchange outage scenario"""
        params = scenario.parameters
        
        # Reduced execution venues increase slippage
        base_slippage = 0.002  # 0.2%
        crisis_slippage = base_slippage + params['slippage_increase']
        
        # Available liquidity reduction
        available_exchanges = params['available_exchanges']
        base_exchanges = 5  # Assume 5 exchanges normally available
        liquidity_multiplier = available_exchanges / base_exchanges
        
        # Monte Carlo simulation
        execution_impacts = []
        for _ in range(self.monte_carlo_iterations):
            # Random slippage based on reduced liquidity
            actual_slippage = np.random.normal(crisis_slippage, crisis_slippage * 0.3)
            actual_slippage = max(actual_slippage, crisis_slippage * 0.5)
            
            # Impact per trade
            trade_size = portfolio.get('avg_trade_size', 50000)
            slippage_cost = trade_size * actual_slippage
            
            # Additional costs from withdrawal delays
            delay_cost = portfolio.get('daily_volume', 1000000) * 0.001  # 0.1% opportunity cost
            
            total_impact = slippage_cost + delay_cost
            execution_impacts.append(total_impact)
        
        return {
            'scenario_type': 'exchange_outage',
            'execution_impacts': execution_impacts,
            'slippage_increase': params['slippage_increase'],
            'available_exchanges': available_exchanges,
            'withdrawal_delay_hours': params['withdrawal_delay_hours']
        }
    
    async def _simulate_liquidity_crisis(self, scenario: StressScenario, portfolio: Dict) -> Dict:
        """Simulate DeFi liquidity crisis scenario"""
        params = scenario.parameters
        
        # TVL drop impacts yields and arbitrage opportunities
        base_tvl = 1.0  # normalized
        crisis_tvl = base_tvl * (1 - params['tvl_drop'])
        
        # Yield compression
        base_yield = 0.05  # 5% APY
        crisis_yield = base_yield * (1 - params['yield_compression'])
        
        # Impermanent loss multiplier
        il_multiplier = params['impermanent_loss_multiplier']
        
        # Monte Carlo simulation
        liquidity_impacts = []
        for _ in range(self.monte_carlo_iterations):
            # Random protocol failure impact
            protocol_failures = np.random.poisson(params['protocol_failures'])
            failure_impact = protocol_failures * portfolio.get('avg_position_size', 10000) * 0.1  # 10% loss per failure
            
            # Yield impact
            yield_impact = (base_yield - crisis_yield) * portfolio.get('lp_positions_value', 0)
            
            # Impermanent loss impact
            il_impact = portfolio.get('lp_positions_value', 0) * 0.02 * il_multiplier  # Base 2% IL multiplied
            
            total_impact = failure_impact + yield_impact + il_impact
            liquidity_impacts.append(total_impact)
        
        return {
            'scenario_type': 'liquidity_crisis',
            'liquidity_impacts': liquidity_impacts,
            'tvl_drop': params['tvl_drop'],
            'yield_compression': params['yield_compression'],
            'il_multiplier': il_multiplier
        }
    
    async def _simulate_regulatory_shock(self, scenario: StressScenario, portfolio: Dict) -> Dict:
        """Simulate regulatory shock scenario"""
        params = scenario.parameters
        
        # Direct compliance costs
        compliance_cost = params['compliance_costs_multiplier'] * portfolio.get('annual_revenue', 1000000) * 0.05  # 5% base compliance
        
        # Legal fees
        legal_fees = params['legal_fees_millions'] * 1e6
        
        # Market confidence impact on volumes and profitability
        confidence_drop = params['market_confidence_drop']
        
        # Monte Carlo simulation
        regulatory_impacts = []
        for _ in range(self.monte_carlo_iterations):
            # Random legal outcome
            legal_multiplier = np.random.uniform(0.5, 2.0)  # Legal costs can vary
            
            # Volume reduction impact
            volume_reduction = np.random.normal(confidence_drop, confidence_drop * 0.2)
            volume_impact = portfolio.get('daily_volume', 1000000) * volume_reduction * portfolio.get('profit_margin', 0.001)
            
            total_impact = (compliance_cost * legal_multiplier) + legal_fees + volume_impact
            regulatory_impacts.append(total_impact)
        
        return {
            'scenario_type': 'regulatory_shock',
            'regulatory_impacts': regulatory_impacts,
            'compliance_cost_multiplier': params['compliance_costs_multiplier'],
            'legal_fees': legal_fees,
            'confidence_drop': confidence_drop
        }
    
    async def _simulate_generic_scenario(self, scenario: StressScenario, portfolio: Dict) -> Dict:
        """Generic scenario simulation fallback"""
        # Simple Monte Carlo based on scenario severity
        severity_multipliers = {
            'low': 0.1,
            'medium': 0.25,
            'high': 0.5,
            'extreme': 0.75
        }
        
        multiplier = severity_multipliers.get(scenario.severity, 0.25)
        
        impacts = []
        for _ in range(self.monte_carlo_iterations):
            # Random impact based on severity
            impact = np.random.normal(multiplier, multiplier * 0.3)
            impact = max(0, impact)  # No negative impacts
            portfolio_impact = portfolio.get('total_value', 1) * impact
            impacts.append(portfolio_impact)
        
        return {
            'scenario_type': 'generic',
            'impacts': impacts,
            'severity_multiplier': multiplier
        }
    
    def _calculate_risk_metrics(self, impact_analysis: Dict) -> Dict:
        """Calculate risk metrics from impact analysis"""
        if 'portfolio_values' in impact_analysis:
            values = impact_analysis['portfolio_values']
        elif 'profitability_impacts' in impact_analysis:
            base_value = 1  # Normalized
            values = [base_value - impact for impact in impact_analysis['profitability_impacts']]
        elif 'execution_impacts' in impact_analysis:
            base_value = 1
            values = [base_value - impact/100000 for impact in impact_analysis['execution_impacts']]  # Normalize
        elif 'liquidity_impacts' in impact_analysis:
            base_value = 1
            values = [base_value - impact/100000 for impact in impact_analysis['liquidity_impacts']]
        elif 'regulatory_impacts' in impact_analysis:
            base_value = 1
            values = [base_value - impact/1000000 for impact in impact_analysis['regulatory_impacts']]
        else:
            values = impact_analysis.get('impacts', [1])
        
        values = np.array(values)
        
        # Portfolio impact (average loss)
        portfolio_impact = 1 - np.mean(values)
        
        # Maximum drawdown
        max_drawdown = 1 - np.min(values)
        
        # Value at Risk (95%)
        var_95 = 1 - np.percentile(values, 5)
        
        # Expected Shortfall (CVaR)
        var_threshold = np.percentile(values, 5)
        tail_losses = values[values <= var_threshold]
        expected_shortfall = 1 - np.mean(tail_losses) if len(tail_losses) > 0 else 0
        
        # Survival probability (probability of losing less than 50%)
        survival_probability = np.mean(values >= 0.5)
        
        return {
            'portfolio_impact': float(portfolio_impact),
            'max_drawdown': float(max_drawdown),
            'var_95': float(var_95),
            'expected_shortfall': float(expected_shortfall),
            'survival_probability': float(survival_probability)
        }
    
    def _generate_scenario_recommendations(self, scenario: StressScenario, risk_metrics: Dict) -> List[str]:
        """Generate recommendations for a specific scenario"""
        recommendations = []
        
        portfolio_impact = risk_metrics['portfolio_impact']
        max_drawdown = risk_metrics['max_drawdown']
        
        if portfolio_impact > 0.5:
            recommendations.append(f"IMMEDIATE: Develop contingency plan for {scenario.name}")
            recommendations.append(f"URGENT: Reduce exposure by at least {int(portfolio_impact * 100)}%")
        
        elif portfolio_impact > 0.25:
            recommendations.append(f"HEDGE: Implement hedging strategy for {scenario.scenario_type.value}")
            recommendations.append(f"MONITOR: Increase monitoring frequency during stress conditions")
        
        if max_drawdown > 0.7:
            recommendations.append("CAPITAL PRESERVATION: Activate emergency capital protection measures")
        
        if risk_metrics['survival_probability'] < 0.5:
            recommendations.append("SURVIVAL: Ensure sufficient liquidity for survival in extreme conditions")
        
        # Scenario-specific recommendations
        if scenario.scenario_type == ScenarioType.FLASH_CRASH:
            recommendations.append("Implement circuit breakers and position limits")
            recommendations.append("Diversify across non-correlated assets")
        
        elif scenario.scenario_type == ScenarioType.GAS_SPIKE:
            recommendations.append("Use Layer 2 solutions for high-frequency trading")
            recommendations.append("Implement gas price monitoring and alerts")
        
        elif scenario.scenario_type == ScenarioType.EXCHANGE_OUTAGE:
            recommendations.append("Maintain accounts on multiple exchanges")
            recommendations.append("Develop manual override procedures")
        
        if len(recommendations) == 0:
            recommendations.append("Current risk exposure appears manageable for this scenario")
        
        return recommendations
    
    def _calculate_overall_metrics(self, scenario_results: Dict) -> Dict:
        """Calculate overall stress test metrics"""
        portfolio_impacts = [r.portfolio_impact for r in scenario_results.values()]
        max_drawdowns = [r.max_drawdown for r in scenario_results.values()]
        var_95s = [r.var_95 for r in scenario_results.values()]
        
        return {
            'worst_case_impact': max(portfolio_impacts) if portfolio_impacts else 0,
            'average_impact': np.mean(portfolio_impacts) if portfolio_impacts else 0,
            'max_drawdown_across_scenarios': max(max_drawdowns) if max_drawdowns else 0,
            'highest_var_95': max(var_95s) if var_95s else 0,
            'scenarios_above_50pct_impact': sum(1 for impact in portfolio_impacts if impact > 0.5),
            'overall_risk_score': self._calculate_overall_risk_score(scenario_results)
        }
    
    def _calculate_overall_risk_score(self, scenario_results: Dict) -> float:
        """Calculate overall risk score (0-100, higher = riskier)"""
        if not scenario_results:
            return 0.0
        
        total_score = 0.0
        max_score = 0.0
        
        for scenario_name, result in scenario_results.items():
            scenario = result.scenario
            
            # Weight by probability and severity
            probability_weight = scenario.probability * 100
            severity_weight = {
                'low': 1,
                'medium': 2,
                'high': 3,
                'extreme': 5
            }.get(scenario.severity, 1)
            
            impact_weight = result.portfolio_impact * 100
            
            scenario_score = probability_weight * severity_weight * impact_weight
            total_score += scenario_score
            max_score += probability_weight * severity_weight * 100
        
        return (total_score / max_score * 100) if max_score > 0 else 0.0
    
    def _generate_overall_recommendations(self, scenario_results: Dict, overall_metrics: Dict) -> List[str]:
        """Generate overall recommendations based on all scenarios"""
        recommendations = []
        
        risk_score = overall_metrics['overall_risk_score']
        worst_case_impact = overall_metrics['worst_case_impact']
        
        if risk_score > 70:
            recommendations.append("íº¨ CRITICAL: Overall risk level extremely high - immediate action required")
            recommendations.append("Reduce total exposure by at least 50%")
            recommendations.append("Implement all scenario-specific recommendations")
        
        elif risk_score > 50:
            recommendations.append("âš ï¸ HIGH: Significant risk exposure detected")
            recommendations.append("Review and implement high-priority scenario recommendations")
            recommendations.append("Consider reducing leverage and position sizes")
        
        elif risk_score > 30:
            recommendations.append("â„¹ï¸ MODERATE: Manageable risk level with proper controls")
            recommendations.append("Implement selective hedging strategies")
            recommendations.append("Maintain current monitoring frequency")
        
        else:
            recommendations.append("âœ… LOW: Risk exposure within acceptable limits")
            recommendations.append("Continue current risk management practices")
            recommendations.append("Regularly review stress test results")
        
        if worst_case_impact > 0.8:
            recommendations.append("SURVIVAL: Ensure business continuity plan for extreme scenarios")
        
        if overall_metrics['scenarios_above_50pct_impact'] > 2:
            recommendations.append("DIVERSIFY: Reduce concentration in vulnerable strategies")
        
        return recommendations
    
    async def sensitivity_analysis(self, portfolio: Dict, parameter: str, range_min: float, range_max: float, steps: int = 10) -> Dict:
        """Run sensitivity analysis for a specific parameter"""
        results = []
        
        for value in np.linspace(range_min, range_max, steps):
            # Modify portfolio parameter
            modified_portfolio = portfolio.copy()
            if parameter in modified_portfolio:
                modified_portfolio[parameter] = value
            
            # Run stress test
            stress_test_result = await self.run_comprehensive_stress_tests(modified_portfolio)
            
            results.append({
                'parameter_value': value,
                'risk_score': stress_test_result['overall_metrics']['overall_risk_score'],
                'worst_case_impact': stress_test_result['overall_metrics']['worst_case_impact']
            })
        
        return {
            'parameter': parameter,
            'analysis_range': [range_min, range_max],
            'steps': steps,
            'results': results,
            'sensitivity_score': self._calculate_sensitivity_score(results)
        }
    
    def _calculate_sensitivity_score(self, results: List[Dict]) -> float:
        """Calculate sensitivity score for parameter analysis"""
        if len(results) < 2:
            return 0.0
        
        risk_scores = [r['risk_score'] for r in results]
        return float(np.std(risk_scores) / np.mean(risk_scores) if np.mean(risk_scores) > 0 else 0.0)
    
    def generate_stress_test_report(self, stress_test_results: Dict) -> Dict:
        """Generate comprehensive stress test report"""
        return {
            'report_id': stress_test_results['stress_test_id'],
            'generated_at': time.time(),
            'executive_summary': self._generate_executive_summary(stress_test_results),
            'detailed_analysis': stress_test_results,
            'key_risk_indicators': self._extract_key_risk_indicators(stress_test_results),
            'action_plan': self._generate_action_plan(stress_test_results),
            'next_review_date': time.time() + 30 * 24 * 3600  # 30 days from now
        }
    
    def _generate_executive_summary(self, results: Dict) -> Dict:
        """Generate executive summary of stress test results"""
        overall_metrics = results['overall_metrics']
        
        return {
            'overall_risk_level': 'CRITICAL' if overall_metrics['overall_risk_score'] > 70 else
                                 'HIGH' if overall_metrics['overall_risk_score'] > 50 else
                                 'MODERATE' if overall_metrics['overall_risk_score'] > 30 else 'LOW',
            'key_findings': [
                f"Worst-case scenario impact: {overall_metrics['worst_case_impact']:.1%}",
                f"Maximum drawdown across scenarios: {overall_metrics['max_drawdown_across_scenarios']:.1%}",
                f"Scenarios with >50% impact: {overall_metrics['scenarios_above_50pct_impact']}",
                f"Overall risk score: {overall_metrics['overall_risk_score']:.1f}/100"
            ],
            'immediate_actions': [r for r in results['recommendations'] if 'IMMEDIATE' in r or 'URGENT' in r],
            'confidence_level': 'HIGH' if len(results['scenario_results']) > 3 else 'MEDIUM'
        }
    
    def _extract_key_risk_indicators(self, results: Dict) -> List[Dict]:
        """Extract key risk indicators from stress test results"""
        kris = []
        
        for scenario_name, result in results['scenario_results'].items():
            kris.append({
                'indicator': f"{scenario_name} Impact",
                'value': f"{result.portfolio_impact:.1%}",
                'trend': 'increasing' if result.portfolio_impact > 0.3 else 'stable',
                'threshold': '0.2',
                'status': 'breached' if result.portfolio_impact > 0.2 else 'within_limits'
            })
        
        overall_metrics = results['overall_metrics']
        kris.append({
            'indicator': 'Overall Risk Score',
            'value': f"{overall_metrics['overall_risk_score']:.1f}",
            'trend': 'monitor',
            'threshold': '50.0',
            'status': 'breached' if overall_metrics['overall_risk_score'] > 50 else 'within_limits'
        })
        
        return kris
    
    def _generate_action_plan(self, results: Dict) -> List[Dict]:
        """Generate prioritized action plan"""
        actions = []
        
        # Categorize recommendations by priority
        for recommendation in results['recommendations']:
            if 'IMMEDIATE' in recommendation:
                priority = 'critical'
                timeframe = '24-48 hours'
            elif 'URGENT' in recommendation:
                priority = 'high'
                timeframe = '1 week'
            elif 'HEDGE' in recommendation or 'REDUCE' in recommendation:
                priority = 'medium'
                timeframe = '2 weeks'
            else:
                priority = 'low'
                timeframe = '1 month'
            
            actions.append({
                'action': recommendation,
                'priority': priority,
                'timeframe': timeframe,
                'assigned_to': 'Risk Team',
                'status': 'pending'
            })
        
        return sorted(actions, key=lambda x: {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}[x['priority']])
