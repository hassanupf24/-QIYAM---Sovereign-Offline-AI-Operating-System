import importlib
import inspect
import os
import sys
from typing import List
from core.plugins.plugin_base import Plugin
from core.plugins.plugin_registry import PluginRegistry
from core.plugins.permission_manager import PermissionManager
from config.logger import setup_logger

logger = setup_logger("core.plugins.plugin_loader")

class PluginLoader:
    def __init__(self, registry: PluginRegistry, permission_manager: PermissionManager, plugins_dir: str = "plugins"):
        self.registry = registry
        self.permission_manager = permission_manager
        
        # Absolute path to plugins directory
        # Assuming QIYAM root is one level up from core
        self.plugins_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", plugins_dir))
        
        if self.plugins_dir not in sys.path:
            sys.path.insert(0, self.plugins_dir)

    def discover_and_load(self) -> int:
        """Scans the plugins directory and dynamically loads valid plugins."""
        if not os.path.exists(self.plugins_dir):
            logger.warning(f"Plugins directory not found at {self.plugins_dir}. Creating it.")
            os.makedirs(self.plugins_dir, exist_ok=True)
            return 0

        loaded_count = 0
        
        for filename in os.listdir(self.plugins_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                try:
                    # Dynamically import the module
                    module = importlib.import_module(module_name)
                    
                    # Hot-reload support (reload if already loaded previously)
                    importlib.reload(module)
                    
                    # Find classes that inherit from Plugin but are not the base class itself
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, Plugin) and obj is not Plugin:
                            plugin_instance = obj()
                            
                            # Validate Permissions before registering
                            if self.permission_manager.validate_permissions(
                                plugin_instance.required_permissions, 
                                plugin_instance.metadata.name
                            ):
                                self.registry.register(plugin_instance)
                                loaded_count += 1
                            else:
                                logger.error(f"Plugin {plugin_instance.metadata.name} failed security validation. Blocked.")
                                
                except Exception as e:
                    logger.error(f"Failed to load plugin module {module_name}: {str(e)}")
                    # System continues running even if a plugin crashes during load
                    continue
                    
        logger.info(f"Plugin discovery complete. Loaded {loaded_count} plugins.")
        return loaded_count
