'''
Created on Oct 5, 2020

@author: pedersen
'''
from __future__ import unicode_literals

from flask import session
from sqlalchemy.orm.attributes import flag_modified
from wtforms.fields.core import BooleanField, StringField
from wtforms.fields.html5 import URLField

from indico.core.plugins import (IndicoPlugin, IndicoPluginBlueprint,
                                 url_for_plugin)
from indico.modules.events.registration.util import get_event_regforms
from indico.modules.vc import VCPluginMixin
from indico.modules.vc.forms import VCRoomAttachFormBase, VCRoomFormBase
from indico.util.i18n import _
from indico.web.forms.widgets import SwitchWidget


class VCRoomForm(VCRoomFormBase):
    room_url = URLField('Room URL?', description="vc room url")
    extra_text = StringField('Extra infos', description="Extra infos, e.g. password")
    show_join_button = BooleanField(
        _('Show join Button'),
        widget=SwitchWidget(),
        description=_("Show the join button on the event page"))
    only_registered_users = BooleanField(
        _('Only registered users'),
        widget=SwitchWidget(),
        description=_("Only registered users"))



class VCRoomAttachForm(VCRoomAttachFormBase):
    room_url = URLField('Room URL?', description="vc room url")
    extra_text = StringField('Extra infos', description="Extra infos, e.g. password")
    show_join_button = BooleanField(
        _('Show join Button'),
        widget=SwitchWidget(),
        description=_("Show the join button on the event page"))
    only_registered_users = BooleanField(
        _('Only registered users'),
        widget=SwitchWidget(),
        description=_("Only registered users"))


class SimpleVCLinkPlugin(VCPluginMixin, IndicoPlugin):
    """Simple VC link plugin

    Simple videoconferencing plugin
    """
    configurable = True
    vc_room_form = VCRoomForm
    vc_room_attach_form = VCRoomAttachForm
    friendly_name = "Simple"

    @property
    def logo_url(self):
        return url_for_plugin(self.name + '.static',
                              filename='images/simple_logo.png')

    @property
    def icon_url(self):
        return url_for_plugin(self.name + '.static',
                              filename='images/simple_icon.png')

    def get_blueprints(self):
        return IndicoPluginBlueprint('vc_simplelink', __name__)

    def get_vc_room_form_defaults(self, event):
        return {'only_registered_user': True}

    def create_room(self, vc_room, event):
        pass

    def delete_room(self, vc_room, event):
        pass

    def update_room(self, vc_room, event):
        pass

    def refresh_room(self, vc_room, event):
        pass

    def update_data_association(self, event, vc_room, event_vc_room, data):

        super(SimpleVCLinkPlugin,
              self).update_data_association(event, vc_room, event_vc_room,
                                            data)
        event_vc_room.data.update({
            key: data.pop(key)
            for key in ['extra_text', 'show_join_button', 'only_registered_users']
        })

        flag_modified(event_vc_room, 'data')

    def update_data_vc_room(self, vc_room, data, is_new=False):
        super(SimpleVCLinkPlugin, self).update_data_vc_room(vc_room, data)

        for key in ['room_url', 'extra_text']:
            if key in data:
                vc_room.data[key] = data.pop(key)

        flag_modified(vc_room, 'data')

    def render_event_buttons(self, vc_room, event_vc_room, **kwargs):
        """Renders a list of plugin specific buttons (eg: Join URL, etc) in the event page

        :param vc_room: the VC room object
        :param event_vc_room: the association of an event and a VC room
        :param kwargs: arguments passed to the template
        """
        event = event_vc_room.event
        if not self.show(event,
                         event_vc_room.data.get('only_registered_users')):
            return ''
        return super(SimpleVCLinkPlugin,
                     self).render_event_buttons(vc_room, event_vc_room,
                                                **kwargs)

    def show(self, event, only_reg=False):
        return not only_reg or any(
            [x[1] for x in get_event_regforms(event, session.user)])
