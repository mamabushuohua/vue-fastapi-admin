from abc import ABC, abstractmethod


class BaseCommand(ABC):
    """
    Abstract base class for custom commands.
    """

    help = ""  # Command description

    def __init__(self, app):
        self.app = app

    def add_arguments(self, parser):
        """
        Add custom arguments to the command.
        This method can be overridden by subclasses.
        """
        pass

    @abstractmethod
    def handle(self, *args, **options):
        """
        The actual logic of the command.
        """
        pass
