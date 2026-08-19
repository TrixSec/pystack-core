"""
Production-ready logging tests
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from datetime import datetime

from py_core.logging import Logger, LogLevel, ConsoleFormatter, JSONFormatter, TextFormatter
from py_core.logging.handlers import ConsoleHandler, FileHandler, AsyncQueueHandler


class TestLoggerBasics:
    """Test basic logger functionality"""
    
    def test_logger_creation(self):
        """Test creating a logger"""
        logger = Logger(name="test-logger")
        assert logger.name == "test-logger"
        assert logger.level == LogLevel.INFO
    
    def test_logger_level_filtering(self):
        """Test that logger respects level filtering"""
        logger = Logger(name="test-logger", level=LogLevel.WARNING)
        
        # These should not log due to level filtering
        logger.debug("debug message")
        logger.info("info message")
        
        # These should log
        logger.warning("warning message")
        logger.error("error message")
        logger.critical("critical message")
    
    def test_set_level(self):
        """Test changing logger level"""
        logger = Logger(name="test-logger", level=LogLevel.INFO)
        assert logger.level == LogLevel.INFO
        
        logger.set_level(LogLevel.DEBUG)
        assert logger.level == LogLevel.DEBUG


class TestLoggerContext:
    """Test logger context management"""
    
    def test_add_global_context(self):
        """Test adding global context"""
        logger = Logger(name="test-logger")
        logger.add_global_context(app_name="test-app", version="1.0.0")
        
        assert "app_name" in logger._context
        assert logger._context["app_name"] == "test-app"
    
    def test_with_context(self):
        """Test creating logger with additional context"""
        logger = Logger(name="test-logger")
        logger.add_global_context(app_name="test-app")
        
        contextual_logger = logger.with_context(request_id="12345", user_id="user1")
        
        assert "app_name" in contextual_logger._context
        assert "request_id" in contextual_logger._context
        assert contextual_logger._context["request_id"] == "12345"
    
    def test_clear_context(self):
        """Test clearing logger context"""
        logger = Logger(name="test-logger")
        logger.add_global_context(app_name="test-app", version="1.0.0")
        
        assert len(logger._context) > 0
        logger.clear_context()
        assert len(logger._context) == 0


class TestFormatters:
    """Test log formatters"""
    
    def test_console_formatter(self):
        """Test console formatter"""
        formatter = ConsoleFormatter(show_colors=False, show_timestamp=True)
        
        log_entry = {
            "level": "INFO",
            "message": "Test message",
            "context": {"timestamp": "2024-01-01T00:00:00"}
        }
        
        formatted = formatter.format(log_entry)
        assert "INFO" in formatted
        assert "Test message" in formatted
        assert "2024-01-01T00:00:00" in formatted
    
    def test_json_formatter(self):
        """Test JSON formatter"""
        formatter = JSONFormatter()
        
        log_entry = {
            "level": "INFO",
            "message": "Test message",
            "context": {"timestamp": "2024-01-01T00:00:00"}
        }
        
        formatted = formatter.format(log_entry)
        import json
        parsed = json.loads(formatted)
        
        assert parsed["level"] == "INFO"
        assert parsed["message"] == "Test message"
    
    def test_text_formatter(self):
        """Test text formatter"""
        formatter = TextFormatter(show_timestamp=True)
        
        log_entry = {
            "level": "INFO",
            "message": "Test message",
            "context": {"timestamp": "2024-01-01T00:00:00"}
        }
        
        formatted = formatter.format(log_entry)
        assert "INFO" in formatted
        assert "Test message" in formatted


class TestHandlers:
    """Test log handlers"""
    
    def test_console_handler(self):
        """Test console handler"""
        handler = ConsoleHandler(level=LogLevel.INFO)
        assert handler.level == LogLevel.INFO
        assert handler._formatter is not None
    
    def test_file_handler_creation(self):
        """Test file handler creation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.log")
            handler = FileHandler(file_path=file_path, level=LogLevel.DEBUG)
            
            assert handler.file_path == Path(file_path)
            assert handler.level == LogLevel.DEBUG
            assert handler._formatter is not None
    
    @pytest.mark.asyncio
    async def test_file_handler_writing(self):
        """Test file handler actually writes to file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.log")
            handler = FileHandler(file_path=file_path, level=LogLevel.DEBUG)
            
            log_entry = {
                "level": "INFO",
                "message": "Test message",
                "formatted": "INFO: Test message"
            }
            
            await handler.emit(log_entry)
            
            # Check file was written
            assert os.path.exists(file_path)
            with open(file_path, 'r') as f:
                content = f.read()
                assert "Test message" in content
    
    def test_async_queue_handler(self):
        """Test async queue handler"""
        handler = AsyncQueueHandler(level=LogLevel.INFO, queue_size=100)
        assert handler.level == LogLevel.INFO
        assert handler._queue.maxsize == 100
    
    @pytest.mark.asyncio
    async def test_async_queue_handler_operations(self):
        """Test async queue handler start/stop"""
        handler = AsyncQueueHandler(level=LogLevel.INFO, queue_size=100)
        
        await handler.start()
        assert handler._running is True
        
        await handler.stop()
        assert handler._running is False


class TestAsyncLogging:
    """Test async logging functionality"""
    
    @pytest.mark.asyncio
    async def test_async_logging_methods(self):
        """Test async logging methods"""
        logger = Logger(name="test-logger", level=LogLevel.DEBUG)
        
        # These should not raise errors
        await logger.adebug("async debug message")
        await logger.ainfo("async info message")
        await logger.awarning("async warning message")
        await logger.aerror("async error message")
        await logger.acritical("async critical message")
    
    @pytest.mark.asyncio
    async def test_enable_async_logging(self):
        """Test enabling async logging"""
        logger = Logger(name="test-logger", level=LogLevel.DEBUG)
        
        logger.enable_async_logging(queue_size=100)
        assert logger._queue_handler is not None
        
        await logger.start_async()
        assert logger._running is True
        
        await logger.stop_async()
        assert logger._running is False


class TestRequestTracking:
    """Test request ID tracking"""
    
    def test_set_request_id(self):
        """Test setting request ID"""
        logger = Logger(name="test-logger")
        logger.set_request_id("test-request-123")
        
        from py_core.logging.logger import _request_id
        assert _request_id.get() == "test-request-123"
    
    def test_request_id_in_context(self):
        """Test that request ID appears in log context"""
        logger = Logger(name="test-logger")
        logger.set_request_id("test-request-123")
        
        context = logger._get_context()
        assert "request_id" in context
        assert context["request_id"] == "test-request-123"


class TestLogLevelConversion:
    """Test log level conversion"""
    
    def test_level_from_string(self):
        """Test converting string to LogLevel"""
        assert LogLevel.from_string("DEBUG") == LogLevel.DEBUG
        assert LogLevel.from_string("INFO") == LogLevel.INFO
        assert LogLevel.from_string("WARNING") == LogLevel.WARNING
        assert LogLevel.from_string("ERROR") == LogLevel.ERROR
        assert LogLevel.from_string("CRITICAL") == LogLevel.CRITICAL
        assert LogLevel.from_string("INVALID") == LogLevel.INFO  # Default
    
    def test_level_values(self):
        """Test that level values are correct"""
        assert LogLevel.DEBUG.value == 10
        assert LogLevel.INFO.value == 20
        assert LogLevel.WARNING.value == 30
        assert LogLevel.ERROR.value == 40
        assert LogLevel.CRITICAL.value == 50


class TestLogEntryBuilding:
    """Test log entry building"""
    
    def test_build_log_entry(self):
        """Test building a complete log entry"""
        logger = Logger(name="test-logger")
        logger.add_global_context(app_name="test-app")
        
        entry = logger._build_log_entry(LogLevel.INFO, "Test message", user_id="user1")
        
        assert entry["level"] == "INFO"
        assert entry["message"] == "Test message"
        assert entry["context"]["logger"] == "test-logger"
        assert entry["context"]["app_name"] == "test-app"
        assert entry["user_id"] == "user1"


class TestPerformance:
    """Test logging performance"""
    
    @pytest.mark.asyncio
    async def test_logging_performance(self):
        """Test that logging can handle high throughput"""
        logger = Logger(name="test-logger", level=LogLevel.INFO)
        logger.enable_async_logging(queue_size=10000)
        await logger.start_async()
        
        # Log 1000 messages
        start = datetime.now()
        for i in range(1000):
            await logger.ainfo(f"Test message {i}")
        end = datetime.now()
        
        duration = (end - start).total_seconds()
        await logger.stop_async()
        
        # Should be able to log 1000 messages in less than 1 second
        assert duration < 1.0, f"Logging took {duration} seconds for 1000 messages"


class TestIntegration:
    """Integration tests for logging"""
    
    @pytest.mark.asyncio
    async def test_full_logging_pipeline(self):
        """Test complete logging pipeline with file handler"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.log")
            
            logger = Logger(name="test-logger", level=LogLevel.DEBUG)
            file_handler = FileHandler(file_path=file_path, level=LogLevel.DEBUG)
            logger.add_handler(file_handler)
            
            logger.enable_async_logging()
            await logger.start_async()
            
            # Log some messages
            await logger.ainfo("Test message 1", user_id="user1")
            await logger.awarning("Test warning", error_code="ERR001")
            
            await logger.stop_async()
            
            # Verify file content
            with open(file_path, 'r') as f:
                content = f.read()
                assert "Test message 1" in content
                assert "Test warning" in content