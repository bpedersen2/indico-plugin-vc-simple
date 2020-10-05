# This file is part of the Indico plugins.
# Copyright (C) 2002 - 2020 CERN
#
# The Indico plugins are free software; you can redistribute
# them and/or modify them under the terms of the MIT License;
# see the LICENSE file for more details.

from __future__ import unicode_literals

from sqlalchemy.orm.attributes import flag_modified
from wtforms.fields.html5 import URLField
from wtforms.fields.core import BooleanField

from indico.core.plugins import IndicoPlugin, IndicoPluginBlueprint, url_for_plugin
from indico.modules.vc import VCPluginMixin
from indico.modules.vc.forms import VCRoomAttachFormBase, VCRoomFormBase
from indico.web.forms.widgets import SwitchWidget


class VCRoomForm(VCRoomFormBase):
    room_url = URLField('Room URL?', description="vc room url")
    show_join_button = BooleanField(_('Show join Button'),
                            widget=SwitchWidget(),
                            description=_("Show the join button on the event page"))


class VCRoomAttachForm(VCRoomAttachFormBase):
    room_url = URLField('Room URL?', description="vc room url")
    show_join_button = BooleanField(_('Show join Button'),
                            widget=SwitchWidget(),
                            description=_("Show the join button on the event page"))


class SimplePlugin(VCPluginMixin, IndicoPlugin):
    """Simple

    Simple videoconferencing plugin
    """
    configurable = True
    vc_room_form = VCRoomForm
    vc_room_attach_form = VCRoomAttachForm
    friendly_name = "Simple"

    @property
    def logo_url(self):
        return url_for_plugin(self.name + '.static', filename='images/simple_logo.png')

    @property
    def icon_url(self):
        return url_for_plugin(self.name + '.static', filename='images/simple_icon.png')

    def get_blueprints(self):
        return IndicoPluginBlueprint('vc_simple', __name__)

    def create_room(self, vc_room, event):
        pass

    def delete_room(self, vc_room, event):
        pass

    def update_room(self, vc_room, event):
        pass

    def refresh_room(self, vc_room, event):
        pass

    def update_data_association(self, event, vc_room, event_vc_room, data):

        super(SimplePlugin, self).update_data_association(event, vc_room, event_vc_room, data)
        event_vc_room.data.update({key: data.pop(key) for key in [
            'show_join_button'
        ]})

        flag_modified(event_vc_room, 'data')
    
    def update_data_vc_room(self, vc_room, data):
        super(SimplePlugin, self).update_data_vc_room(vc_room, data)

        for key in ['room_url']:
            if key in data:
                vc_room.data[key] = data.pop(key)

        flag_modified(vc_room, 'data')
