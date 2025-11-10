"""Base integration class for external services."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time


class BaseIntegration(ABC):
    """Base class for all integrations."""

    def __init__(self, name: str) -> None:
        """Initialize base integration.

        Args:
            name: Integration name
        """
        self.name = name
        self.enabled = True
        self.last_sync_time: Optional[float] = None
        self.error_count = 0
        self.max_errors = 3

    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the service.

        Returns:
            True if authentication successful
        """
        pass

    @abstractmethod
    def sync(self) -> Dict[str, Any]:
        """Sync data from the service.

        Returns:
            Dictionary with sync results
        """
        pass

    def handle_error(self, error: Exception) -> None:
        """Handle errors with exponential backoff.

        Args:
            error: Exception that occurred
        """
        self.error_count += 1
        if self.error_count >= self.max_errors:
            self.enabled = False
            print(f"Integration {self.name} disabled after {self.max_errors} errors")
        else:
            wait_time = 2 ** self.error_count
            print(f"Error in {self.name}: {error}. Retrying in {wait_time}s...")
            time.sleep(wait_time)

    def reset_error_count(self) -> None:
        """Reset error count after successful operation."""
        self.error_count = 0

    def is_healthy(self) -> bool:
        """Check if integration is healthy.

        Returns:
            True if integration is enabled and healthy
        """
        return self.enabled and self.error_count < self.max_errors

