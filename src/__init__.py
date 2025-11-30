"""
Travel Assistant - Modular Application
A comprehensive travel planning assistant for elderly travelers.
"""

__version__ = "2.0.0"
__author__ = "Travel Assistant Team"

# Import main components for easy access
from .config.config import *
from .api.openai_client import *
from .utils.helpers import *
from .core.travel_functions import *
from .data.processors import *
from .ui.components import *
from .main import create_app, main