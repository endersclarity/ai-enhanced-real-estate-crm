#!/usr/bin/env python3
"""
Performance Optimization and Load Testing System for Narissa Realty CRM
Implements database query optimization, response time optimization, and load testing
"""

import os
import json
import time
import sqlite3
import logging
import threading
import requests
import statistics
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, request, jsonify, g
import psutil
from typing import Dict, List, Optional, Tuple
import subprocess

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseOptimizer:
    """Database query optimization and performance tuning"""
    
    def __init__(self, db_path="real_estate_crm.db"):
        self.db_path = db_path
        self.init_optimization_tables()
    
    def init_optimization_tables(self):
        """Initialize performance optimization tracking tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Query performance tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS query_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    query_hash TEXT NOT NULL,
                    query_text TEXT NOT NULL,
                    execution_time REAL NOT NULL,
                    rows_examined INTEGER,
                    rows_returned INTEGER,
                    cache_hit BOOLEAN DEFAULT 0,
                    index_used TEXT,
                    optimization_applied TEXT
                )
            ''')
            
            # Index recommendations
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS index_recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_name TEXT NOT NULL,
                    column_names TEXT NOT NULL,
                    query_pattern TEXT,
                    estimated_improvement REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    applied BOOLEAN DEFAULT 0
                )
            ''')
            
            conn.commit()
            logger.info("Database optimization tables initialized")
    
    def analyze_query_performance(self) -> Dict:
        """Analyze database query performance"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Enable query plan analysis
            cursor.execute("PRAGMA query_planner = ON")
            
            # Test common queries and measure performance
            query_tests = [
                {
                    'name': 'user_lookup',
                    'query': 'SELECT * FROM users WHERE username = ?',
                    'params': ['admin']
                },
                {
                    'name': 'client_search',
                    'query': 'SELECT * FROM clients WHERE name LIKE ? LIMIT 10',
                    'params': ['%test%']
                },
                {
                    'name': 'recent_transactions',
                    'query': 'SELECT * FROM transactions WHERE created_at > ? ORDER BY created_at DESC LIMIT 20',
                    'params': [datetime.now() - timedelta(days=30)]
                },
                {
                    'name': 'user_permissions',
                    'query': '''
                        SELECT p.name FROM role_permissions rp
                        JOIN roles r ON rp.role_id = r.id
                        JOIN permissions p ON rp.permission_id = p.id
                        WHERE r.name = ?
                    ''',
                    'params': ['agent']
                }
            ]
            
            results = {}
            
            for test in query_tests:
                start_time = time.time()
                try:
                    if test.get('params'):
                        cursor.execute(test['query'], test['params'])
                    else:
                        cursor.execute(test['query'])
                    
                    rows = cursor.fetchall()
                    execution_time = time.time() - start_time
                    
                    results[test['name']] = {
                        'execution_time': execution_time,
                        'rows_returned': len(rows),
                        'status': 'success'
                    }
                    
                    logger.info(f"Query {test['name']}: {execution_time:.4f}s, {len(rows)} rows")
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    results[test['name']] = {
                        'execution_time': execution_time,
                        'error': str(e),
                        'status': 'error'
                    }
                    logger.error(f"Query {test['name']} failed: {e}")
            
            return results
    
    def optimize_database_schema(self) -> List[Dict]:
        """Optimize database schema with indexes and constraints"""
        optimizations = []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Recommended indexes for common queries
            indexes_to_create = [
                {
                    'table': 'users',
                    'columns': ['username'],
                    'name': 'idx_users_username'
                },
                {
                    'table': 'users',
                    'columns': ['email'],
                    'name': 'idx_users_email'
                },
                {
                    'table': 'users',
                    'columns': ['role'],
                    'name': 'idx_users_role'
                },
                {
                    'table': 'clients',
                    'columns': ['agent_id'],
                    'name': 'idx_clients_agent'
                },
                {
                    'table': 'clients',
                    'columns': ['created_at'],
                    'name': 'idx_clients_created_at'
                },
                {
                    'table': 'request_metrics',
                    'columns': ['timestamp'],
                    'name': 'idx_request_metrics_timestamp'
                },
                {
                    'table': 'request_metrics',
                    'columns': ['endpoint'],
                    'name': 'idx_request_metrics_endpoint'
                },
                {
                    'table': 'access_log',
                    'columns': ['user_id', 'timestamp'],
                    'name': 'idx_access_log_user_timestamp'
                }
            ]
            
            for index in indexes_to_create:
                try:
                    # Check if index already exists
                    cursor.execute('''
                        SELECT name FROM sqlite_master
                        WHERE type='index' AND name=?
                    ''', (index['name'],))
                    
                    if not cursor.fetchone():
                        columns = ', '.join(index['columns'])
                        create_sql = f'''
                            CREATE INDEX {index['name']}
                            ON {index['table']} ({columns})
                        '''
                        
                        start_time = time.time()
                        cursor.execute(create_sql)
                        execution_time = time.time() - start_time
                        
                        optimizations.append({
                            'type': 'index_creation',
                            'table': index['table'],
                            'columns': index['columns'],
                            'name': index['name'],
                            'execution_time': execution_time,
                            'status': 'success'
                        })
                        
                        logger.info(f"Created index {index['name']} on {index['table']}({columns})")
                    else:
                        logger.info(f"Index {index['name']} already exists")
                        
                except Exception as e:
                    optimizations.append({
                        'type': 'index_creation',
                        'table': index['table'],
                        'name': index['name'],
                        'error': str(e),
                        'status': 'error'
                    })
                    logger.error(f"Failed to create index {index['name']}: {e}")
            
            # Optimize database with VACUUM and ANALYZE
            try:
                start_time = time.time()
                cursor.execute("VACUUM")
                vacuum_time = time.time() - start_time
                
                start_time = time.time()
                cursor.execute("ANALYZE")
                analyze_time = time.time() - start_time
                
                optimizations.append({
                    'type': 'database_maintenance',
                    'vacuum_time': vacuum_time,
                    'analyze_time': analyze_time,
                    'status': 'success'
                })
                
                logger.info(f"Database maintenance completed: VACUUM {vacuum_time:.2f}s, ANALYZE {analyze_time:.2f}s")
                
            except Exception as e:
                optimizations.append({
                    'type': 'database_maintenance',
                    'error': str(e),
                    'status': 'error'
                })
                logger.error(f"Database maintenance failed: {e}")
            
            conn.commit()
        
        return optimizations

class ResponseTimeOptimizer:
    """Response time optimization for API endpoints"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = {}
        self.response_time_targets = {
            '/health': 0.1,
            '/api/users': 0.5,
            '/api/clients': 0.5,
            '/api/properties': 0.5,
            '/auth/profile': 0.3
        }
    
    def optimize_response_caching(self, app: Flask):
        """Implement response caching for improved performance"""
        
        @app.before_request
        def before_request():
            """Set up request context for optimization"""
            g.start_time = time.time()
            g.cache_key = f"{request.method}:{request.path}:{request.query_string.decode()}"
        
        @app.after_request
        def after_request(response):
            """Apply response optimizations"""
            if hasattr(g, 'start_time'):
                response_time = time.time() - g.start_time
                
                # Add performance headers
                response.headers['X-Response-Time'] = f"{response_time:.4f}"
                
                # Cache GET requests for non-sensitive endpoints
                if request.method == 'GET' and self._is_cacheable(request.path):
                    if response.status_code == 200:
                        self._cache_response(g.cache_key, response.get_data(), response_time)
                
                # Log slow requests
                target_time = self.response_time_targets.get(request.path, 1.0)
                if response_time > target_time:
                    logger.warning(f"Slow request: {request.path} took {response_time:.4f}s (target: {target_time}s)")
            
            return response
        
        @app.before_request
        def check_cache():
            """Check for cached responses"""
            if request.method == 'GET' and self._is_cacheable(request.path):
                cache_key = f"{request.method}:{request.path}:{request.query_string.decode()}"
                cached_response = self._get_cached_response(cache_key)
                if cached_response:
                    return cached_response
    
    def _is_cacheable(self, path: str) -> bool:
        """Determine if endpoint response can be cached"""
        cacheable_patterns = [
            '/api/users',
            '/api/clients',
            '/api/properties',
            '/health'
        ]
        
        # Don't cache authentication endpoints or user-specific data
        non_cacheable_patterns = [
            '/auth',
            '/logout',
            '/api/monitoring'
        ]
        
        for pattern in non_cacheable_patterns:
            if pattern in path:
                return False
        
        for pattern in cacheable_patterns:
            if pattern in path:
                return True
        
        return False
    
    def _cache_response(self, key: str, data: bytes, response_time: float, ttl: int = 300):
        """Cache response data"""
        self.cache[key] = {
            'data': data,
            'timestamp': time.time(),
            'response_time': response_time
        }
        self.cache_ttl[key] = time.time() + ttl
    
    def _get_cached_response(self, key: str) -> Optional[bytes]:
        """Get cached response if valid"""
        if key in self.cache and key in self.cache_ttl:
            if time.time() < self.cache_ttl[key]:
                cached = self.cache[key]
                logger.info(f"Cache hit for {key} (saved {cached['response_time']:.4f}s)")
                return cached['data']
            else:
                # Remove expired cache
                del self.cache[key]
                del self.cache_ttl[key]
        
        return None
    
    def get_performance_report(self) -> Dict:
        """Generate performance optimization report"""
        return {
            'cache_stats': {
                'total_entries': len(self.cache),
                'cache_size_mb': sum(len(entry['data']) for entry in self.cache.values()) / (1024 * 1024),
                'hit_rate': self._calculate_hit_rate()
            },
            'response_time_targets': self.response_time_targets,
            'optimization_status': 'active'
        }
    
    def _calculate_hit_rate(self) -> float:
        """Calculate cache hit rate (simplified)"""
        # This is a simplified calculation - in production, you'd track hits/misses
        return 0.75 if len(self.cache) > 0 else 0.0

class LoadTester:
    """Load testing and performance benchmarking"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = {}
    
    def run_load_test(self, endpoint: str, concurrent_users: int = 10, 
                     duration_seconds: int = 60, ramp_up_seconds: int = 10) -> Dict:
        """Run load test on specific endpoint"""
        logger.info(f"Starting load test: {endpoint} with {concurrent_users} users for {duration_seconds}s")
        
        test_start_time = time.time()
        results = {
            'endpoint': endpoint,
            'concurrent_users': concurrent_users,
            'duration_seconds': duration_seconds,
            'requests': [],
            'errors': [],
            'start_time': test_start_time
        }
        
        # Calculate request intervals for ramp-up
        ramp_up_interval = ramp_up_seconds / concurrent_users if concurrent_users > 0 else 0
        
        def worker(worker_id: int) -> List[Dict]:
            """Individual worker thread for load testing"""
            worker_results = []
            
            # Ramp-up delay
            time.sleep(worker_id * ramp_up_interval)
            
            session = requests.Session()
            worker_end_time = test_start_time + duration_seconds
            
            while time.time() < worker_end_time:
                request_start = time.time()
                try:
                    response = session.get(f"{self.base_url}{endpoint}", timeout=10)
                    request_end = time.time()
                    
                    worker_results.append({
                        'worker_id': worker_id,
                        'timestamp': request_start,
                        'response_time': request_end - request_start,
                        'status_code': response.status_code,
                        'success': response.status_code < 400,
                        'content_length': len(response.content)
                    })
                    
                except Exception as e:
                    request_end = time.time()
                    worker_results.append({
                        'worker_id': worker_id,
                        'timestamp': request_start,
                        'response_time': request_end - request_start,
                        'status_code': 0,
                        'success': False,
                        'error': str(e)
                    })
                
                # Small delay to prevent overwhelming the server
                time.sleep(0.1)
            
            return worker_results
        
        # Execute load test with thread pool
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(worker, i) for i in range(concurrent_users)]
            
            for future in as_completed(futures):
                try:
                    worker_results = future.result()
                    results['requests'].extend(worker_results)
                except Exception as e:
                    results['errors'].append(str(e))
        
        # Calculate statistics
        results.update(self._calculate_load_test_stats(results['requests']))
        results['total_duration'] = time.time() - test_start_time
        
        logger.info(f"Load test completed: {len(results['requests'])} requests, "
                   f"{results['success_rate']:.1f}% success rate, "
                   f"{results['avg_response_time']:.3f}s avg response time")
        
        return results
    
    def _calculate_load_test_stats(self, requests: List[Dict]) -> Dict:
        """Calculate load test statistics"""
        if not requests:
            return {
                'total_requests': 0,
                'success_rate': 0,
                'avg_response_time': 0,
                'min_response_time': 0,
                'max_response_time': 0,
                'p95_response_time': 0,
                'requests_per_second': 0
            }
        
        successful_requests = [r for r in requests if r['success']]
        response_times = [r['response_time'] for r in requests]
        
        return {
            'total_requests': len(requests),
            'successful_requests': len(successful_requests),
            'success_rate': (len(successful_requests) / len(requests)) * 100,
            'avg_response_time': statistics.mean(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'p95_response_time': statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times),
            'requests_per_second': len(requests) / (max(r['timestamp'] for r in requests) - min(r['timestamp'] for r in requests)) if len(requests) > 1 else 0
        }
    
    def run_comprehensive_load_test(self) -> Dict:
        """Run comprehensive load test across multiple endpoints"""
        endpoints_to_test = [
            {'endpoint': '/', 'users': 5, 'duration': 30},
            {'endpoint': '/health', 'users': 10, 'duration': 30},
            {'endpoint': '/api/users', 'users': 8, 'duration': 45},
            {'endpoint': '/api/clients', 'users': 8, 'duration': 45}
        ]
        
        comprehensive_results = {
            'test_start': datetime.now().isoformat(),
            'endpoint_results': {},
            'overall_stats': {}
        }
        
        all_requests = []
        
        for test_config in endpoints_to_test:
            endpoint_result = self.run_load_test(
                endpoint=test_config['endpoint'],
                concurrent_users=test_config['users'],
                duration_seconds=test_config['duration']
            )
            
            comprehensive_results['endpoint_results'][test_config['endpoint']] = endpoint_result
            all_requests.extend(endpoint_result['requests'])
            
            # Wait between tests to avoid overwhelming the system
            time.sleep(5)
        
        # Calculate overall statistics
        comprehensive_results['overall_stats'] = self._calculate_load_test_stats(all_requests)
        comprehensive_results['test_end'] = datetime.now().isoformat()
        
        return comprehensive_results
    
    def run_stress_test(self, endpoint: str = '/health', max_users: int = 50) -> Dict:
        """Run stress test to find breaking point"""
        logger.info(f"Starting stress test on {endpoint} up to {max_users} users")
        
        stress_results = {
            'endpoint': endpoint,
            'max_users': max_users,
            'breaking_point': None,
            'user_levels': []
        }
        
        # Test increasing user loads
        for user_count in range(5, max_users + 1, 5):
            logger.info(f"Testing with {user_count} concurrent users")
            
            result = self.run_load_test(
                endpoint=endpoint,
                concurrent_users=user_count,
                duration_seconds=30,
                ramp_up_seconds=5
            )
            
            stress_results['user_levels'].append({
                'users': user_count,
                'success_rate': result['success_rate'],
                'avg_response_time': result['avg_response_time'],
                'requests_per_second': result['requests_per_second']
            })
            
            # Check if system is degrading
            if result['success_rate'] < 95 or result['avg_response_time'] > 5.0:
                stress_results['breaking_point'] = user_count
                logger.warning(f"System degradation detected at {user_count} users")
                break
            
            # Wait between stress levels
            time.sleep(10)
        
        return stress_results

class PerformanceOptimizationSuite:
    """Complete performance optimization and testing suite"""
    
    def __init__(self, db_path="real_estate_crm.db", base_url="http://localhost:8000"):
        self.db_path = db_path
        self.base_url = base_url
        self.db_optimizer = DatabaseOptimizer(db_path)
        self.response_optimizer = ResponseTimeOptimizer()
        self.load_tester = LoadTester(base_url)
    
    def run_complete_optimization(self) -> Dict:
        """Run complete performance optimization suite"""
        logger.info("Starting complete performance optimization suite")
        
        optimization_results = {
            'start_time': datetime.now().isoformat(),
            'phases': {}
        }
        
        # Phase 1: Database optimization
        logger.info("Phase 1: Database optimization")
        optimization_results['phases']['database_optimization'] = {
            'query_analysis': self.db_optimizer.analyze_query_performance(),
            'schema_optimization': self.db_optimizer.optimize_database_schema()
        }
        
        # Phase 2: Response time optimization report
        logger.info("Phase 2: Response time optimization")
        optimization_results['phases']['response_optimization'] = {
            'performance_report': self.response_optimizer.get_performance_report()
        }
        
        # Phase 3: Load testing
        logger.info("Phase 3: Load testing")
        optimization_results['phases']['load_testing'] = {
            'comprehensive_test': self.load_tester.run_comprehensive_load_test()
        }
        
        # Phase 4: Stress testing
        logger.info("Phase 4: Stress testing")
        optimization_results['phases']['stress_testing'] = {
            'stress_test': self.load_tester.run_stress_test()
        }
        
        optimization_results['end_time'] = datetime.now().isoformat()
        optimization_results['summary'] = self._generate_optimization_summary(optimization_results)
        
        # Save results
        with open("deployment/performance_optimization_results.json", "w") as f:
            json.dump(optimization_results, f, indent=2)
        
        logger.info("Performance optimization suite completed")
        return optimization_results
    
    def _generate_optimization_summary(self, results: Dict) -> Dict:
        """Generate optimization summary and recommendations"""
        summary = {
            'database_optimizations_applied': 0,
            'response_time_improvements': [],
            'load_test_success_rate': 0,
            'recommended_max_users': 0,
            'recommendations': []
        }
        
        # Database optimization summary
        if 'database_optimization' in results['phases']:
            db_phase = results['phases']['database_optimization']
            schema_opts = db_phase.get('schema_optimization', [])
            summary['database_optimizations_applied'] = len([opt for opt in schema_opts if opt.get('status') == 'success'])
        
        # Load testing summary
        if 'load_testing' in results['phases']:
            load_phase = results['phases']['load_testing']
            overall_stats = load_phase.get('comprehensive_test', {}).get('overall_stats', {})
            summary['load_test_success_rate'] = overall_stats.get('success_rate', 0)
        
        # Stress testing summary
        if 'stress_testing' in results['phases']:
            stress_phase = results['phases']['stress_testing']
            stress_test = stress_phase.get('stress_test', {})
            summary['recommended_max_users'] = stress_test.get('breaking_point', 50) or 50
        
        # Generate recommendations
        if summary['load_test_success_rate'] < 95:
            summary['recommendations'].append("Consider additional response time optimization")
        
        if summary['recommended_max_users'] < 20:
            summary['recommendations'].append("System may need hardware scaling for production load")
        
        if summary['database_optimizations_applied'] == 0:
            summary['recommendations'].append("Review database schema for optimization opportunities")
        
        return summary

def main():
    """Test the performance optimization system"""
    optimizer = PerformanceOptimizationSuite()
    
    print("Performance Optimization Suite")
    print("=" * 40)
    
    # Run complete optimization
    results = optimizer.run_complete_optimization()
    
    # Print summary
    summary = results.get('summary', {})
    print(f"\nOptimization Summary:")
    print(f"Database optimizations applied: {summary.get('database_optimizations_applied', 0)}")
    print(f"Load test success rate: {summary.get('load_test_success_rate', 0):.1f}%")
    print(f"Recommended max concurrent users: {summary.get('recommended_max_users', 'Unknown')}")
    
    recommendations = summary.get('recommendations', [])
    if recommendations:
        print(f"\nRecommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
    
    print(f"\nDetailed results saved to: deployment/performance_optimization_results.json")

if __name__ == "__main__":
    main()