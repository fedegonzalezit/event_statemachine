"""Main module."""
import logging

logger = logging.getLogger(__name__)


class Context:
    def __init__(self):
        self._data = {}

    def __getattr__(self, key):
        if key in self._data:
            return self._data[key]
        raise AttributeError(f"Key '{key}' does not exist.")

    def __setattr__(self, key, value):
        if key == "_data":
            super().__setattr__(key, value)
        else:
            self._data[key] = value

    def to_dict(self):
        return self._data

    def from_dict(self, data):
        self._data.update(data)

    def __eq__(self, __value: object) -> bool:
        return self._data == __value._data


class HandlerMeta(type):
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        cls.transitions = {}
        cls.on_entries = {}
        cls.on_exits = {}
        for name, value in dct.items():
            if hasattr(value, "state"):
                next_state = {
                    "next_state": value.next_state,
                    "handler": value,
                }
                if hasattr(value, "event_condition"):
                    next_state["event_condition"] = value.event_condition
                next_states = cls.transitions.get(value.state, [])
                next_states.append(next_state)
                cls.transitions[value.state] = next_states
            if hasattr(value, "on_entry"):
                cls.on_entries[value.on_entry] = value
            if hasattr(value, "on_exit"):
                cls.on_exits[value.on_exit] = value


class StateMachine(metaclass=HandlerMeta):
    def __init__(self, *args, **kwargs):
        if self.transitions is None:
            raise ValueError("No se encontraron transiciones")
        self.current_state = kwargs.pop("initial_state", "Initial")
        self.evt = {}
        self.context = Context()

    def get_context(self):
        custom_context = self.on_get_context()
        self.context._data.update(custom_context)
        context = self.context.to_dict()
        return context

    def set_context(self, context):
        new_context = self.on_set_context(context)
        self.context.from_dict(new_context)

    def on_entry(self):
        pass

    def on_exit(self):
        pass

    def on_get_context(self):
        return {}

    def on_set_context(self, context):
        return context

    def on_return(self):
        return {}

    def run_state(self, event=None):
        self.evt = event or {}
        logger.debug("Current state: %s", self.current_state)
        logger.debug("Receive event: %s", self.evt)
        self.on_entry()
        current_transitions = self.transitions.get(self.current_state, [])
        any_transitions = self.transitions.get("Any", [])
        current_transitions.extend(any_transitions)
        for transition in current_transitions:
            if self.__exec_transition(transition):
                if self.on_entries.get(self.current_state):
                    logger.debug("Executing on_entry for %s", self.current_state)
                    entry_func = self.on_entries[self.current_state]
                    entry_func(self)
                logger.debug("Executing transition %s", transition)
                handler = transition["handler"]
                alternative_next_state = handler(self)
                if self.on_exits.get(self.current_state):
                    logger.debug("Executing on_exit for %s", self.current_state)
                    exit_func = self.on_exits[self.current_state]
                    exit_func(self)
                if alternative_next_state:
                    valid_next_states = transition["next_state"].split(",")
                    if alternative_next_state not in valid_next_states:
                        raise ValueError(
                            f"El estado {alternative_next_state} no es válido"
                        )
                    else:
                        self.current_state = alternative_next_state
                else:
                    self.current_state = transition["next_state"]
                break
        self.on_exit()
        return self.on_return()

    def __exec_transition(self, transition):
        event_condition = transition.get("event_condition")
        if event_condition is None:
            return True
        parameter_names = event_condition.__code__.co_varnames
        if "self" in parameter_names:
            return event_condition(self)
        else:
            raise ValueError(
                f"La transición {transition.__name__} no tiene los parámetros requeridos"
            )
