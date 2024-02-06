import pytest
from metadata.core.domain.app import AppId
from metadata.core.domain.common import EntityError
from metadata.core.domain.event import CommonEvent, Event
from metadata.core.domain.schema import ParameterType, Schema, SchemaParameter

@pytest.mark.parametrize("event_name", [
    ("event"),
    ("eve_nt"),("event_ctx"),("context_ctx"),
    ("eve1nt"),("event1"),

])
def test_create_event_with_legal_names(event_name):
    Event.create_game_specific(AppId('newapp'), event_name)


@pytest.mark.parametrize("event_name", [
    (""), (" "), ("_"),
    ("_event"),("event_"),("ev__ent"),
    (" event"),("eve nt"),
    ("eve-nt"),
    ("1event"),
    ("event!"),("event?"),("event,"),("event."),
    ("ctx_event"),("event_context"),
    ("event"*50),
    ("Event"),
    ("e\nvent"),("e\tvent"),
    ("eve'nt"),('eve"nt')
])
def test_create_event_with_illegal_names(event_name):
    with pytest.raises(EntityError):
        Event.create_game_specific(AppId('newapp'), event_name)


@pytest.mark.parametrize("parameters", [
    ([""]), ([" "]), (["_"]),
    ("_param"),("param_"),("pa__ram"),
    (" param"),("par am"),
    ("par-am"),
    ("1param"),
    ("param!"),("param?"),("param,"),("param."),
    ("custom_param"),
    ("param"*50),
    ("Param"),
    ("par\nam"),("par\tam"),
    ("par'am"),('par"am'),
    (['param1', 'param1']),

])
def test_add_illegal_parameters_to_empty_event(parameters):
    event = Event.create_game_specific(AppId('newapp'), "event")
    with pytest.raises(EntityError):
        event.add_parameters([SchemaParameter(
            name=name,
            type=ParameterType.STRING,
            introduced_at_version=0
        ) for name in parameters])


@pytest.mark.parametrize("parameters", [
    ([]),
    (['param']),
    (['param1']),
    (['par_am']),
    (['param1', 'param2']),

])
def test_add_legal_parameters_to_empty_event(parameters):
    event = Event.create_game_specific(AppId('newapp'), "event")
    event.add_parameters([SchemaParameter(
        name=name,
        type=ParameterType.STRING,
        introduced_at_version=0
    ) for name in parameters])
    assert [p.name for p in event.get_schema().parameters] == parameters


def test_add_legal_parameters_to_existing_event():
    event = Event.create_game_specific(AppId('newapp'), "event")
    event.add_parameters([SchemaParameter(
        name='param',
        type=ParameterType.STRING,
        introduced_at_version=0
    )])
    event.schema.id = 1 # simulate save
    event.add_parameters([SchemaParameter(
        name='param1',
        type=ParameterType.STRING,
        introduced_at_version=1
    )])
    assert [p.name for p in event.schema.parameters] == ['param', 'param1']


def test_add_legal_parameters_to_existing_event_without_parameters():
    event = Event.create_game_specific(AppId('newapp'), "event")
    event.schema.id = 1 # simulate save
    event.add_parameters([SchemaParameter(
        name='param',
        type=ParameterType.STRING,
        introduced_at_version=1
    )])
    assert [p.name for p in event.get_schema().parameters] == ['param']


def test_try_to_add_existing_parameter():
    event = Event.create_game_specific(AppId('newapp'), "event")
    event.add_parameters([SchemaParameter(
        name='param',
        type=ParameterType.STRING,
        introduced_at_version=0
    )])
    event.schema.id = 1 # simulate save
    with pytest.raises(EntityError):
        event.add_parameters([SchemaParameter(
            name='param',
            type=ParameterType.STRING,
            introduced_at_version=1
        )])


def test_add_parameter_to_event_with_parent_common_event_without_mandatory_prefix():
    event = Event.create_game_specific(AppId('newapp'), "event")
    event.parent_common_event = CommonEvent(schema=Schema(
        parameters=[SchemaParameter(name='common_param', type=ParameterType.STRING, introduced_at_version=0)],
        vendor='',
        name='event'
    ))
    event.parent_common_event_version = 0
    with pytest.raises(EntityError):
        event.add_parameters([SchemaParameter(
            name='param',
            type=ParameterType.STRING,
            introduced_at_version=1
        )])


def test_add_parameter_to_event_with_parent_common_event_with_mandatory_prefix():
    event = Event.create_game_specific(AppId('newapp'), "event")
    event.parent_common_event = CommonEvent(schema=Schema(
        parameters=[SchemaParameter(name='common_param', type=ParameterType.STRING, introduced_at_version=0)],
        vendor='',
        name='event'
    ))
    event.parent_common_event_version = 0
    event.add_parameters([SchemaParameter(
        name='custom_param',
        type=ParameterType.STRING,
        introduced_at_version=0
    )])
    assert [p.name for p in event.get_schema().parameters] == ['common_param', 'custom_param']
