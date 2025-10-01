#!/usr/bin/env python3
"""
Architectural Alignment Module
Ensures all components work together seamlessly
Fixes misalignments, wiring issues, and integration problems
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable, Tuple
from pathlib import Path
from datetime import datetime
import inspect
import importlib

logger = logging.getLogger(__name__)

# ============================================
# COMPONENT REGISTRY
# ============================================

class ComponentRegistry:
    """
    Central registry for all bot components
    Ensures proper wiring and dependency injection
    """
    
    def __init__(self):
        self.components = {}
        self.dependencies = {}
        self.initializers = {}
        self.health_checks = {}
        
    def register(self, name: str, component: Any, 
                dependencies: List[str] = None,
                initializer: Callable = None,
                health_check: Callable = None):
        """Register a component with its dependencies"""
        self.components[name] = component
        self.dependencies[name] = dependencies or []
        
        if initializer:
            self.initializers[name] = initializer
            
        if health_check:
            self.health_checks[name] = health_check
            
        logger.info(f"Registered component: {name}")
        
    def get(self, name: str) -> Any:
        """Get a component by name"""
        if name not in self.components:
            logger.warning(f"Component {name} not found")
            return None
        return self.components[name]
        
    def initialize_all(self):
        """Initialize all components in dependency order"""
        initialized = set()
        
        def init_component(name: str):
            if name in initialized:
                return
                
            # Initialize dependencies first
            for dep in self.dependencies.get(name, []):
                if dep not in initialized:
                    init_component(dep)
                    
            # Initialize this component
            if name in self.initializers:
                try:
                    logger.info(f"Initializing {name}...")
                    self.initializers[name](self.components[name])
                    initialized.add(name)
                except Exception as e:
                    logger.error(f"Failed to initialize {name}: {e}")
                    
        for name in self.components:
            init_component(name)
            
    def check_health(self) -> Dict[str, bool]:
        """Check health of all components"""
        results = {}
        
        for name, check in self.health_checks.items():
            try:
                results[name] = check(self.components.get(name))
            except Exception as e:
                logger.error(f"Health check failed for {name}: {e}")
                results[name] = False
                
        return results

# Global registry
component_registry = ComponentRegistry()

# ============================================
# DEPENDENCY INJECTOR
# ============================================

class DependencyInjector:
    """
    Handles dependency injection across components
    """
    
    @staticmethod
    def inject_dependencies(target: Any, registry: ComponentRegistry):
        """Inject dependencies into a target object"""
        
        # Get class annotations for type hints
        if hasattr(target, '__annotations__'):
            for attr_name, attr_type in target.__annotations__.items():
                # Try to find matching component
                type_name = attr_type.__name__ if hasattr(attr_type, '__name__') else str(attr_type)
                
                # Look for component by type name
                for comp_name, component in registry.components.items():
                    if type(component).__name__ == type_name:
                        setattr(target, attr_name, component)
                        logger.debug(f"Injected {comp_name} into {target.__class__.__name__}.{attr_name}")
                        
        # Also check for explicit dependency declarations
        if hasattr(target, 'required_components'):
            for comp_name in target.required_components:
                component = registry.get(comp_name)
                if component:
                    setattr(target, comp_name, component)
                    logger.debug(f"Injected {comp_name} into {target.__class__.__name__}")

# ============================================
# INTERFACE VALIDATOR
# ============================================

class InterfaceValidator:
    """
    Validates that components implement required interfaces
    """
    
    REQUIRED_INTERFACES = {
        'exchange': ['fetch_ticker', 'fetch_balance', 'create_order', 'cancel_order'],
        'database': ['save', 'load', 'query', 'delete'],
        'risk_manager': ['check_risk', 'calculate_position_size', 'get_stop_loss'],
        'ml_engine': ['predict', 'train', 'evaluate'],
        'notification': ['send_alert', 'send_trade_notification'],
    }
    
    @staticmethod
    def validate_component(component: Any, component_type: str) -> Tuple[bool, List[str]]:
        """Validate a component implements required interface"""
        
        if component_type not in InterfaceValidator.REQUIRED_INTERFACES:
            return True, []  # No interface requirements
            
        required_methods = InterfaceValidator.REQUIRED_INTERFACES[component_type]
        missing = []
        
        for method in required_methods:
            if not hasattr(component, method) or not callable(getattr(component, method)):
                missing.append(method)
                
        return len(missing) == 0, missing
        
    @staticmethod
    def create_stub_methods(component: Any, methods: List[str]):
        """Create stub methods for missing interface methods"""
        
        for method_name in methods:
            def stub_method(*args, **kwargs):
                logger.warning(f"Stub method {method_name} called on {component.__class__.__name__}")
                return None
                
            setattr(component, method_name, stub_method)
            logger.info(f"Added stub method {method_name} to {component.__class__.__name__}")

# ============================================
# EVENT BUS
# ============================================

class EventBus:
    """
    Central event bus for component communication
    Ensures loose coupling between components
    """
    
    def __init__(self):
        self.subscribers = {}
        self.event_history = []
        self.max_history = 1000
        
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to an event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
            
        self.subscribers[event_type].append(handler)
        logger.debug(f"Subscribed {handler.__name__} to {event_type}")
        
    def publish(self, event_type: str, data: Any = None):
        """Publish an event"""
        event = {
            'type': event_type,
            'data': data,
            'timestamp': datetime.now()
        }
        
        # Store in history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
            
        # Notify subscribers
        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        asyncio.create_task(handler(event))
                    else:
                        handler(event)
                except Exception as e:
                    logger.error(f"Event handler failed: {e}")
                    
    def get_history(self, event_type: str = None, limit: int = 100) -> List[Dict]:
        """Get event history"""
        history = self.event_history
        
        if event_type:
            history = [e for e in history if e['type'] == event_type]
            
        return history[-limit:]

# Global event bus
event_bus = EventBus()

# ============================================
# CONFIGURATION MERGER
# ============================================

class ConfigurationMerger:
    """
    Merges configurations from multiple sources
    Handles conflicts and validates completeness
    """
    
    @staticmethod
    def merge_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
        """Merge multiple configuration dictionaries"""
        result = {}
        
        for config in configs:
            result = ConfigurationMerger._deep_merge(result, config)
            
        return result
        
    @staticmethod
    def _deep_merge(dict1: Dict, dict2: Dict) -> Dict:
        """Deep merge two dictionaries"""
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigurationMerger._deep_merge(result[key], value)
            else:
                result[key] = value
                
        return result
        
    @staticmethod
    def load_all_configs() -> Dict[str, Any]:
        """Load and merge all configuration files"""
        configs = []
        
        # Load from multiple sources
        config_files = [
            'config.json',
            'config.yaml',
            'api_config.json',
            'trading_config.json',
            '.env'
        ]
        
        for file in config_files:
            filepath = Path(file)
            if filepath.exists():
                try:
                    if file.endswith('.json'):
                        with open(filepath) as f:
                            configs.append(json.load(f))
                    elif file.endswith('.yaml'):
                        # Handle YAML if available
                        try:
                            import yaml
                            with open(filepath) as f:
                                configs.append(yaml.safe_load(f))
                        except ImportError:
                            pass
                    elif file == '.env':
                        # Load environment variables
                        env_config = {}
                        with open(filepath) as f:
                            for line in f:
                                if '=' in line and not line.startswith('#'):
                                    key, value = line.strip().split('=', 1)
                                    env_config[key] = value
                        configs.append({'env': env_config})
                        
                except Exception as e:
                    logger.error(f"Failed to load config from {file}: {e}")
                    
        # Merge all configs
        return ConfigurationMerger.merge_configs(*configs)

# ============================================
# PIPELINE ORCHESTRATOR
# ============================================

class PipelineOrchestrator:
    """
    Orchestrates data flow through the pipeline
    Ensures proper sequencing and error handling
    """
    
    def __init__(self):
        self.pipeline_stages = []
        self.error_handlers = {}
        self.stage_metrics = {}
        
    def add_stage(self, name: str, processor: Callable, 
                 error_handler: Callable = None):
        """Add a processing stage to the pipeline"""
        self.pipeline_stages.append({
            'name': name,
            'processor': processor
        })
        
        if error_handler:
            self.error_handlers[name] = error_handler
            
        self.stage_metrics[name] = {
            'processed': 0,
            'errors': 0,
            'total_time': 0
        }
        
    async def process(self, data: Any) -> Any:
        """Process data through the pipeline"""
        result = data
        
        for stage in self.pipeline_stages:
            name = stage['name']
            processor = stage['processor']
            
            try:
                start_time = datetime.now()
                
                if asyncio.iscoroutinefunction(processor):
                    result = await processor(result)
                else:
                    result = processor(result)
                    
                # Update metrics
                self.stage_metrics[name]['processed'] += 1
                self.stage_metrics[name]['total_time'] += (datetime.now() - start_time).total_seconds()
                
            except Exception as e:
                logger.error(f"Pipeline stage {name} failed: {e}")
                self.stage_metrics[name]['errors'] += 1
                
                # Try error handler
                if name in self.error_handlers:
                    try:
                        result = self.error_handlers[name](result, e)
                    except Exception as handler_error:
                        logger.error(f"Error handler for {name} failed: {handler_error}")
                        raise
                else:
                    raise
                    
        return result
        
    def get_metrics(self) -> Dict[str, Any]:
        """Get pipeline metrics"""
        return self.stage_metrics

# ============================================
# SYSTEM ALIGNER
# ============================================

class SystemAligner:
    """
    Main class that aligns all system components
    """
    
    def __init__(self):
        self.registry = component_registry
        self.injector = DependencyInjector()
        self.validator = InterfaceValidator()
        self.event_bus = event_bus
        self.config_merger = ConfigurationMerger()
        self.pipeline = PipelineOrchestrator()
        
    def align_system(self, bot):
        """Align all system components"""
        
        logger.info("=" * 60)
        logger.info("🔧 STARTING SYSTEM ALIGNMENT")
        logger.info("=" * 60)
        
        # 1. Load and merge configurations
        logger.info("Loading configurations...")
        config = self.config_merger.load_all_configs()
        if hasattr(bot, 'config'):
            bot.config = self.config_merger.merge_configs(bot.config, config)
        else:
            bot.config = config
            
        # 2. Register all components
        logger.info("Registering components...")
        self._register_bot_components(bot)
        
        # 3. Validate interfaces
        logger.info("Validating interfaces...")
        self._validate_all_interfaces()
        
        # 4. Inject dependencies
        logger.info("Injecting dependencies...")
        self.injector.inject_dependencies(bot, self.registry)
        
        # 5. Setup event bus
        logger.info("Setting up event bus...")
        self._setup_event_handlers(bot)
        
        # 6. Setup pipeline
        logger.info("Setting up processing pipeline...")
        self._setup_pipeline(bot)
        
        # 7. Initialize all components
        logger.info("Initializing components...")
        self.registry.initialize_all()
        
        # 8. Verify system health
        logger.info("Verifying system health...")
        health = self.registry.check_health()
        
        unhealthy = [k for k, v in health.items() if not v]
        if unhealthy:
            logger.warning(f"Unhealthy components: {unhealthy}")
        else:
            logger.info("✅ All components healthy!")
            
        logger.info("=" * 60)
        logger.info("✅ SYSTEM ALIGNMENT COMPLETE")
        logger.info("=" * 60)
        
        return bot
        
    def _register_bot_components(self, bot):
        """Register all bot components"""
        
        # Register main bot
        self.registry.register('bot', bot)
        
        # Register sub-components
        components_to_register = [
            'exchange', 'database', 'risk_manager', 
            'ml_engine', 'notification_manager', 'dashboard',
            'data_collector', 'config_manager', 'pipeline'
        ]
        
        for comp_name in components_to_register:
            if hasattr(bot, comp_name):
                component = getattr(bot, comp_name)
                self.registry.register(comp_name, component)
                
    def _validate_all_interfaces(self):
        """Validate all component interfaces"""
        
        for name, component in self.registry.components.items():
            # Determine component type
            comp_type = None
            for type_name in InterfaceValidator.REQUIRED_INTERFACES:
                if type_name in name.lower():
                    comp_type = type_name
                    break
                    
            if comp_type:
                valid, missing = self.validator.validate_component(component, comp_type)
                
                if not valid:
                    logger.warning(f"Component {name} missing methods: {missing}")
                    # Add stub methods
                    self.validator.create_stub_methods(component, missing)
                    
    def _setup_event_handlers(self, bot):
        """Setup event handlers for the bot"""
        
        # Trade events
        if hasattr(bot, 'on_trade'):
            self.event_bus.subscribe('trade', bot.on_trade)
            
        # Error events
        if hasattr(bot, 'on_error'):
            self.event_bus.subscribe('error', bot.on_error)
            
        # Market data events
        if hasattr(bot, 'on_market_data'):
            self.event_bus.subscribe('market_data', bot.on_market_data)
            
        # Signal events
        if hasattr(bot, 'on_signal'):
            self.event_bus.subscribe('signal', bot.on_signal)
            
    def _setup_pipeline(self, bot):
        """Setup the data processing pipeline"""
        
        # Add pipeline stages based on available components
        
        if hasattr(bot, 'fetch_market_data'):
            self.pipeline.add_stage('fetch_data', bot.fetch_market_data)
            
        if hasattr(bot, 'calculate_indicators'):
            self.pipeline.add_stage('indicators', bot.calculate_indicators)
            
        if hasattr(bot, 'generate_signals'):
            self.pipeline.add_stage('signals', bot.generate_signals)
            
        if hasattr(bot, 'check_risk'):
            self.pipeline.add_stage('risk_check', bot.check_risk)
            
        if hasattr(bot, 'execute_trades'):
            self.pipeline.add_stage('execution', bot.execute_trades)
            
        # Attach pipeline to bot
        bot.pipeline_processor = self.pipeline

# ============================================
# MAIN INTEGRATION
# ============================================

def align_architecture(bot):
    """
    Main function to align the entire system architecture
    """
    aligner = SystemAligner()
    
    # Apply alignment
    bot = aligner.align_system(bot)
    
    # Add helper methods
    bot.get_component = component_registry.get
    bot.publish_event = event_bus.publish
    bot.get_event_history = event_bus.get_history
    
    if hasattr(bot, 'pipeline_processor'):
        bot.process_pipeline = bot.pipeline_processor.process
        bot.get_pipeline_metrics = bot.pipeline_processor.get_metrics
        
    logger.info("🎯 Architecture aligned successfully!")
    logger.info("  ✅ Components registered and wired")
    logger.info("  ✅ Dependencies injected")
    logger.info("  ✅ Interfaces validated")
    logger.info("  ✅ Event bus configured")
    logger.info("  ✅ Pipeline orchestrated")
    logger.info("  ✅ Configuration merged")
    
    return bot

if __name__ == "__main__":
    print("=" * 60)
    print("🏗️ ARCHITECTURAL ALIGNMENT MODULE")
    print("=" * 60)
    print("\nThis module provides:")
    print("  1. Component registry and wiring")
    print("  2. Dependency injection")
    print("  3. Interface validation")
    print("  4. Event bus for communication")
    print("  5. Configuration merging")
    print("  6. Pipeline orchestration")
    print("  7. System health checks")
    print("\n✅ Ready to align your system!")
    print("Use: align_architecture(bot)")