from datetime import datetime
from typing import List, Generator

from cachetclient.base import Manager, Resource
from cachetclient import utils
from cachetclient.v1.incident_updates import IncidentUpdatesManager
from cachetclient.httpclient import HttpClient


class Incident(Resource):

    @property
    def id(self) -> int:
        """int: unique id of the incident"""
        return self.get('id')

    @property
    def component_id(self) -> int:
        """int: Get or set component id for this incident"""
        return self.get('component_id')

    @component_id.setter
    def component_id(self, value: int):
        self._data['component_id'] = value

    @property
    def name(self) -> str:
        """str: Get or set name/title of the incident"""
        return self.get('name')

    @name.setter
    def name(self, value: str):
        self._data['name'] = value

    @property
    def message(self) -> str:
        """str: Get or set message"""
        return self.get('message')

    @message.setter
    def message(self, value: str):
        self._data['message'] = value

    @property
    def notify(self) -> str:
        """bool: Get or set notification flag"""
        return self.get('notify')

    @notify.setter
    def notify(self, value: bool):
        self._data['notify'] = value

    @property
    def status(self) -> int:
        """int: Get or set status. See :py:data:`enums`"""
        return self.get('status')

    @status.setter
    def status(self, value: int):
        self._data['status'] = value

    @property
    def human_status(self) -> str:
        """str: Human representation of the status"""
        return self.get('human_status')

    @property
    def visible(self) -> int:
        """bool: Get or set visibility of the indcinent"""
        return self.get('visible') == 1

    @visible.setter
    def visible(self, value: bool):
        self._data['visible'] = value

    @property
    def scheduled_at(self) -> datetime:
        """datetime: Scheduled time. This is used for scheduled events
        like maintenance in Cachet 2.3 were incident status is ``INCIDENT_SCHEDULED``.
        2.4 has its own schedule resource and endpoints.
        """
        return utils.to_datetime(self.get('scheduled_at'))

    @property
    def created_at(self) -> datetime:
        """datetime: When the issue was created"""
        return utils.to_datetime(self.get('created_at'))

    @property
    def updated_at(self) -> datetime:
        """datetime: Last time the issue was updated"""
        return utils.to_datetime(self.get('updated_at'))

    @property
    def deleted_at(self) -> datetime:
        """datetime: When the issue was deleted"""
        return utils.to_datetime(self.get('deleted_at'))

    def updates(self) -> Generator['Incident', None, None]:
        """Generator['Incident', None, None]: Incident updates for this issue"""
        return self._manager.updates.list(self.id)


class IncidentManager(Manager):
    resource_class = Incident
    path = 'incidents'

    def __init__(self, http_client: HttpClient, incident_update_manager: IncidentUpdatesManager):
        super().__init__(http_client)
        self.updates = incident_update_manager

    def create(
            self,
            *,
            name: str,
            message: str,
            status: int,
            visible: bool = True,
            component_id: int = None,
            component_status: int = None,
            notify: bool = True,
            created_at: datetime = None,
            template: str = None,
            template_vars: List[str] = None) -> Incident:
        """
        Create and general issue or issue for a component.
        component_id and component_status must be supplied when making
        a component issue.

        Keyword Args:
            name (str): Name/title of the issue
            message (str): Mesage body for the issue
            status (int): Status of the incident (see enums)
            visible (bool): Publicly visible incident
            component_id (int): The component to update
            component_status (int): The status to apply on component
            notify (bool): If users should be notified
            created_at: when the indicent was created
            template (str): Slug of template to use
            template_vars (list): Variables to the template

        Returns:
            Incident instance
        """
        return self._create(
            self.path,
            {
                'name': name,
                'message': message,
                'status': status,
                'visible': 1 if visible else 0,
                'component_id': component_id,
                'component_status': component_status,
                'notify': 1 if notify else 0,
                'created_at': created_at,
                'template': template,
                'vars': template_vars,
            }
        )

    def update(
            self,
            incident_id: int,
            name: str = None,
            message: str = None,
            status: int = None,
            visible: bool = None,
            component_id: int = None,
            component_status: int = None,
            notify: bool = True,
            created_at: datetime = None,
            template: str = None,
            template_vars: List[str] = None,
            **kwargs) -> Incident:
        """
        Update an incident.

        Args:
            incident_id (int): The incident to update

        Keyword Args:
            name (str): Name/title of the issue
            message (str): Mesage body for the issue
            status (int): Status of the incident (see enums)
            visible (bool): Publicly visible incident
            component_id (int): The component to update
            component_status (int): The status to apply on component
            notify (bool): If users should be notified
            created_at: when the indicent was created
            template (str): Slug of template to use
            template_vars (list): Variables to the template

        Returns:
            Updated incident Instance
        """
        if name is None or message is None or status is None or visible is None:
            raise ValueError('name, message, status and visible are required parameters')

        return self._update(
            self.path,
            incident_id,
            self._build_data_dict(
                name=name,
                message=message,
                status=status,
                visible=1 if visible else 0,
                component_id=component_id,
                component_status=component_status,
                notify=1 if notify else 0,
                created_at=created_at,
                template=template,
                vars=template_vars,
            )
        )

    def list(self, page: int = 1, per_page: int = 1) -> Generator[Incident, None, None]:
        """
        List all incidents paginated

        Keyword Args:
            page (int): Page to start on
            per_page (int): Entires per page

        Returns:
            Generator of :py:data:`Incident`s
        """
        return self._list_paginated(
            self.path,
            page=page,
            per_page=per_page,
        )

    def get(self, incident_id: int) -> Incident:
        """
        Get a single incident

        Args:
            incident_id (int): The incident id to get

        Returns:
            :py:data:`Incident` instance

        Raises:
            :py:data:`requests.exception.HttpError`: if incident do not exist
        """
        return self._get(self.path, incident_id)

    def count(self) -> int:
        """
        Count the number of incidents

        Returns:
            int: Total number of incidents
        """
        return self._count(self.path)

    def delete(self, incident_id: int) -> None:
        """
        Delete an incident

        Args:
            incident_id (int): The incident id
        """
        self._delete(self.path, incident_id)
