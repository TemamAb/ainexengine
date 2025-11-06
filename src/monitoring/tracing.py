"""
Feature 34: Distributed Tracing
Source: OpenTelemetry, Jaeger, Prometheus
"""
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger import JaegerSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.metrics import Counter, Histogram
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from contextlib import contextmanager
import asyncio
import json

@dataclass
class TraceContext:
    trace_id: str
    span_id: str
    is_remote: bool = False

class DistributedTracing:
    def __init__(self, service_name: str = "ai-nexus-engine"):
        self.service_name = service_name
        self.setup_tracing()
        self.setup_metrics()
        
    def setup_tracing(self):
        """Setup OpenTelemetry tracing with Jaeger exporter"""
        # Create tracer provider
        resource = Resource.create({
            "service.name": self.service_name,
            "service.version": "2.0.0"
        })
        
        trace.set_tracer_provider(TracerProvider(resource=resource))
        
        # Configure Jaeger exporter
        jaeger_exporter = JaegerSpanExporter(
            agent_host_name="localhost",
            agent_port=6831,
        )
        
        # Add batch span processor
        span_processor = BatchSpanProcessor(jaeger_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        
        self.tracer = trace.get_tracer(__name__)
        
    def setup_metrics(self):
        """Setup Prometheus metrics"""
        self.prometheus_reader = PrometheusMetricReader()
        self.meter_provider = MeterProvider(metric_readers=[self.prometheus_reader])
        
        # Create metrics
        self.meter = self.meter_provider.get_meter(__name__)
        
        # Counters
        self.flash_loan_counter = self.meter.create_counter(
            "flash_loan_requests_total",
            description="Total number of flash loan requests"
        )
        
        self.arbitrage_opportunities_counter = self.meter.create_counter(
            "arbitrage_opportunities_total", 
            description="Total number of arbitrage opportunities detected"
        )
        
        self.successful_trades_counter = self.meter.create_counter(
            "successful_trades_total",
            description="Total number of successful trades"
        )
        
        # Histograms
        self.flash_loan_duration_histogram = self.meter.create_histogram(
            "flash_loan_duration_seconds",
            description="Duration of flash loan executions",
            unit="s"
        )
        
        self.arbitrage_profit_histogram = self.meter.create_histogram(
            "arbitrage_profit_usd",
            description="Profit from arbitrage trades in USD"
        )
        
        self.gas_used_histogram = self.meter.create_histogram(
            "gas_used_per_transaction",
            description="Gas used per transaction"
        )
        
    @contextmanager
    def start_span(self, name: str, attributes: Dict = None):
        """Context manager for starting a span"""
        with self.tracer.start_as_current_span(name, attributes=attributes) as span:
            start_time = time.time()
            try:
                yield span
            except Exception as e:
                # Record exception in span
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise
            finally:
                duration = time.time() - start_time
                span.set_attribute("duration", duration)
    
    async def trace_arbitrage_cycle(self, opportunity: Dict):
        """End-to-end tracing of arbitrage execution cycle"""
        attributes = {
            "opportunity.id": opportunity.get('id', 'unknown'),
            "opportunity.expected_profit": opportunity.get('expected_profit', 0),
            "opportunity.asset_pair": opportunity.get('asset_pair', 'unknown'),
            "opportunity.spread_percentage": opportunity.get('spread_percentage', 0)
        }
        
        with self.start_span("arbitrage_cycle", attributes) as span:
            # Increment opportunities counter
            self.arbitrage_opportunities_counter.add(1, attributes)
            
            # Trace detection phase
            await self._trace_detection_phase(span, opportunity)
            
            # Trace risk assessment
            risk_result = await self._trace_risk_assessment(span, opportunity)
            
            if risk_result.get('approved', False):
                # Trace execution phase
                execution_result = await self._trace_execution_phase(span, opportunity)
                
                # Record success metrics
                if execution_result.get('success', False):
                    self.successful_trades_counter.add(1)
                    profit = execution_result.get('profit', 0)
                    self.arbitrage_profit_histogram.record(profit, attributes)
                    
                    span.set_attribute("execution.success", True)
                    span.set_attribute("execution.actual_profit", profit)
                    span.set_attribute("execution.gas_used", execution_result.get('gas_used', 0))
                else:
                    span.set_attribute("execution.success", False)
                    span.set_attribute("execution.error", execution_result.get('error', 'unknown'))
            else:
                span.set_attribute("risk.assessment.approved", False)
                span.set_attribute("risk.assessment.reason", risk_result.get('reason', 'unknown'))
    
    async def _trace_detection_phase(self, parent_span, opportunity: Dict):
        """Trace opportunity detection phase"""
        with self.tracer.start_as_current_span("opportunity_detection", 
                                              context=parent_span.get_span_context()) as span:
            
            span.set_attribute("detection.method", opportunity.get('detection_method', 'cross_dex'))
            span.set_attribute("detection.confidence", opportunity.get('confidence', 0))
            span.set_attribute("detection.timestamp", opportunity.get('timestamp', time.time()))
            
            # Simulate detection logic
            await asyncio.sleep(0.001)
            
            span.set_attribute("detection.completed", True)
    
    async def _trace_risk_assessment(self, parent_span, opportunity: Dict) -> Dict:
        """Trace risk assessment phase"""
        with self.tracer.start_as_current_span("risk_assessment",
                                              context=parent_span.get_span_context()) as span:
            
            try:
                # Simulate risk assessment
                await asyncio.sleep(0.002)
                
                # Mock risk assessment result
                risk_score = min(opportunity.get('spread_percentage', 0) * 10, 1.0)
                approved = risk_score < 0.7
                
                span.set_attribute("risk.score", risk_score)
                span.set_attribute("risk.approved", approved)
                span.set_attribute("risk.threshold", 0.7)
                
                if not approved:
                    span.set_status(trace.Status(trace.StatusCode.ERROR, "Risk threshold exceeded"))
                
                return {
                    "approved": approved,
                    "risk_score": risk_score,
                    "reason": "Risk threshold exceeded" if not approved else "Approved"
                }
                
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                return {"approved": False, "error": str(e)}
    
    async def _trace_execution_phase(self, parent_span, opportunity: Dict) -> Dict:
        """Trace execution phase including flash loan"""
        with self.tracer.start_as_current_span("execution_phase",
                                              context=parent_span.get_span_context()) as span:
            
            try:
                start_time = time.time()
                
                # Trace flash loan execution
                flash_loan_result = await self._trace_flash_loan(span, opportunity)
                
                if not flash_loan_result.get('success', False):
                    span.set_status(trace.Status(trace.StatusCode.ERROR, "Flash loan failed"))
                    return {"success": False, "error": "Flash loan failed"}
                
                # Trace trade execution
                trade_result = await self._trace_trade_execution(span, opportunity, flash_loan_result)
                
                # Trace loan repayment
                repayment_result = await self._trace_loan_repayment(span, opportunity, trade_result)
                
                duration = time.time() - start_time
                
                # Record metrics
                self.flash_loan_duration_histogram.record(duration)
                self.flash_loan_counter.add(1)
                
                if repayment_result.get('success', False):
                    profit = trade_result.get('profit', 0)
                    span.set_attribute("execution.profit", profit)
                    span.set_attribute("execution.duration", duration)
                    
                    return {
                        "success": True,
                        "profit": profit,
                        "gas_used": flash_loan_result.get('gas_used', 0) + trade_result.get('gas_used', 0),
                        "duration": duration
                    }
                else:
                    span.set_status(trace.Status(trace.StatusCode.ERROR, "Loan repayment failed"))
                    return {"success": False, "error": "Loan repayment failed"}
                    
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                return {"success": False, "error": str(e)}
    
    async def _trace_flash_loan(self, parent_span, opportunity: Dict) -> Dict:
        """Trace flash loan execution"""
        with self.tracer.start_as_current_span("flash_loan_execution",
                                              context=parent_span.get_span_context()) as span:
            
            try:
                span.set_attribute("flash_loan.amount", opportunity.get('amount', 0))
                span.set_attribute("flash_loan.provider", opportunity.get('provider', 'unknown'))
                span.set_attribute("flash_loan.asset", opportunity.get('asset', 'unknown'))
                
                # Simulate flash loan execution
                await asyncio.sleep(0.005)
                
                # Mock successful flash loan
                return {
                    "success": True,
                    "loan_id": f"loan_{int(time.time())}",
                    "gas_used": 150000,
                    "fee": opportunity.get('amount', 0) * 0.0009
                }
                
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                return {"success": False, "error": str(e)}
    
    async def _trace_trade_execution(self, parent_span, opportunity: Dict, flash_loan_result: Dict) -> Dict:
        """Trace trade execution"""
        with self.tracer.start_as_current_span("trade_execution",
                                              context=parent_span.get_span_context()) as span:
            
            try:
                span.set_attribute("trade.type", "arbitrage")
                span.set_attribute("trade.dex", opportunity.get('dex', 'unknown'))
                span.set_attribute("trade.direction", opportunity.get('direction', 'unknown'))
                
                # Simulate trade execution
                await asyncio.sleep(0.003)
                
                # Mock trade result
                profit = opportunity.get('expected_profit', 0) * 0.8  # 80% of expected
                
                span.set_attribute("trade.profit", profit)
                span.set_attribute("trade.slippage", 0.001)
                
                return {
                    "success": True,
                    "profit": profit,
                    "gas_used": 120000,
                    "slippage": 0.001
                }
                
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                return {"success": False, "error": str(e)}
    
    async def _trace_loan_repayment(self, parent_span, opportunity: Dict, trade_result: Dict) -> Dict:
        """Trace loan repayment"""
        with self.tracer.start_as_current_span("loan_repayment",
                                              context=parent_span.get_span_context()) as span:
            
            try:
                span.set_attribute("repayment.amount", opportunity.get('amount', 0))
                
                # Simulate repayment
                await asyncio.sleep(0.002)
                
                # Mock successful repayment
                return {
                    "success": True,
                    "gas_used": 80000,
                    "repayment_time": time.time()
                }
                
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                return {"success": False, "error": str(e)}
    
    def trace_cross_chain_arbitrage(self, opportunity: Dict):
        """Trace cross-chain arbitrage operations"""
        attributes = {
            "cross_chain.source_chain": opportunity.get('source_chain', 'unknown'),
            "cross_chain.target_chain": opportunity.get('target_chain', 'unknown'),
            "cross_chain.bridge": opportunity.get('bridge', 'unknown'),
            "cross_chain.asset": opportunity.get('asset', 'unknown')
        }
        
        with self.start_span("cross_chain_arbitrage", attributes) as span:
            # This would include bridge operations, cross-chain transactions, etc.
            span.set_attribute("arbitrage.type", "cross_chain")
            span.set_attribute("estimated_profit", opportunity.get('estimated_profit', 0))
    
    def trace_liquidity_provision(self, lp_operation: Dict):
        """Trace liquidity provision operations"""
        attributes = {
            "liquidity.pool": lp_operation.get('pool_address', 'unknown'),
            "liquidity.asset_a": lp_operation.get('asset_a', 'unknown'),
            "liquidity.asset_b": lp_operation.get('asset_b', 'unknown'),
            "liquidity.amount": lp_operation.get('amount', 0)
        }
        
        with self.start_span("liquidity_provision", attributes) as span:
            span.set_attribute("lp.action", lp_operation.get('action', 'add_liquidity'))
            span.set_attribute("lp.fee_tier", lp_operation.get('fee_tier', 'unknown'))
    
    def trace_ai_optimization(self, optimization_data: Dict):
        """Trace AI optimization cycles"""
        attributes = {
            "ai.model": optimization_data.get('model', 'unknown'),
            "ai.optimization_type": optimization_data.get('type', 'strategy_optimization'),
            "ai.training_cycles": optimization_data.get('training_cycles', 0)
        }
        
        with self.start_span("ai_optimization", attributes) as span:
            span.set_attribute("ai.performance_improvement", optimization_data.get('improvement', 0))
            span.set_attribute("ai.training_duration", optimization_data.get('duration', 0))
    
    def create_trace_context(self) -> TraceContext:
        """Create trace context for distributed tracing"""
        current_span = trace.get_current_span()
        span_context = current_span.get_span_context()
        
        return TraceContext(
            trace_id=format(span_context.trace_id, '032x'),
            span_id=format(span_context.span_id, '016x')
        )
    
    def extract_trace_context(self, headers: Dict) -> Optional[TraceContext]:
        """Extract trace context from incoming headers"""
        trace_id = headers.get('x-trace-id')
        span_id = headers.get('x-span-id')
        
        if trace_id and span_id:
            return TraceContext(
                trace_id=trace_id,
                span_id=span_id,
                is_remote=True
            )
        return None
    
    async def get_trace_metrics(self) -> Dict:
        """Get current tracing and metrics data"""
        # This would query Prometheus or Jaeger for actual metrics
        # For now, return mock metrics
        
        return {
            "tracing": {
                "active_traces": 45,
                "traces_per_second": 12.5,
                "average_trace_duration_ms": 245.7,
                "error_rate": 0.023
            },
            "metrics": {
                "flash_loans_total": 1250,
                "arbitrage_opportunities_total": 8900,
                "successful_trades_total": 780,
                "average_profit_per_trade": 850.50,
                "average_gas_used": 185000
            },
            "service_health": {
                "tracing_system": "healthy",
                "metrics_collection": "healthy", 
                "exporters": ["jaeger", "prometheus"]
            }
        }
    
    def record_custom_metric(self, metric_name: str, value: float, attributes: Dict = None):
        """Record custom business metric"""
        # Create custom counter if it doesn't exist
        if not hasattr(self, f'_custom_{metric_name}'):
            setattr(self, f'_custom_{metric_name}', 
                   self.meter.create_counter(metric_name, description=f"Custom metric: {metric_name}"))
        
        counter = getattr(self, f'_custom_{metric_name}')
        counter.add(value, attributes or {})
    
    async def export_traces(self):
        """Force export of all pending traces"""
        # This would flush all pending spans to the exporter
        tracer_provider = trace.get_tracer_provider()
        if hasattr(tracer_provider, 'force_flush'):
            await tracer_provider.force_flush()
    
    def shutdown(self):
        """Shutdown tracing system"""
        tracer_provider = trace.get_tracer_provider()
        if hasattr(tracer_provider, 'shutdown'):
            tracer_provider.shutdown()
        
        if hasattr(self.meter_provider, 'shutdown'):
            self.meter_provider.shutdown()

# Global tracing instance
global_tracer = None

def setup_global_tracing(service_name: str = "ai-nexus-engine") -> DistributedTracing:
    """Setup global tracing instance"""
    global global_tracer
    if global_tracer is None:
        global_tracer = DistributedTracing(service_name)
    return global_tracer

def get_global_tracer() -> DistributedTracing:
    """Get global tracing instance"""
    global global_tracer
    if global_tracer is None:
        raise RuntimeError("Global tracer not initialized. Call setup_global_tracing first.")
    return global_tracer

# Example usage decorator
def trace_function(span_name: str):
    """Decorator to trace function execution"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            tracer = get_global_tracer()
            function_name = func.__name__
            attributes = {
                "function.name": function_name,
                "function.module": func.__module__
            }
            
            with tracer.start_span(f"{span_name}.{function_name}", attributes) as span:
                try:
                    result = await func(*args, **kwargs)
                    span.set_attribute("function.success", True)
                    return result
                except Exception as e:
                    span.set_attribute("function.success", False)
                    span.record_exception(e)
                    raise
        
        def sync_wrapper(*args, **kwargs):
            tracer = get_global_tracer()
            function_name = func.__name__
            attributes = {
                "function.name": function_name,
                "function.module": func.__module__
            }
            
            with tracer.start_span(f"{span_name}.{function_name}", attributes) as span:
                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("function.success", True)
                    return result
                except Exception as e:
                    span.set_attribute("function.success", False)
                    span.record_exception(e)
                    raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
