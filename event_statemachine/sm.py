"""Main module."""
import logging
from typing import Any, Callable, Optional

from event_statemachine.handler import HandlerMeta
from event_statemachine.context import Context

logger = logging.getLogger(__name__)


def transition(transition_name: str) -> Callable:
    """Decorator to define a transition.

    It is used in the following way:

    .. code-block:: python

        @transition("StateFrom -> StateTo")
        def handler_function(self):
            pass


    The states are defined as strings separated by a ``->`` symbol.

    Args:
        transition_name (str): Transition ``from -> to``.
    """

    def decorator(func):
        state, next_state = transition_name.replace(" ", "").split("->")
        func.state = state
        func.next_state = next_state
        return func

    return decorator


def event_condition(condition: Callable) -> Callable:
    """Decorator to define a condition for an event.
    The condition is a funtion that receives `self` from the state machine.
    It's use to control the flow of the state machine, and validate the
    event that is received.

    It is used in the following way:

    .. code-block:: python

        @transition("StateFrom -> StateTo")
        @event_condition(lambda self: self.evt.get("condition") == "expected_value")
        def handler_function(self):
            pass


    Args:
        condition (Callable): a function that receives `self` from the state machine
        and returns a boolean.
    """

    def decorator(func):
        func.event_condition = condition
        return func

    return decorator


def on_state_entry(state: str) -> Callable:
    """Decorator to define a function that is executed when an event is received
    in a specific state.

    It is used in the following way:

    .. code-block:: python

        @on_state_entry("State")
        def handler_function(self):
            # allways executed when an event is received in the state "State"
            pass


    Args:
        state (str): state name.
    """

    def decorator(func):
        func.on_entry = state
        return func

    return decorator


def on_state_exit(state: str) -> Callable:
    """Decorator to define a function that is executed when an event is received
    after executing some state.

    It is used in the following way:

    .. code-block:: python

        @on_state_exit("State")
        def handler_function(self):
            # allways executed after handling an event in the state "State"
            pass


    Args:
        state (str): state name.
    """

    def decorator(func):
        func.on_exit = state
        return func

    return decorator


class StateMachine(metaclass=HandlerMeta):
    """Base class for a state machine.

    Args:
        initial_state (str, optional): Initial state of the state machine. Defaults to "Initial".
    """

    def __init__(self, initial_state: Optional[str] = "Initial"):
        if self.transitions is None:
            raise ValueError("No se encontraron transiciones")
        self.current_state = initial_state
        self.evt = {}
        self.context = Context()

    def get_context(self) -> dict:
        """Obtain the context of the state machine.

        Returns:
            dict: context of the state machine
        """
        custom_context = self.on_get_context()
        self.context._data.update(custom_context)
        context = self.context.to_dict()
        return context

    def set_context(self, context: dict) -> None:
        """Set the context of the state machine.

        Args:
            context (dict): context of the state machine obtained from ``get_context()``
        """
        new_context = self.on_set_context(context)
        self.context.from_dict(new_context)

    def on_entry(self) -> None:
        """Hook to execute code when an event is received in the state machine,
        doesn't matter if the event is handled or not.
        """

    def on_exit(self) -> None:
        """Hook to execute code after an event is received in the state machine,
        doesn't matter if the event was handled or not.
        """

    def on_get_context(self) -> dict:
        """Hook to perform custom actions when the context is obtained.

        Returns:
            dict: new values for the context
        """
        return {}

    def on_set_context(self, context: dict) -> dict:
        """Hook to perform custom actions when the context is set.

        Args:
            context (dict): the received context

        Returns:
            dict: a modified context
        """
        return context

    def on_return(self) -> Any:
        """Hook to return a value after executing the state machine.

        Returns:
            Any: custom value to return
        """

    def run_state(self, event: Optional[Any] = None) -> Any:
        """Method to run the state machine.

        Args:
            event (Optional[Any], optional): The data of the event. Defaults to None.

        Returns:
            Any: The value returned by the ``on_return`` hook.
        """
        self.evt = event or {}
        logger.debug("Current state: %s", self.current_state)
        logger.debug("Receive event: %s", self.evt)
        self.on_entry()

        valid_transition = self.__get_transition_for_state(self.current_state)
        if valid_transition:
            handler = valid_transition["handler"]
            self.__run_on_entry_handler(self.current_state)
            logger.debug("Executing transition %s", transition)
            alternative_next_state = handler(self)
            self.__run_on_exit_handler(self.current_state)

            self.current_state = self.__get_next_state(
                valid_transition, alternative_next_state
            )
        self.on_exit()
        return self.on_return()

    def __valid_transition_condition(self, transition):
        condition = transition.get("event_condition")
        if condition is None:
            return True
        parameter_names = condition.__code__.co_varnames
        if "self" in parameter_names:
            return condition(self)
        else:
            raise ValueError(
                f"La transición {transition.__name__} no tiene los parámetros requeridos"
            )

    def __get_transition_for_state(self, state: str) -> Optional[dict]:
        current_transitions = self.transitions.get(state, [])
        any_transitions = self.transitions.get("Any", [])
        current_transitions.extend(any_transitions)
        for state_transition in current_transitions:
            if self.__valid_transition_condition(state_transition):
                return state_transition
        return None

    def __run_on_entry_handler(self, state: str) -> None:
        if self.on_entries.get(state):
            logger.debug("Executing on_entry for %s", state)
            entry_func = self.on_entries[state]
            entry_func(self)

    def __run_on_exit_handler(self, state: str) -> None:
        if self.on_exits.get(state):
            logger.debug("Executing on_exit for %s", state)
            exit_func = self.on_exits[state]
            exit_func(self)

    def __get_next_state(self, transition: dict, alternative_next_state: str) -> str:
        if alternative_next_state:
            valid_next_states = transition["next_state"].split(",")
            if alternative_next_state not in valid_next_states:
                raise ValueError(f"El estado {alternative_next_state} no es válido")
            else:
                return alternative_next_state
        else:
            return transition["next_state"]
