from event_statemachine import StateMachine
from event_statemachine import transition
from event_statemachine import event_condition


class Turnstile(StateMachine):
    @transition("Locked -> Unlocked")
    @event_condition(
        lambda self: self.evt.get("action") == "coin"
        and self.evt.get("coin") == "valid"
    )
    def on_coin(self):
        print("Unlocking turnstile")

    @transition("Locked -> Locked")
    @event_condition(
        lambda self: self.evt.get("action") == "coin"
        and self.evt.get("coin") == "invalid"
    )
    def on_coin_invalid(self):
        print("Invalid coin, try again")

    @transition("Unlocked -> Unlocked")
    @event_condition(lambda self: self.evt.get("action") == "coin")
    def on_unlocked_coin(self):
        print("turnstile already unlocked, returning coin")

    @transition("Unlocked -> Locked")
    @event_condition(lambda self: self.evt.get("action") == "push")
    def on_push(self):
        print("Locking turnstile")


sm = Turnstile(initial_state="Locked")
evt = {"action": "push"}
sm.run_state(evt)
evt = {"action": "coin", "coin": "invalid"}
sm.run_state(evt)
evt = {"action": "coin", "coin": "valid"}
sm.run_state(evt)
evt = {"action": "coin", "coin": "valid"}
sm.run_state(evt)
evt = {"action": "push"}
sm.run_state(evt)
