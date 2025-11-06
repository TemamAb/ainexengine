"""
Feature 32: Security Audit Pipeline
Source: Slither, MythX, Security Tooling
"""
import subprocess
import asyncio
import json
import tempfile
import os
from typing import Dict, List, Optional
from pathlib import Path
import requests
import time
from dataclasses import dataclass
from enum import Enum

class AuditSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityVulnerability:
    severity: AuditSeverity
    title: str
    description: str
    location: str
    recommendation: str
    tool: str

@dataclass
class AuditResult:
    contract_name: str
    vulnerabilities: List[SecurityVulnerability]
    security_score: float
    passed: bool
    audit_duration: float

class SecurityAuditPipeline:
    def __init__(self):
        self.audit_tools = ['slither', 'mythril', 'oyente', 'security']
        self.severity_weights = {
            AuditSeverity.CRITICAL: 10.0,
            AuditSeverity.HIGH: 5.0,
            AuditSeverity.MEDIUM: 2.0,
            AuditSeverity.LOW: 0.5
        }
        self.audit_history = []
        
    async def audit_smart_contracts(self, contract_path: str, contract_name: str) -> AuditResult:
        """Comprehensive security audit for smart contracts"""
        start_time = time.time()
        
        try:
            # Run all audit tools in parallel
            audit_tasks = [
                self._run_slither_analysis(contract_path),
                self._run_mythril_analysis(contract_path),
                self._run_oyente_analysis(contract_path),
                self._run_security_analysis(contract_path)
            ]
            
            tool_results = await asyncio.gather(*audit_tasks, return_exceptions=True)
            
            # Aggregate vulnerabilities from all tools
            all_vulnerabilities = []
            for result in tool_results:
                if isinstance(result, list):
                    all_vulnerabilities.extend(result)
            
            # Calculate security score
            security_score = self._calculate_security_score(all_vulnerabilities)
            
            # Determine if audit passed
            passed = self._determine_audit_pass(all_vulnerabilities, security_score)
            
            audit_result = AuditResult(
                contract_name=contract_name,
                vulnerabilities=all_vulnerabilities,
                security_score=security_score,
                passed=passed,
                audit_duration=time.time() - start_time
            )
            
            # Store audit result
            self.audit_history.append(audit_result)
            
            return audit_result
            
        except Exception as e:
            # Return failed audit result
            return AuditResult(
                contract_name=contract_name,
                vulnerabilities=[],
                security_score=0.0,
                passed=False,
                audit_duration=time.time() - start_time
            )
    
    async def _run_slither_analysis(self, contract_path: str) -> List[SecurityVulnerability]:
        """Run Slither static analysis"""
        vulnerabilities = []
        
        try:
            # Run slither command
            cmd = ['slither', contract_path, '--json', '-']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                slither_output = json.loads(result.stdout)
                
                # Parse Slither results
                for detector in slither_output.get('results', {}).get('detectors', []):
                    severity = self._map_slither_severity(detector.get('impact', 'Low'))
                    
                    vulnerability = SecurityVulnerability(
                        severity=severity,
                        title=detector.get('check', 'Unknown'),
                        description=detector.get('description', 'No description'),
                        location=detector.get('elements', [{}])[0].get('name', 'Unknown'),
                        recommendation=detector.get('exploit_scenario', 'No recommendation'),
                        tool='slither'
                    )
                    vulnerabilities.append(vulnerability)
            
        except subprocess.TimeoutExpired:
            vulnerabilities.append(self._create_timeout_vulnerability('slither'))
        except Exception as e:
            vulnerabilities.append(self._create_error_vulnerability('slither', str(e)))
        
        return vulnerabilities
    
    async def _run_mythril_analysis(self, contract_path: str) -> List[SecurityVulnerability]:
        """Run Mythril security analysis"""
        vulnerabilities = []
        
        try:
            # Run mythril command
            cmd = ['myth', 'analyze', contract_path, '--max-depth', '12', '-o', 'json']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                mythril_output = json.loads(result.stdout)
                
                # Parse Mythril results
                for issue in mythril_output.get('issues', []):
                    severity = self._map_mythril_severity(issue.get('severity', 'Low'))
                    
                    vulnerability = SecurityVulnerability(
                        severity=severity,
                        title=issue.get('title', 'Unknown'),
                        description=issue.get('description', 'No description'),
                        location=issue.get('address', 'Unknown'),
                        recommendation=issue.get('remediation', 'No recommendation'),
                        tool='mythril'
                    )
                    vulnerabilities.append(vulnerability)
            
        except subprocess.TimeoutExpired:
            vulnerabilities.append(self._create_timeout_vulnerability('mythril'))
        except Exception as e:
            vulnerabilities.append(self._create_error_vulnerability('mythril', str(e)))
        
        return vulnerabilities
    
    async def _run_oyente_analysis(self, contract_path: str) -> List[SecurityVulnerability]:
        """Run Oyente symbolic execution analysis"""
        vulnerabilities = []
        
        try:
            # Run oyente command
            cmd = ['oyente', '-s', contract_path, '-j']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                oyente_output = json.loads(result.stdout)
                
                # Parse Oyente results
                for vulnerability_type, detected in oyente_output.get('vulnerabilities', {}).items():
                    if detected:
                        severity = self._map_oyente_severity(vulnerability_type)
                        
                        vulnerability = SecurityVulnerability(
                            severity=severity,
                            title=vulnerability_type.replace('_', ' ').title(),
                            description=f"Detected {vulnerability_type} vulnerability",
                            location=contract_path,
                            recommendation=f"Fix {vulnerability_type} vulnerability",
                            tool='oyente'
                        )
                        vulnerabilities.append(vulnerability)
            
        except subprocess.TimeoutExpired:
            vulnerabilities.append(self._create_timeout_vulnerability('oyente'))
        except Exception as e:
            vulnerabilities.append(self._create_error_vulnerability('oyente', str(e)))
        
        return vulnerabilities
    
    async def _run_security_analysis(self, contract_path: str) -> List[SecurityVulnerability]:
        """Run additional security checks"""
        vulnerabilities = []
        
        try:
            # Custom security checks
            with open(contract_path, 'r') as f:
                contract_code = f.read()
            
            # Check for common vulnerabilities
            checks = [
                self._check_reentrancy(contract_code),
                self._check_integer_overflow(contract_code),
                self._check_access_control(contract_code),
                self._check_gas_limits(contract_code)
            ]
            
            for check_result in checks:
                if check_result:
                    vulnerabilities.append(check_result)
            
        except Exception as e:
            vulnerabilities.append(self._create_error_vulnerability('security', str(e)))
        
        return vulnerabilities
    
    def _check_reentrancy(self, code: str) -> Optional[SecurityVulnerability]:
        """Check for reentrancy vulnerabilities"""
        if 'call.value' in code and not ('require(' in code and 'success' in code):
            return SecurityVulnerability(
                severity=AuditSeverity.HIGH,
                title="Potential Reentrancy",
                description="Contract uses call.value without proper checks",
                location="Multiple locations",
                recommendation="Use Checks-Effects-Interactions pattern",
                tool='security'
            )
        return None
    
    def _check_integer_overflow(self, code: str) -> Optional[SecurityVulnerability]:
        """Check for integer overflow vulnerabilities"""
        if any(op in code for op in ['++', '--', '+=']) and 'SafeMath' not in code:
            return SecurityVulnerability(
                severity=AuditSeverity.MEDIUM,
                title="Potential Integer Overflow",
                description="Arithmetic operations without SafeMath",
                location="Multiple locations", 
                recommendation="Use SafeMath library for arithmetic",
                tool='security'
            )
        return None
    
    def _check_access_control(self, code: str) -> Optional[SecurityVulnerability]:
        """Check for access control issues"""
        if 'onlyOwner' not in code and 'public' in code:
            return SecurityVulnerability(
                severity=AuditSeverity.MEDIUM,
                title="Missing Access Control",
                description="Public functions without access restrictions",
                location="Multiple locations",
                recommendation="Add onlyOwner or similar modifiers",
                tool='security'
            )
        return None
    
    def _check_gas_limits(self, code: str) -> Optional[SecurityVulnerability]:
        """Check for gas limit issues"""
        if 'for(' in code or 'while(' in code:
            return SecurityVulnerability(
                severity=AuditSeverity.LOW,
                title="Potential Gas Limit Issues",
                description="Loops that may exceed gas limits",
                location="Multiple locations",
                recommendation="Limit loop iterations or use pagination",
                tool='security'
            )
        return None
    
    def _map_slither_severity(self, impact: str) -> AuditSeverity:
        """Map Slither impact to standard severity"""
        mapping = {
            'High': AuditSeverity.HIGH,
            'Medium': AuditSeverity.MEDIUM,
            'Low': AuditSeverity.LOW,
            'Informational': AuditSeverity.LOW
        }
        return mapping.get(impact, AuditSeverity.LOW)
    
    def _map_mythril_severity(self, severity: str) -> AuditSeverity:
        """Map Mythril severity to standard severity"""
        mapping = {
            'High': AuditSeverity.HIGH,
            'Medium': AuditSeverity.MEDIUM, 
            'Low': AuditSeverity.LOW
        }
        return mapping.get(severity, AuditSeverity.LOW)
    
    def _map_oyente_severity(self, vuln_type: str) -> AuditSeverity:
        """Map Oyente vulnerability type to severity"""
        critical_vulns = ['reentrancy', 'integer_overflow', 'integer_underflow']
        high_vulns = ['timestamp_dependency', 'transaction_order_dependency']
        
        if vuln_type in critical_vulns:
            return AuditSeverity.CRITICAL
        elif vuln_type in high_vulns:
            return AuditSeverity.HIGH
        else:
            return AuditSeverity.MEDIUM
    
    def _create_timeout_vulnerability(self, tool: str) -> SecurityVulnerability:
        """Create vulnerability for tool timeout"""
        return SecurityVulnerability(
            severity=AuditSeverity.MEDIUM,
            title=f"{tool} Analysis Timeout",
            description=f"{tool} analysis took too long and was terminated",
            location="Tool execution",
            recommendation="Increase timeout or optimize contract",
            tool=tool
        )
    
    def _create_error_vulnerability(self, tool: str, error: str) -> SecurityVulnerability:
        """Create vulnerability for tool error"""
        return SecurityVulnerability(
            severity=AuditSeverity.MEDIUM,
            title=f"{tool} Analysis Error",
            description=f"{tool} failed with error: {error}",
            location="Tool execution", 
            recommendation="Check tool configuration and contract compatibility",
            tool=tool
        )
    
    def _calculate_security_score(self, vulnerabilities: List[SecurityVulnerability]) -> float:
        """Calculate overall security score (0-100)"""
        if not vulnerabilities:
            return 100.0
        
        total_weight = 0.0
        for vuln in vulnerabilities:
            total_weight += self.severity_weights.get(vuln.severity, 0.0)
        
        # Convert to score (higher weight = lower score)
        max_possible_weight = len(vulnerabilities) * self.severity_weights[AuditSeverity.CRITICAL]
        if max_possible_weight == 0:
            return 100.0
        
        score = max(0.0, 100.0 - (total_weight / max_possible_weight * 100.0))
        return round(score, 2)
    
    def _determine_audit_pass(self, vulnerabilities: List[SecurityVulnerability], score: float) -> bool:
        """Determine if audit passes based on vulnerabilities and score"""
        # Fail if any critical vulnerabilities
        if any(v.severity == AuditSeverity.CRITICAL for v in vulnerabilities):
            return False
        
        # Fail if score below threshold
        if score < 80.0:
            return False
        
        # Fail if too many high severity vulnerabilities
        high_severity_count = sum(1 for v in vulnerabilities if v.severity == AuditSeverity.HIGH)
        if high_severity_count > 3:
            return False
        
        return True
    
    def generate_audit_report(self, audit_result: AuditResult) -> Dict:
        """Generate comprehensive audit report"""
        report = {
            "contract_name": audit_result.contract_name,
            "audit_date": time.time(),
            "security_score": audit_result.security_score,
            "audit_passed": audit_result.passed,
            "audit_duration_seconds": audit_result.audit_duration,
            "vulnerability_summary": {
                "total": len(audit_result.vulnerabilities),
                "critical": sum(1 for v in audit_result.vulnerabilities if v.severity == AuditSeverity.CRITICAL),
                "high": sum(1 for v in audit_result.vulnerabilities if v.severity == AuditSeverity.HIGH),
                "medium": sum(1 for v in audit_result.vulnerabilities if v.severity == AuditSeverity.MEDIUM),
                "low": sum(1 for v in audit_result.vulnerabilities if v.severity == AuditSeverity.LOW)
            },
            "tool_coverage": self.audit_tools,
            "detailed_findings": [
                {
                    "severity": vuln.severity.value,
                    "title": vuln.title,
                    "description": vuln.description,
                    "location": vuln.location,
                    "recommendation": vuln.recommendation,
                    "tool": vuln.tool
                }
                for vuln in audit_result.vulnerabilities
            ],
            "recommendations": self._generate_recommendations(audit_result.vulnerabilities),
            "next_steps": self._generate_next_steps(audit_result)
        }
        
        return report
    
    def _generate_recommendations(self, vulnerabilities: List[SecurityVulnerability]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        critical_vulns = [v for v in vulnerabilities if v.severity == AuditSeverity.CRITICAL]
        high_vulns = [v for v in vulnerabilities if v.severity == AuditSeverity.HIGH]
        
        if critical_vulns:
            recommendations.append("IMMEDIATE: Fix all critical vulnerabilities before deployment")
        
        if high_vulns:
            recommendations.append("URGENT: Address high severity vulnerabilities")
        
        if any('reentrancy' in v.title.lower() for v in vulnerabilities):
            recommendations.append("Implement Checks-Effects-Interactions pattern")
        
        if any('overflow' in v.title.lower() for v in vulnerabilities):
            recommendations.append("Use SafeMath for all arithmetic operations")
        
        if any('access control' in v.title.lower() for v in vulnerabilities):
            recommendations.append("Review and strengthen access control mechanisms")
        
        if len(recommendations) == 0:
            recommendations.append("Continue with standard security best practices")
        
        return recommendations
    
    def _generate_next_steps(self, audit_result: AuditResult) -> List[str]:
        """Generate next steps based on audit result"""
        if audit_result.passed:
            return [
                "Proceed with deployment",
                "Continue monitoring with runtime analysis",
                "Schedule follow-up audit after major changes"
            ]
        else:
            return [
                "Address all critical and high severity vulnerabilities",
                "Re-run security audit after fixes",
                "Consider third-party audit for production deployment",
                "Implement additional security monitoring"
            ]
    
    async def continuous_audit_monitoring(self, contract_path: str, interval_hours: int = 24):
        """Continuous audit monitoring for deployed contracts"""
        while True:
            try:
                audit_result = await self.audit_smart_contracts(contract_path, "Continuous Audit")
                report = self.generate_audit_report(audit_result)
                
                # Alert if security score drops
                if audit_result.security_score < 70:
                    await self._trigger_security_alert(report)
                
                # Store audit result
                self.audit_history.append(audit_result)
                
                # Wait for next audit cycle
                await asyncio.sleep(interval_hours * 3600)
                
            except Exception as e:
                print(f"Continuous audit error: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour on error
    
    async def _trigger_security_alert(self, report: Dict):
        """Trigger security alert for critical findings"""
        # In production, this would send alerts via email, Slack, etc.
        print(f"íº¨ SECURITY ALERT: Contract security score dropped to {report['security_score']}")
        print(f"Critical vulnerabilities: {report['vulnerability_summary']['critical']}")
        print(f"High vulnerabilities: {report['vulnerability_summary']['high']}")
