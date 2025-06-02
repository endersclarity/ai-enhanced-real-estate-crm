"""
Performance Management Module
Consolidated performance testing and optimization
"""

import time
import requests
import statistics
import concurrent.futures
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from .config import get_config
from .logger import setup_logger


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    response_times: List[float]
    success_rate: float
    error_count: int
    throughput_rps: float
    concurrent_users: int
    timestamp: str
    
    @property
    def avg_response_time(self) -> float:
        return statistics.mean(self.response_times) if self.response_times else 0
    
    @property
    def max_response_time(self) -> float:
        return max(self.response_times) if self.response_times else 0
    
    @property
    def min_response_time(self) -> float:
        return min(self.response_times) if self.response_times else 0


class PerformanceManager:
    """Unified performance testing and optimization manager"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = setup_logger("performance")
        self.base_url = self.config.production_url
        
    def health_check(self) -> Dict[str, Any]:
        """Perform application health check"""
        self.logger.test("Running health check...")
        
        endpoints = [
            ('/', 'Homepage'),
            ('/static/style.css', 'Static CSS'),
            ('/static/script.js', 'Static JS'),
            ('/health', 'Health Check'),
            ('/metrics', 'Metrics')
        ]
        
        results = {
            'total_endpoints': len(endpoints),
            'working_endpoints': 0,
            'failing_endpoints': 0,
            'endpoints': {}
        }
        
        for endpoint, description in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                is_working = 200 <= response.status_code < 400
                if is_working:
                    results['working_endpoints'] += 1
                    self.logger.success(f"{description}: {response.status_code} ({response_time:.1f}ms)")
                else:
                    results['failing_endpoints'] += 1
                    self.logger.warning(f"{description}: {response.status_code} ({response_time:.1f}ms)")
                
                results['endpoints'][endpoint] = {
                    'description': description,
                    'status_code': response.status_code,
                    'response_time_ms': round(response_time, 2),
                    'working': is_working
                }
                
            except Exception as e:
                results['failing_endpoints'] += 1
                self.logger.error(f"{description}: {str(e)}")
                results['endpoints'][endpoint] = {
                    'description': description,
                    'error': str(e),
                    'working': False
                }
        
        # Overall health assessment
        health_percentage = (results['working_endpoints'] / results['total_endpoints']) * 100
        results['health_percentage'] = round(health_percentage, 1)
        
        if health_percentage >= 80:
            results['status'] = 'HEALTHY'
            self.logger.success(f"Health check passed: {health_percentage}%")
        elif health_percentage >= 60:
            results['status'] = 'DEGRADED'
            self.logger.warning(f"Health check degraded: {health_percentage}%")
        else:
            results['status'] = 'UNHEALTHY'
            self.logger.error(f"Health check failed: {health_percentage}%")
        
        return results
    
    def load_test(self, concurrent_users: int = 10, duration_seconds: int = 30) -> PerformanceMetrics:
        """Perform load testing with specified parameters"""
        self.logger.test(f"Starting load test: {concurrent_users} users for {duration_seconds}s")
        
        def make_request() -> Dict[str, Any]:
            """Make a single request and return timing data"""
            start_time = time.time()
            try:
                response = requests.get(self.base_url, timeout=10)
                end_time = time.time()
                return {
                    'success': response.status_code == 200,
                    'response_time': end_time - start_time,
                    'status_code': response.status_code
                }
            except Exception as e:
                return {
                    'success': False,
                    'response_time': time.time() - start_time,
                    'error': str(e)
                }
        
        # Run load test
        start_test_time = time.time()
        all_results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            while time.time() - start_test_time < duration_seconds:
                # Submit batch of requests
                futures = [executor.submit(make_request) for _ in range(concurrent_users)]
                batch_results = [future.result() for future in concurrent.futures.as_completed(futures)]
                all_results.extend(batch_results)
                
                # Small delay between batches
                time.sleep(0.1)
        
        # Analyze results
        successful_results = [r for r in all_results if r.get('success')]
        response_times = [r['response_time'] for r in successful_results]
        
        metrics = PerformanceMetrics(
            response_times=response_times,
            success_rate=(len(successful_results) / len(all_results)) * 100 if all_results else 0,
            error_count=len(all_results) - len(successful_results),
            throughput_rps=len(all_results) / duration_seconds,
            concurrent_users=concurrent_users,
            timestamp=datetime.now().isoformat()
        )
        
        # Log results
        self.logger.success(f"Load test completed:")
        self.logger.info(f"  Total Requests: {len(all_results)}")
        self.logger.info(f"  Success Rate: {metrics.success_rate:.1f}%")
        self.logger.info(f"  Average Response Time: {metrics.avg_response_time:.3f}s")
        self.logger.info(f"  Throughput: {metrics.throughput_rps:.1f} RPS")
        
        return metrics
    
    def benchmark_scenarios(self) -> Dict[str, PerformanceMetrics]:
        """Run predefined benchmark scenarios"""
        self.logger.test("Running benchmark scenarios...")
        
        scenarios = {
            'light_load': {
                'users': self.config.performance.light_load_users,
                'duration': 30
            },
            'medium_load': {
                'users': self.config.performance.medium_load_users,
                'duration': 45
            },
            'heavy_load': {
                'users': self.config.performance.heavy_load_users,
                'duration': 20
            }
        }
        
        results = {}
        for scenario_name, params in scenarios.items():
            self.logger.info(f"Running {scenario_name} scenario...")
            metrics = self.load_test(
                concurrent_users=params['users'],
                duration_seconds=params['duration']
            )
            results[scenario_name] = metrics
        
        return results
    
    def validate_performance_targets(self, metrics: PerformanceMetrics) -> Dict[str, bool]:
        """Validate performance against targets"""
        targets = self.config.performance
        
        validation = {
            'response_time_target': metrics.avg_response_time <= (targets.response_time_target_ms / 1000),
            'throughput_target': metrics.throughput_rps >= targets.throughput_target_rps,
            'success_rate_target': metrics.success_rate >= 95.0
        }
        
        # Log validation results
        for target, passed in validation.items():
            if passed:
                self.logger.success(f"✅ {target}: PASSED")
            else:
                self.logger.warning(f"❌ {target}: FAILED")
        
        return validation
    
    def generate_optimization_recommendations(self, metrics: PerformanceMetrics) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        # Response time analysis
        if metrics.avg_response_time > 1.0:
            recommendations.extend([
                "Implement response caching for static content",
                "Optimize database queries with proper indexing",
                "Consider CDN for static asset delivery"
            ])
        
        # Throughput analysis
        if metrics.throughput_rps < self.config.performance.throughput_target_rps:
            recommendations.extend([
                "Increase gunicorn worker processes",
                "Implement connection pooling",
                "Consider horizontal scaling"
            ])
        
        # Success rate analysis
        if metrics.success_rate < 95.0:
            recommendations.extend([
                "Investigate error causes",
                "Implement circuit breaker patterns",
                "Add retry logic for transient failures"
            ])
        
        # Concurrent user analysis
        if metrics.concurrent_users > 25 and metrics.avg_response_time > 2.0:
            recommendations.extend([
                "Implement load balancing",
                "Optimize application for concurrency",
                "Consider async processing for heavy operations"
            ])
        
        return recommendations
    
    def comprehensive_performance_test(self) -> Dict[str, Any]:
        """Run comprehensive performance testing suite"""
        self.logger.section("COMPREHENSIVE PERFORMANCE TESTING", level=1)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'health_check': None,
            'load_test_scenarios': None,
            'performance_validation': None,
            'recommendations': None
        }
        
        # 1. Health Check
        self.logger.info("Step 1: Application Health Check")
        results['health_check'] = self.health_check()
        
        # 2. Load Testing Scenarios
        self.logger.info("Step 2: Load Testing Scenarios")
        results['load_test_scenarios'] = self.benchmark_scenarios()
        
        # 3. Performance Validation
        self.logger.info("Step 3: Performance Validation")
        # Use medium load scenario for validation
        medium_load_metrics = results['load_test_scenarios']['medium_load']
        results['performance_validation'] = self.validate_performance_targets(medium_load_metrics)
        
        # 4. Optimization Recommendations
        self.logger.info("Step 4: Optimization Recommendations")
        results['recommendations'] = self.generate_optimization_recommendations(medium_load_metrics)
        
        # Summary
        self.logger.section("PERFORMANCE TEST SUMMARY", level=2)
        health_status = results['health_check']['status']
        validation_passed = sum(results['performance_validation'].values())
        validation_total = len(results['performance_validation'])
        
        self.logger.info(f"Health Status: {health_status}")
        self.logger.info(f"Performance Validation: {validation_passed}/{validation_total} targets met")
        self.logger.info(f"Recommendations Generated: {len(results['recommendations'])}")
        
        return results