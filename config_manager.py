"""
Configuration Manager for Production Trading Bot
Handles all configuration loading, validation, and management
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ExchangeConfig:
    """Exchange configuration"""
    name: str
    api_key: str = ""
    api_secret: str = ""
    passphrase: str = ""
    testnet: bool = True
    sandbox: bool = True
    rate_limit: bool = True
    
    def is_configured(self) -> bool:
        """Check if exchange is properly configured"""
        return bool(self.api_key and self.api_secret)

@dataclass
class RiskConfig:
    """Risk management configuration"""
    max_position_size: float = 2.0  # % of portfolio
    daily_loss_limit: float = 50.0  # USD
    max_drawdown: float = 10.0  # %
    risk_per_trade: float = 2.0  # %
    max_concurrent_trades: int = 5
    min_confidence: float = 80.0  # % for auto trading
    stop_loss_percentage: float = 2.0  # %
    take_profit_percentage: float = 5.0  # %
    trailing_stop: bool = True
    trailing_stop_percentage: float = 1.5  # %

@dataclass
class TradingConfig:
    """Trading configuration"""
    enabled: bool = False
    auto_trading: bool = False
    mode: str = "paper"  # paper, testnet, live
    default_leverage: int = 3
    max_leverage: int = 5
    slippage_tolerance: float = 0.5  # %
    order_timeout: int = 30  # seconds
    partial_fill_enabled: bool = True
    
    def is_live(self) -> bool:
        """Check if in live trading mode"""
        return self.mode == "live" and self.enabled

@dataclass
class NotificationConfig:
    """Notification configuration"""
    telegram_enabled: bool = False
    telegram_token: str = ""
    telegram_admin_channel: str = ""
    telegram_free_channel: str = ""
    telegram_vip_channel: str = ""
    email_enabled: bool = False
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    alert_email: str = ""
    discord_enabled: bool = False
    discord_webhook: str = ""

@dataclass
class DatabaseConfig:
    """Database configuration"""
    type: str = "sqlite"  # sqlite, postgresql, mysql
    sqlite_path: str = "data/trading_bot.db"
    host: str = "localhost"
    port: int = 5432
    name: str = "trading_bot"
    user: str = ""
    password: str = ""
    
    def get_connection_string(self) -> str:
        """Get database connection string"""
        if self.type == "sqlite":
            return f"sqlite:///{self.sqlite_path}"
        elif self.type == "postgresql":
            return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        elif self.type == "mysql":
            return f"mysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        return ""

@dataclass
class MLConfig:
    """Machine Learning configuration"""
    enabled: bool = True
    model_update_frequency: int = 24  # hours
    min_training_data: int = 1000
    confidence_threshold: float = 70.0
    feature_engineering: bool = True
    ensemble_models: bool = True

@dataclass
class MonitoringConfig:
    """Monitoring configuration"""
    enabled: bool = True
    health_check_interval: int = 60  # seconds
    alert_loss_threshold: float = 5.0  # USD
    alert_drawdown_threshold: float = 5.0  # %
    prometheus_enabled: bool = False
    prometheus_port: int = 9090
    grafana_enabled: bool = False

@dataclass
class BotConfig:
    """Main bot configuration"""
    exchange: Dict[str, ExchangeConfig] = field(default_factory=dict)
    risk: RiskConfig = field(default_factory=RiskConfig)
    trading: TradingConfig = field(default_factory=TradingConfig)
    notification: NotificationConfig = field(default_factory=NotificationConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    ml: MLConfig = field(default_factory=MLConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    # System settings
    log_level: str = "INFO"
    log_dir: str = "logs"
    debug_mode: bool = False
    verbose_logging: bool = False
    
    # Performance settings
    use_websockets: bool = True
    cache_enabled: bool = True
    cache_ttl: int = 300  # seconds
    
    # Security settings
    two_factor_auth: bool = False
    ip_whitelist: list = field(default_factory=list)
    session_timeout: int = 30  # minutes

class ConfigManager:
    """Configuration manager for the trading bot"""
    
    def __init__(self, config_file: str = ".env"):
        self.config_file = config_file
        self.config = BotConfig()
        self.load_config()
        self.validate_config()
    
    def load_config(self):
        """Load configuration from environment variables and files"""
        # Try to load .env file
        env_path = Path(self.config_file)
        if env_path.exists():
            self._load_env_file(env_path)
        
        # Load exchange configurations
        self._load_exchange_config()
        
        # Load risk configuration
        self._load_risk_config()
        
        # Load trading configuration
        self._load_trading_config()
        
        # Load notification configuration
        self._load_notification_config()
        
        # Load database configuration
        self._load_database_config()
        
        # Load ML configuration
        self._load_ml_config()
        
        # Load monitoring configuration
        self._load_monitoring_config()
        
        # Load system settings
        self._load_system_settings()
        
        logger.info("Configuration loaded successfully")
    
    def _load_env_file(self, path: Path):
        """Load environment variables from file"""
        try:
            with open(path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
        except Exception as e:
            logger.warning(f"Could not load .env file: {e}")
    
    def _load_exchange_config(self):
        """Load exchange configurations"""
        exchanges = ['bybit', 'binance', 'okx', 'coinbase', 'kucoin']
        
        for exchange in exchanges:
            config = ExchangeConfig(
                name=exchange,
                api_key=os.getenv(f'{exchange.upper()}_API_KEY', ''),
                api_secret=os.getenv(f'{exchange.upper()}_API_SECRET', ''),
                passphrase=os.getenv(f'{exchange.upper()}_PASSPHRASE', ''),
                testnet=self._get_bool(f'{exchange.upper()}_TESTNET', True),
                sandbox=self._get_bool(f'{exchange.upper()}_SANDBOX', True),
                rate_limit=self._get_bool(f'{exchange.upper()}_RATE_LIMIT', True)
            )
            self.config.exchange[exchange] = config
    
    def _load_risk_config(self):
        """Load risk management configuration"""
        self.config.risk = RiskConfig(
            max_position_size=self._get_float('MAX_POSITION_SIZE', 2.0),
            daily_loss_limit=self._get_float('DAILY_LOSS_LIMIT', 50.0),
            max_drawdown=self._get_float('MAX_DRAWDOWN', 10.0),
            risk_per_trade=self._get_float('RISK_PER_TRADE', 2.0),
            max_concurrent_trades=self._get_int('MAX_CONCURRENT_TRADES', 5),
            min_confidence=self._get_float('MIN_CONFIDENCE', 80.0),
            stop_loss_percentage=self._get_float('STOP_LOSS_PERCENTAGE', 2.0),
            take_profit_percentage=self._get_float('TAKE_PROFIT_PERCENTAGE', 5.0),
            trailing_stop=self._get_bool('TRAILING_STOP', True),
            trailing_stop_percentage=self._get_float('TRAILING_STOP_PERCENTAGE', 1.5)
        )
    
    def _load_trading_config(self):
        """Load trading configuration"""
        self.config.trading = TradingConfig(
            enabled=self._get_bool('TRADING_ENABLED', False),
            auto_trading=self._get_bool('AUTO_TRADING_ENABLED', False),
            mode=os.getenv('TRADING_MODE', 'paper'),
            default_leverage=self._get_int('DEFAULT_LEVERAGE', 3),
            max_leverage=self._get_int('MAX_LEVERAGE', 5),
            slippage_tolerance=self._get_float('SLIPPAGE_TOLERANCE', 0.5),
            order_timeout=self._get_int('ORDER_TIMEOUT', 30),
            partial_fill_enabled=self._get_bool('PARTIAL_FILL_ENABLED', True)
        )
    
    def _load_notification_config(self):
        """Load notification configuration"""
        self.config.notification = NotificationConfig(
            telegram_enabled=self._get_bool('TELEGRAM_ENABLED', False),
            telegram_token=os.getenv('TELEGRAM_BOT_TOKEN', ''),
            telegram_admin_channel=os.getenv('TELEGRAM_ADMIN_CHANNEL', ''),
            telegram_free_channel=os.getenv('TELEGRAM_FREE_CHANNEL', ''),
            telegram_vip_channel=os.getenv('TELEGRAM_VIP_CHANNEL', ''),
            email_enabled=self._get_bool('EMAIL_ENABLED', False),
            smtp_host=os.getenv('SMTP_HOST', ''),
            smtp_port=self._get_int('SMTP_PORT', 587),
            smtp_user=os.getenv('SMTP_USER', ''),
            smtp_password=os.getenv('SMTP_PASSWORD', ''),
            alert_email=os.getenv('ALERT_EMAIL', ''),
            discord_enabled=self._get_bool('DISCORD_ENABLED', False),
            discord_webhook=os.getenv('DISCORD_WEBHOOK_URL', '')
        )
    
    def _load_database_config(self):
        """Load database configuration"""
        self.config.database = DatabaseConfig(
            type=os.getenv('DATABASE_TYPE', 'sqlite'),
            sqlite_path=os.getenv('SQLITE_DB_PATH', 'data/trading_bot.db'),
            host=os.getenv('DATABASE_HOST', 'localhost'),
            port=self._get_int('DATABASE_PORT', 5432),
            name=os.getenv('DATABASE_NAME', 'trading_bot'),
            user=os.getenv('DATABASE_USER', ''),
            password=os.getenv('DATABASE_PASSWORD', '')
        )
    
    def _load_ml_config(self):
        """Load ML configuration"""
        self.config.ml = MLConfig(
            enabled=self._get_bool('ML_ENABLED', True),
            model_update_frequency=self._get_int('MODEL_UPDATE_FREQUENCY', 24),
            min_training_data=self._get_int('MIN_TRAINING_DATA', 1000),
            confidence_threshold=self._get_float('ML_CONFIDENCE_THRESHOLD', 70.0),
            feature_engineering=self._get_bool('FEATURE_ENGINEERING', True),
            ensemble_models=self._get_bool('ENSEMBLE_MODELS', True)
        )
    
    def _load_monitoring_config(self):
        """Load monitoring configuration"""
        self.config.monitoring = MonitoringConfig(
            enabled=self._get_bool('MONITORING_ENABLED', True),
            health_check_interval=self._get_int('HEALTH_CHECK_INTERVAL', 60),
            alert_loss_threshold=self._get_float('ALERT_LOSS_THRESHOLD', 5.0),
            alert_drawdown_threshold=self._get_float('ALERT_DRAWDOWN_THRESHOLD', 5.0),
            prometheus_enabled=self._get_bool('PROMETHEUS_ENABLED', False),
            prometheus_port=self._get_int('PROMETHEUS_PORT', 9090),
            grafana_enabled=self._get_bool('GRAFANA_ENABLED', False)
        )
    
    def _load_system_settings(self):
        """Load system settings"""
        self.config.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.config.log_dir = os.getenv('LOG_DIR', 'logs')
        self.config.debug_mode = self._get_bool('DEBUG_MODE', False)
        self.config.verbose_logging = self._get_bool('VERBOSE_LOGGING', False)
        self.config.use_websockets = self._get_bool('USE_WEBSOCKETS', True)
        self.config.cache_enabled = self._get_bool('CACHE_ENABLED', True)
        self.config.cache_ttl = self._get_int('CACHE_TTL', 300)
        self.config.two_factor_auth = self._get_bool('TWO_FACTOR_AUTH', False)
        
        ip_whitelist = os.getenv('IP_WHITELIST', '')
        self.config.ip_whitelist = [ip.strip() for ip in ip_whitelist.split(',') if ip.strip()]
        self.config.session_timeout = self._get_int('SESSION_TIMEOUT', 30)
    
    def _get_bool(self, key: str, default: bool) -> bool:
        """Get boolean environment variable"""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    def _get_int(self, key: str, default: int) -> int:
        """Get integer environment variable"""
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            return default
    
    def _get_float(self, key: str, default: float) -> float:
        """Get float environment variable"""
        try:
            return float(os.getenv(key, str(default)))
        except ValueError:
            return default
    
    def validate_config(self):
        """Validate configuration for production readiness"""
        warnings = []
        errors = []
        
        # Check if we're in production mode with test settings
        if self.config.trading.mode == "live":
            if not any(ex.is_configured() for ex in self.config.exchange.values()):
                errors.append("No exchange configured for live trading")
            
            if self.config.trading.enabled and not self.config.risk.max_position_size:
                errors.append("Risk parameters not configured for live trading")
            
            if self.config.trading.auto_trading and self.config.risk.min_confidence < 70:
                warnings.append("Auto trading confidence threshold is low for live trading")
        
        # Check database configuration
        if self.config.database.type != "sqlite" and not self.config.database.user:
            errors.append("Database credentials not configured")
        
        # Check notification configuration
        if self.config.notification.telegram_enabled and not self.config.notification.telegram_token:
            warnings.append("Telegram enabled but token not configured")
        
        # Security checks
        if self.config.trading.mode == "live" and not self.config.two_factor_auth:
            warnings.append("2FA not enabled for live trading")
        
        if self.config.debug_mode and self.config.trading.mode == "live":
            errors.append("Debug mode enabled in live trading")
        
        # Log validation results
        for warning in warnings:
            logger.warning(f"Configuration warning: {warning}")
        
        for error in errors:
            logger.error(f"Configuration error: {error}")
        
        if errors and self.config.trading.mode == "live":
            raise ValueError("Configuration validation failed for live trading")
        
        return len(errors) == 0
    
    def get_exchange_config(self, exchange: str) -> Optional[ExchangeConfig]:
        """Get configuration for specific exchange"""
        return self.config.exchange.get(exchange)
    
    def save_config(self, path: str = None):
        """Save current configuration to file"""
        path = path or f"config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        config_dict = {
            'exchanges': {k: v.__dict__ for k, v in self.config.exchange.items()},
            'risk': self.config.risk.__dict__,
            'trading': self.config.trading.__dict__,
            'notification': self.config.notification.__dict__,
            'database': self.config.database.__dict__,
            'ml': self.config.ml.__dict__,
            'monitoring': self.config.monitoring.__dict__,
            'system': {
                'log_level': self.config.log_level,
                'log_dir': self.config.log_dir,
                'debug_mode': self.config.debug_mode,
                'verbose_logging': self.config.verbose_logging,
                'use_websockets': self.config.use_websockets,
                'cache_enabled': self.config.cache_enabled,
                'cache_ttl': self.config.cache_ttl
            }
        }
        
        # Remove sensitive data
        for exchange in config_dict['exchanges'].values():
            exchange['api_key'] = '***'
            exchange['api_secret'] = '***'
            exchange['passphrase'] = '***'
        
        config_dict['notification']['telegram_token'] = '***'
        config_dict['notification']['smtp_password'] = '***'
        config_dict['database']['password'] = '***'
        
        with open(path, 'w') as f:
            json.dump(config_dict, f, indent=2)
        
        logger.info(f"Configuration saved to {path}")
    
    def reload_config(self):
        """Reload configuration from sources"""
        logger.info("Reloading configuration...")
        self.load_config()
        self.validate_config()
        logger.info("Configuration reloaded successfully")

# Singleton instance
_config_manager = None

def get_config_manager(config_file: str = ".env") -> ConfigManager:
    """Get or create config manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_file)
    return _config_manager

def get_config() -> BotConfig:
    """Get bot configuration"""
    return get_config_manager().config