"""
Test script for enhanced QuoteWise AI functionality.
Demonstrates the new features and components.
"""

import os
import sys
import time
from pathlib import Path

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(os.path.dirname(current_dir), 'src')
sys.path.append(src_path)

from utils.logger import get_logger, logger
from utils.config import config
from utils.cache import cache, cached
from utils.exceptions import QuoteWiseException
from components.analytics import AnalyticsDashboard
from components.ui_components import ModernUIComponents

def test_logging_system():
    """Test the enhanced logging system."""
    print("🧪 Testing Logging System...")
    
    logger.info("Testing info logging")
    logger.warning("Testing warning logging")
    logger.error("Testing error logging")
    logger.log_quotation_event("test_event", "QT-001", test_data="sample")
    logger.log_agent_activity("test_agent", "test_activity", duration=1.5)
    logger.log_performance("test_operation", 2.3)
    
    print("✅ Logging system test completed")

def test_configuration_system():
    """Test the configuration management system."""
    print("🧪 Testing Configuration System...")
    
    print(f"Environment: {config.is_development()}")
    print(f"Database path: {config.get_database_path()}")
    print(f"Output directory: {config.get_output_directory()}")
    print(f"API model: {config.api.model_name}")
    print(f"Log level: {config.logging.level}")
    
    print("✅ Configuration system test completed")

def test_caching_system():
    """Test the caching system."""
    print("🧪 Testing Caching System...")
    
    # Test basic caching
    cache.set("test_key", "test_value", ttl=60)
    value = cache.get("test_key")
    print(f"Cached value: {value}")
    
    # Test cache statistics
    stats = cache.get_stats()
    print(f"Cache stats: {stats}")
    
    # Test cache cleanup
    cleaned = cache.cleanup_expired()
    print(f"Cleaned {cleaned} expired entries")
    
    print("✅ Caching system test completed")

def test_analytics_dashboard():
    """Test the analytics dashboard."""
    print("🧪 Testing Analytics Dashboard...")
    
    analytics = AnalyticsDashboard()
    
    # Test inventory analytics
    inventory_data = analytics.get_inventory_analytics()
    print(f"Inventory analytics: {len(inventory_data)} metrics")
    
    # Test quotation history
    quotations = analytics.get_quotation_history()
    print(f"Quotation history: {len(quotations)} entries")
    
    # Test export functionality
    report = analytics.export_analytics_report()
    print(f"Analytics report: {len(report)} characters")
    
    print("✅ Analytics dashboard test completed")

def test_ui_components():
    """Test the UI components."""
    print("🧪 Testing UI Components...")
    
    ui = ModernUIComponents()
    
    # Test component initialization
    print("UI components initialized successfully")
    
    print("✅ UI components test completed")

def test_error_handling():
    """Test the enhanced error handling."""
    print("🧪 Testing Error Handling...")
    
    try:
        # Test custom exception
        raise QuoteWiseException(
            "Test error message",
            error_code="TEST_ERROR",
            context={"test": "data"}
        )
    except QuoteWiseException as e:
        print(f"Caught custom exception: {e.message}")
        print(f"Error code: {e.error_code}")
        print(f"Context: {e.context}")
    
    print("✅ Error handling test completed")

def test_performance():
    """Test performance optimizations."""
    print("🧪 Testing Performance...")
    
    # Test cached function
    @cached(ttl=60)
    def expensive_operation():
        time.sleep(0.1)  # Simulate expensive operation
        return "result"
    
    # First call (should be slow)
    start_time = time.time()
    result1 = expensive_operation()
    first_call_time = time.time() - start_time
    
    # Second call (should be fast from cache)
    start_time = time.time()
    result2 = expensive_operation()
    second_call_time = time.time() - start_time
    
    print(f"First call time: {first_call_time:.3f}s")
    print(f"Second call time: {second_call_time:.3f}s")
    print(f"Speed improvement: {first_call_time/second_call_time:.1f}x")
    
    print("✅ Performance test completed")

def main():
    """Run all tests."""
    print("🚀 Starting Enhanced QuoteWise AI Tests")
    print("=" * 50)
    
    try:
        test_logging_system()
        print()
        
        test_configuration_system()
        print()
        
        test_caching_system()
        print()
        
        test_analytics_dashboard()
        print()
        
        test_ui_components()
        print()
        
        test_error_handling()
        print()
        
        test_performance()
        print()
        
        print("🎉 All tests completed successfully!")
        print("=" * 50)
        print("Enhanced QuoteWise AI is ready to use!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.error("Test suite failed", exception=e)

if __name__ == "__main__":
    main()






