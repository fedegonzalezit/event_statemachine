#!/usr/bin/env python

"""Tests for `event_statemachine` package."""

import pytest

from event_statemachine import (
    StateMachine,
    transition,
    on_state_entry,
    on_state_exit,
    event_condition,
)


@pytest.fixture
def sm_class():
    class TestStateMachine(StateMachine):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.context.my_var = 0
            self.context.on_entry = False
            self.context.on_exit = False
            self.on_entrystate_executed = False
            self.on_exitstate_executed = False

        def on_entry(self):
            self.context.on_entry = True

        def on_exit(self):
            self.context.on_exit = True

        @transition("Initial -> State1")
        def on_event1(self):
            self.context.my_var = 1

        @transition("State1 -> State2")
        def on_event2(self):
            self.context.my_var = 2

        @transition("State2 -> State3a")
        @event_condition(lambda self: self.evt.get("next_state") == "State3a")
        def on_event3a(self):
            self.context.my_var = 3

        @transition("State2 -> State3b")
        @event_condition(lambda self: self.evt.get("next_state") == "State3b")
        def on_event3b(self):
            self.context.my_var = 4

        @on_state_entry("StateEntry")
        def on_entry_state(self):
            self.on_entrystate_executed = True

        @on_state_exit("StateEntry")
        def on_exit_state(self):
            self.on_exitstate_executed = True

        @transition("StateEntry -> StateEntry")
        @event_condition(lambda self: self.evt.get("next_state") == "StateEntry")
        def on_stateentry(self):
            self.context.my_var = 5

    return TestStateMachine


def test_transition(sm_class):
    sm = sm_class()
    assert sm.current_state == "Initial"
    sm.run_state()
    assert sm.current_state == "State1"
    sm.run_state()
    assert sm.current_state == "State2"


def test_initial_state(sm_class):
    sm = sm_class(initial_state="State1")
    assert sm.current_state == "State1"
    sm.run_state()
    assert sm.current_state == "State2"


def test_context(sm_class):
    sm = sm_class()
    assert sm.context.my_var == 0
    sm.run_state()
    assert sm.context.my_var == 1


def test_load_context(sm_class):
    sm = sm_class()
    sm.run_state()
    context = sm.get_context()
    sm2 = sm_class(initial_state=sm.current_state)
    sm2.set_context(context)
    assert sm2.context.my_var == 1
    assert sm2.current_state == "State1"


def test_on_exit_on_exit(sm_class):
    sm = sm_class()
    assert sm.context.on_entry is False
    assert sm.context.on_exit is False
    sm.run_state()
    assert sm.context.on_entry is True
    assert sm.context.on_exit is True


def test_event_condition(sm_class):
    sm = sm_class(initial_state="State2")
    event = {"next_state": "State3a"}
    sm.run_state(event)
    assert sm.current_state == "State3a"

    sm = sm_class(initial_state="State2")
    event = {"next_state": "State3b"}
    sm.run_state(event)
    assert sm.current_state == "State3b"


def test_invalid_event(sm_class):
    sm = sm_class(initial_state="State2")
    event = {"no_key": "no_value"}
    sm.run_state(event)
    assert sm.current_state == "State2"


def test_state_on_entry(sm_class):
    sm = sm_class(initial_state="StateEntry")
    assert sm.on_entrystate_executed is False
    sm.run_state()
    assert sm.on_entrystate_executed is False

    event = {"next_state": "StateEntry"}
    sm.run_state(event)
    assert sm.on_entrystate_executed is True


def test_state_on_exit(sm_class):
    sm = sm_class(initial_state="StateEntry")
    assert sm.on_exitstate_executed is False
    sm.run_state()
    assert sm.on_exitstate_executed is False

    event = {"next_state": "StateEntry"}
    sm.run_state(event)
    assert sm.on_exitstate_executed is True
