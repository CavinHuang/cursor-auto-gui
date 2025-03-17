from .log_manager import LogManager, LogLevel

logger = LogManager()
logger.set_log_level(LogLevel.DEBUG)
logger.set_gui_logger(logger)

__all__ = ['LogManager', 'LogLevel', 'logger']