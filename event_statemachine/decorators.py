def transition(transition_name, event_condition=None):
    def decorator(func):
        state, next_state = transition_name.replace(" ", "").split("->")
        func.state = state
        func.next_state = next_state
        if event_condition:
            func.event_condition = event_condition
        return func

    return decorator


def event_condition(condition):
    def decorator(func):
        func.event_condition = condition
        return func

    return decorator


def on_state_entry(state):
    def decorator(func):
        func.on_entry = state
        return func

    return decorator


def on_state_exit(state):
    def decorator(func):
        func.on_exit = state
        return func

    return decorator
