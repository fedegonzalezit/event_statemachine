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
