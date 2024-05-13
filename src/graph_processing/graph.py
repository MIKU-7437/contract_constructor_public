import uuid
import operator
from copy import deepcopy
from typing import Callable


from graph_processing.graph_schemas import GrafInputDTO
from shared.error_structure import Error


class Graph:
    """Performs graph calculations and updates the state of nodes (not presented in public version)"""
