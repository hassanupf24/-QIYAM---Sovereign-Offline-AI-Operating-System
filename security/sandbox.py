import docker
from typing import Tuple
from config.logger import setup_logger

logger = setup_logger("security.sandbox")

class Sandbox:
    def __init__(self):
        try:
            self.client = docker.from_env()
            logger.info("Docker SDK initialized for secure sandboxing.")
        except Exception as e:
            logger.error(f"Failed to initialize Docker SDK: {e}")
            self.client = None
            
        self.container_image = "python:3.11-alpine"

    def execute_command(self, command: str, human_approved: bool = False) -> Tuple[bool, str]:
        """
        Executes a command safely inside an isolated, network-disabled Docker container.
        """
        if not self.client:
            return False, "Error: Sandbox environment is not available."

        logger.info(f"Executing sandboxed command: {command}")
        try:
            # Run command in a restricted container
            # Using sh -c to execute the passed command string
            container = self.client.containers.run(
                self.container_image,
                command=f"sh -c '{command}'",
                detach=False,
                remove=True,
                network_mode="none", # Completely disable networking
                mem_limit="128m",    # Restrict memory
                cpu_quota=50000,     # Restrict CPU
                user="nobody"        # Run as unprivileged user
            )
            
            # The run method returns the logs directly when detach=False
            output = container.decode('utf-8')
            return True, output
            
        except docker.errors.ContainerError as e:
            # Command failed
            return False, f"Command Error: {e.stderr.decode('utf-8') if e.stderr else str(e)}"
        except docker.errors.ImageNotFound:
            return False, f"Error: Sandbox image {self.container_image} not found."
        except Exception as e:
            return False, f"Sandbox Error: {str(e)}"
