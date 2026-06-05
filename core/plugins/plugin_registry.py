from typing import Dict, List, Optional
from core.plugins.plugin_base import Plugin
from config.logger import setup_logger

logger = setup_logger("core.plugins.plugin_registry")

class PluginRegistry:
    def __init__(self):
        self._plugins: Dict[str, Plugin] = {}

    def register(self, plugin: Plugin) -> bool:
        name = plugin.metadata.name
        if name in self._plugins:
            logger.warning(f"Plugin {name} is already registered. Overwriting.")
        
        self._plugins[name] = plugin
        logger.info(f"Successfully registered plugin: {name} (v{plugin.metadata.version})")
        return True

    def get_plugin(self, name: str) -> Optional[Plugin]:
        return self._plugins.get(name)

    def get_all_plugins(self) -> List[Plugin]:
        return list(self._plugins.values())

    def remove_plugin(self, name: str) -> bool:
        if name in self._plugins:
            del self._plugins[name]
            logger.info(f"Unregistered plugin: {name}")
            return True
        return False
