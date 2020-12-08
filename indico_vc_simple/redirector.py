'''
Created on Oct 5, 2020

@author: pedersen
'''

import requests
from flask import flash, redirect, session
from sqlalchemy.orm.attributes import flag_modified
from werkzeug.exceptions import BadRequest
from wtforms.fields.core import BooleanField
from wtforms.fields.html5 import URLField

from indico.core.plugins import IndicoPluginBlueprint, url_for_plugin
from indico.modules.events.contributions.models.contributions import \
    Contribution
from indico.modules.events.registration.util import get_event_regforms
from indico.modules.vc.forms import VCRoomAttachFormBase, VCRoomFormBase
from indico.util.i18n import _
from indico.web.forms.widgets import SwitchWidget
from indico.web.rh import RHSimple
from indico_vc_simple.simple import SimpleVCLinkPlugin


class VCRoomForm(VCRoomFormBase):
    room_url_base = URLField('Redirector URL?', description="vc room url rediredctor")
    show_join_button = BooleanField(
        _('Show join Button'),
        widget=SwitchWidget(),
        description=_("Show the join button on the event page"))
    only_registered_users = BooleanField(
        _('Only registered users'),
        widget=SwitchWidget(),
        description=_("Only registered users"))


class VCRoomAttachForm(VCRoomAttachFormBase):
    room_url_base = URLField('Redirector URL?', description="vc room url redirector")
    show_join_button = BooleanField(
        _('Show join Button'),
        widget=SwitchWidget(),
        description=_("Show the join button on the event page"))
    only_registered_users = BooleanField(
        _('Only registered users'),
        widget=SwitchWidget(),
        description=_("Only registered users"))


class RedirectorPlugin(SimpleVCLinkPlugin):
    """Redirect  to VC

    Simple videoconferencing plugin, BBB redirect
    """
    configurable = True
    vc_room_form = VCRoomForm
    vc_room_attach_form = VCRoomAttachForm
    friendly_name = "Redirector Simple"

    @property
    def logo_url(self):
        return url_for_plugin(SimpleVCLinkPlugin.name + '.static',
                              filename='images/redirector_logo.png')

    @property
    def icon_url(self):
        return url_for_plugin(SimpleVCLinkPlugin.name + '.static',
                              filename='images/redirector_icon.png')

    def get_blueprints(self):
        return _bp

    def update_data_vc_room(self, vc_room, data, is_new=False):
        super(RedirectorPlugin, self).update_data_vc_room(vc_room, data)

        for key in ['room_url_base']:
            if key in data:
                vc_room.data[key] = data.pop(key)
                contrib = Contribution.get(data['contribution'])
                cid = contrib.id if contrib else 0
                vc_room.data['room_url'] = url_for_plugin(
                    'vc_redirector.vc_redirect', contrib_id=cid)

        flag_modified(vc_room, 'data')


@RHSimple.wrap_function
def RHredirectToExternal(contrib_id):

    contrib = Contribution.get_or_404(contrib_id)
    event = contrib.event
    if not session.user:
        flash(_("The vc link  is only available to logged in users."),'error')
        raise BadRequest(response=redirect(event.url))

    vcas = contrib.vc_room_associations
    vca = None
    for _vca in vcas:
        vca = _vca
        if isinstance(vca.vc_room.plugin, RedirectorPlugin):
            break
    else:
        raise BadRequest(response=redirect(event.url))
    if vca.data.get('only_registered_users') and \
        not any([x[1] for x in get_event_regforms(event, session.user)]):
        flash(_("The vc link is only available to registered users."),'error')
        raise BadRequest(response=redirect(event.url))

    vcroom = vca.vc_room
    url = vcroom.data['room_url_base']
    data = {'id': contrib.friendly_id, 'username': session.user.name}

    req = requests.post(url, json=data)
    if req.status_code != 200:
        flash('Error: The redirector did not succeed!','error')
        raise BadRequest(response=redirect(event.url))

    res = req.json()
    if res['status'] != 'success':
        flash(_("Videoconference link:") +' '+ res['message'], 'error')
        raise BadRequest(response=redirect(event.url))


    return redirect(res['url'])


_bp = IndicoPluginBlueprint('vc_redirector', __name__)

_bp.add_url_rule('/redirectVC/<contrib_id>',
                 'vc_redirect',
                 view_func=RHredirectToExternal)
