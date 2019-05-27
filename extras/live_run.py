"""
Run some simple test on an actual cachet setup.
This can be set up locally with docker fairly quickly.

Set the following enviroment variables before running the script:

- CACHET_ENDPOINT (eg: http://test.example.com/api/v1)
- CACHET_API_TOKEN (eg. Wohc7eeGhaewae7zie1E)
"""
import os
from datetime import datetime
from pprint import pprint

import cachetclient
from cachetclient.v1.client import Client
from cachetclient.v1 import enums

CACHET_ENDPOINT = os.environ.get('CACHET_ENDPOINT')
CACHET_API_TOKEN = os.environ.get('CACHET_API_TOKEN')
CLIENT = None


def client() -> Client:
    global CLIENT
    if CLIENT is None:
        CLIENT = cachetclient.Client(endpoint=CACHET_ENDPOINT, api_token=CACHET_API_TOKEN)

    return CLIENT


def main():
    if CACHET_ENDPOINT is None:
        raise ValueError("CACHET_ENDPOINT enviroment variable missing")

    if CACHET_API_TOKEN is None:
        raise ValueError("CACHET_API_TOKEN enviroment variable missing")

    test_ping()
    test_version()
    test_components()
    test_component_groups()
    test_subscribers()
    test_incidents()
    test_issue_updates()
    test_metrics()
    test_metric_points()

    # test_schedules()


def test_ping():
    result = client().ping()
    if result is not True:
        raise ValueError("Ping failed. {} ({}) returned instead of True (bool)".format(result, type(result)))


def test_version():
    version = client().version()
    if version.value is not str and len(version.value) < 3:
        raise ValueError("Version value string suspicious? '{}'".format(version.value))

    print("Version   :", version.value)
    print("on_latest :", version.on_latest)
    print("latest    :", version.latest)


def test_components():
    comp = client().components.create(
        "Test Component",
        enums.COMPONENT_STATUS_OPERATIONAL,
        description="This is a test",
        tags="test, thing",
        order=1,
        group_id=1,
    )
    pprint(comp.attrs, indent=2)
    assert comp.status == enums.COMPONENT_STATUS_OPERATIONAL
    assert isinstance(comp.created_at, datetime)
    assert isinstance(comp.updated_at, datetime)

    # Create component using properties
    comp.name = 'Test Thing'
    comp.status = enums.COMPONENT_STATUS_MAJOR_OUTAGE
    comp.link = 'http://status.example.com'
    comp.order = 10
    comp.group_id = 1000
    comp.enabled = False
    comp.tags = {'moo', 'boo'}
    comp = comp.update()

    # Test if values are correctly updates
    assert comp.name == 'Test Thing'
    assert comp.description == 'This is a test'
    assert comp.status == enums.COMPONENT_STATUS_MAJOR_OUTAGE
    assert comp.link == 'http://status.example.com'
    assert comp.order == 10
    assert comp.group_id == 1000
    assert comp.enabled is False
    assert comp.tags == {'moo', 'boo'}

    # Call update directly on the manager
    comp = client().components.update(
        comp.id,
        status=enums.COMPONENT_STATUS_OPERATIONAL,
        name="A new component name",
        tags={'bolle', 'kake'}
    )
    assert comp.name == "A new component name"
    assert comp.description == 'This is a test'
    assert comp.status == enums.COMPONENT_STATUS_OPERATIONAL
    assert comp.link == 'http://status.example.com'
    assert comp.order == 10
    assert comp.group_id == 1000
    assert comp.enabled is False
    assert comp.tags == {'bolle', 'kake'}
    comp.delete()


def test_component_groups():
    grp = client().component_groups.create("Test Group", order=1)
    assert grp.id > 0
    assert grp.name == "Test Group"
    assert grp.order == 1
    assert grp.is_collapsed is False
    assert grp.is_open is True
    assert grp.is_operational is True

    # Re-fetch by id
    grp = client().component_groups.get(grp.id)

    # Update group
    grp.order = 2
    grp.name = "Global Services"
    grp.collapsed = enums.COMPONENT_GROUP_COLLAPSED_TRUE
    assert grp.id > 0
    assert grp.name == "Global Services"
    assert grp.order == 2
    assert grp.is_collapsed is True
    assert grp.is_open is False
    assert grp.is_operational is True

    pprint(grp.attrs, indent=2)
    grp.delete()


def test_subscribers():
    new_sub = client().subscribers.create('einar2@zetta.io')

    assert isinstance(new_sub.created_at, datetime)
    assert isinstance(new_sub.updated_at, datetime)
    assert isinstance(new_sub.verified_at, datetime)

    # Rought subscriber count check
    count = client().subscribers.count()
    if count == 0:
        raise ValueError("Subscriber count is 0")

    # Iterate subscribers
    for sub in client().subscribers.list():
        print(sub)

    # Delete subscriber and recount
    new_sub.delete()
    count_pre = client().subscribers.count()
    if count != count_pre + 1:
        raise ValueError("subscriber count {} != {}".format(count, count_pre))


def test_incidents():
    issue = client().incidents.create(
        "Something blew up!",
        "We are looking into it",
        enums.INCIDENT_INVESTIGATING,
        visible=True,
        component_id=1,
        component_status=enums.COMPONENT_STATUS_MAJOR_OUTAGE,
    )
    pprint(issue.attrs)
    issue.delete()


def test_issue_updates():
    pass


# def test_schedules():
#     sch = client().schedules.create("Test Schedule", "Shits gonna happen", None)
#     pprint(sch.attrs, indent=2)


def test_metrics():
    pass


def test_metric_points():
    pass


if __name__ == '__main__':
    main()
