==================
Event StateMachine
==================


.. image:: https://img.shields.io/pypi/v/event_statemachine.svg
        :target: https://pypi.python.org/pypi/event_statemachine

.. image:: https://github.com/fedegonzalezit/event_statemachine/actions/workflows/python-app.yml/badge.svg?branch=develop
        :target: https://github.com/fedegonzalezit/event_statemachine/actions/workflows/python-app.yml?query=branch%3Adevelop

.. image:: https://readthedocs.org/projects/event-statemachine/badge/?version=latest
        :target: https://event-statemachine.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status




A simple event driven statemachine


* Free software: MIT license
* Documentation: https://event-statemachine.readthedocs.io.

Welcome to Event StateMachine. I always struggled to find a simple statemachine that could be used in a python project. So I decided to create my own, it's simple but useful.
The desing is based on transitions more than states, so you can define a transition from a state to another and the event that triggers it.

Getting started
--------

To install Event StateMachine, run this command in your terminal:

.. code-block:: console

    $ pip install event_statemachine

Let's implement this simple turnstile example:

.. image:: https://raw.githubusercontent.com/fedegonzalezit/event_statemachine/[branch]/docs/_static/turnstile.jpg
    :alt: Turnstile example

Define your state machine:

.. code-block:: python

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


Initialize your state machine:

.. code-block:: python

    turnstile = Turnstile(initial_state="Locked")

Send events to your state machine:

.. code-block:: python

    evt = {"action": "push"}
    sm.run_state(evt)  # Do nothing

    evt = {"action": "coin", "coin": "invalid"}
    sm.run_state(evt)  # Print: Invalid coin, try again

    evt = {"action": "coin", "coin": "valid"}
    sm.run_state(evt)  # Print: Unlocking turnstile

    evt = {"action": "coin", "coin": "valid"}
    sm.run_state(evt)  # Print: turnstile already unlocked, returning coin

    evt = {"action": "push"}
    sm.run_state(evt)  # Print: Locking turnstile

Features
--------

- Define your transitions using @transition decorator
- Each transition can have a condition to be executed using @event_condition decorator.
- You can get the context of the state maching using the method get_context() and load it using the method set_context(). This allows you to use an stateless architecture and save the context of the state machine in a database.
- You can override the methods on_entry and on_exit in the SM. This code will be executed always at the beginning and at the end of each transition respectively.
- Using the decorators @on_state_entry and @on_state_exit you can archieve the same as the previous point but for each state.
