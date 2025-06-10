#!/usr/bin/env python3
"""
Autonomous Test Orchestrator for Claude Code Integration
Works with existing two-stage Docker setup
"""

import json
import time
import subprocess
import logging
import sys
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass, asdict

@dataclass
class TestIteration:
    iteration: int
    instance: str
    timestamp: str
    tests_run: int
    tests_passed: int
    tests_failed: int
    confidence_score: float
    critical_failures: List[str]
    ready_for_promotion: bool
    next_action: str

class AutonomousOrchestrator:
    """
    Orchestrates autonomous testing until complete confidence
    Integrates with existing two-stage-manager.sh
    """
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.setup_logging()
        self.confidence_threshold = 0.95
        self.max_iterations = 10  # Reduced from 20 for practicality
        self.results_history = []
        
    def setup_logging(self):
        """Setup comprehensive logging for Claude Code analysis"""
        log_dir = self.project_root / "logs" / "autonomous"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "autonomous_orchestrator.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def run_until_confident(self, instance: str = "dev") -> Dict:
        """
        Main autonomous loop - runs until completely confident
        """
        self.logger.info(f"🚀 Starting autonomous testing on {instance} until completely confident")
        
        for iteration in range(1, self.max_iterations + 1):
            self.logger.info(f"\n=== ITERATION {iteration} ===")
            
            # Run comprehensive test suite
            test_result = self._run_test_iteration(instance, iteration)
            self.results_history.append(test_result)
            
            # Log results for Claude Code analysis
            self._log_iteration_result(test_result)
            
            # Check confidence level
            if test_result.ready_for_promotion:
                self.logger.info(f"✅ CONFIDENT: {instance} ready after {iteration} iterations")
                return self._generate_success_report(test_result, iteration)
            
            # Brief pause between iterations
            time.sleep(3)
        
        # Max iterations reached without confidence
        return self._generate_failure_report()
    
    def _run_test_iteration(self, instance: str, iteration: int) -> TestIteration:
        """Run single test iteration with comprehensive analysis"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Run tests using two-stage test runner
        test_cmd = f"./scripts/two-stage-test-runner.sh {instance}"
        test_result = self._execute_command(test_cmd)
        
        # No need for separate docker test - it's all integrated
        docker_result = test_result
        
        # Calculate confidence metrics
        confidence_data = self._calculate_confidence_metrics(
            test_result, docker_result, instance
        )
        
        return TestIteration(
            iteration=iteration,
            instance=instance,
            timestamp=timestamp,
            tests_run=confidence_data['tests_run'],
            tests_passed=confidence_data['tests_passed'],
            tests_failed=confidence_data['tests_failed'],
            confidence_score=confidence_data['confidence_score'],
            critical_failures=confidence_data['critical_failures'],
            ready_for_promotion=confidence_data['confidence_score'] >= self.confidence_threshold,
            next_action=confidence_data['next_action']
        )
    
    def _execute_command(self, cmd: str) -> Dict:
        """Execute command and return structured result"""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=60
            )
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'stdout': '',
                'stderr': 'Command timed out',
                'returncode': -1
            }
    
    def _calculate_confidence_metrics(self, test_result: Dict, docker_result: Dict, 
                                    instance: str) -> Dict:
        """Calculate comprehensive confidence metrics"""
        
        # Analyze test results
        tests_passed = 0
        tests_failed = 0
        critical_failures = []
        
        # Parse test output for pass/fail counts
        for result in [test_result, docker_result]:
            # Always parse stdout for results, regardless of exit code
            output_lines = result['stdout'].split('\n')
            for line in output_lines:
                if '✅' in line or 'PASSED' in line:
                    tests_passed += 1
                elif '❌' in line or 'FAILED' in line:
                    tests_failed += 1
                    if any(critical in line.lower() for critical in 
                          ['database', 'security', 'critical', 'authentication']):
                        critical_failures.append(line.strip())
            
            # Also check for summary lines
            for line in output_lines:
                if 'Tests Passed:' in line:
                    try:
                        # Extract number from "Tests Passed: 11"
                        passed_count = int(line.split(':')[1].strip().split()[0])
                        tests_passed = max(tests_passed, passed_count)
                    except:
                        pass
                elif 'Tests Failed:' in line:
                    try:
                        failed_count = int(line.split(':')[1].strip().split()[0])
                        tests_failed = max(tests_failed, failed_count)
                    except:
                        pass
                elif 'Confidence Score:' in line:
                    try:
                        confidence = float(line.split(':')[1].strip())
                    except:
                        pass
        
        total_tests = tests_passed + tests_failed
        
        # Calculate confidence score
        if total_tests > 0:
            confidence = tests_passed / total_tests
        else:
            confidence = 0.0
        
        # Determine next action
        if confidence >= self.confidence_threshold:
            next_action = "PROMOTE" if instance == "dev" else "DEPLOY"
        elif critical_failures:
            next_action = "FIX_CRITICAL"
        elif confidence > 0.7:
            next_action = "CONTINUE_TESTING"
        else:
            next_action = "INVESTIGATE_FAILURES"
        
        return {
            'tests_run': total_tests,
            'tests_passed': tests_passed,
            'tests_failed': tests_failed,
            'confidence_score': confidence,
            'critical_failures': critical_failures,
            'next_action': next_action
        }
    
    def _log_iteration_result(self, result: TestIteration):
        """Log iteration result in JSON format for Claude Code analysis"""
        log_file = self.project_root / "logs" / "autonomous" / "iteration_results.jsonl"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(asdict(result)) + '\n')
    
    def _generate_success_report(self, final_result: TestIteration, iterations: int) -> Dict:
        """Generate success report for Claude Code"""
        return {
            'status': 'SUCCESS',
            'instance': final_result.instance,
            'iterations_required': iterations,
            'final_confidence_score': final_result.confidence_score,
            'tests_summary': {
                'total': final_result.tests_run,
                'passed': final_result.tests_passed,
                'failed': final_result.tests_failed
            },
            'ready_for_promotion': True,
            'next_action': final_result.next_action,
            'timestamp': final_result.timestamp
        }
    
    def _generate_failure_report(self) -> Dict:
        """Generate failure report when max iterations reached"""
        return {
            'status': 'FAILED',
            'reason': 'Maximum iterations reached without achieving confidence threshold',
            'iterations_attempted': len(self.results_history),
            'final_confidence_score': self.results_history[-1].confidence_score if self.results_history else 0,
            'persistent_failures': [r.critical_failures for r in self.results_history[-3:]],
            'requires_human_intervention': True,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

def main():
    """Main entry point for Claude Code autonomous testing"""
    if len(sys.argv) < 2:
        print("Usage: python autonomous-orchestrator.py <instance>")
        print("Instance: dev, staging")
        sys.exit(1)
    
    instance = sys.argv[1]
    orchestrator = AutonomousOrchestrator()
    
    print(f"🚀 Starting autonomous testing on {instance} until completely confident...")
    result = orchestrator.run_until_confident(instance)
    
    print("\n" + "="*80)
    print("AUTONOMOUS TESTING COMPLETE")
    print("="*80)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()