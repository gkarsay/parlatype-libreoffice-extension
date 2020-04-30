# -*- coding: utf-8 -*-
'''
Copyright (C) Gabor Karsay 2020 <gabor.karsay@gmx.at>

This program is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

from subprocess import Popen
import sys
import os
import uno
import unohelper
from com.sun.star.lang import XServiceInfo
from com.sun.star.frame import XDispatchProvider
from com.sun.star.frame import XDispatch
from com.sun.star.frame import FeatureStateEvent
from com.sun.star.beans import PropertyValue
from com.sun.star.awt import XKeyHandler
from com.sun.star.awt import XMouseClickHandler
from com.sun.star.document import XDocumentEventListener
from com.sun.star.beans.PropertyAttribute import MAYBEVOID
from com.sun.star.beans.PropertyAttribute import BOUND
from com.sun.star.beans.PropertyAttribute import REMOVEABLE
import gettext
import parlatype_utils as pt_utils
from parlatype_utils import showMessage


_ = gettext.gettext

ImplementationName = "org.parlatype.ProtocolHandler"
ServiceName = "com.sun.star.frame.ProtocolHandler"
Protocol = "org.parlatype.loextension:"


current_timestamp = ''


class KeyHandler(unohelper.Base, XKeyHandler):

    def __init__(self, parent):
        self.parent = parent

    def keyPressed(self, oEvent):
        return False

    def keyReleased(self, oEvent):
        self.parent._checkCursorforTimestamp()
        return False

    def disposing(self, source):
        pass


class MouseHandler(unohelper.Base, XMouseClickHandler):

    def __init__(self, parent):
        self.parent = parent

    def mousePressed(self, oEvent):
        return False

    def mouseReleased(self, oEvent):
        self.parent._checkCursorforTimestamp(goto_current_timestamp=True)
        return False

    def disposing(self, source):
        pass


class ParlatypeController(object):
    """ Controls Parlatype. """

    def __init__(self, ctx):
        self.ctx = ctx
        self.key_handler = KeyHandler(self)
        self.mouse_handler = MouseHandler(self)
        self.link_url = None
        self.linked = False
        smgr = self.ctx.getServiceManager()
        self.desktop = smgr.createInstanceWithContext(
            "com.sun.star.frame.Desktop", self.ctx)

    def _checkCursorforTimestamp(self, goto_current_timestamp=False):
        global current_timestamp
        doc = self.desktop.getCurrentComponent()
        controller = doc.getCurrentController()
        timestamp = pt_utils.extractTimestamp(controller)

        if (timestamp is None):
            current_timestamp = ''
            return
        if (timestamp == current_timestamp
                and goto_current_timestamp is False):
            return
        current_timestamp = timestamp

        iface = pt_utils.getDBUSService()
        try:
            iface.GotoTimestamp(timestamp)
        except Exception as e:
            print(str(e))

    def deactivateTimestampScanner(self):
        doc = self.desktop.getCurrentComponent()
        controller = doc.getCurrentController()
        controller.removeKeyHandler(self.key_handler)
        controller.removeMouseClickHandler(self.mouse_handler)

    def activateTimestampScanner(self):
        # Get options
        smgr = self.ctx.getServiceManager()
        cfg = smgr.createInstanceWithContext(
            'com.sun.star.configuration.ConfigurationProvider', self.ctx)
        node = PropertyValue()
        node.Name = 'nodepath'
        node.Value = '/org.parlatype.config'
        reader = cfg.createInstanceWithArguments(
            'com.sun.star.configuration.ConfigurationAccess', (node,))
        keys = reader.getPropertyValue('TimestampKeys')
        mouse = reader.getPropertyValue('TimestampMouse')

        # Attach listeners
        doc = self.desktop.getCurrentComponent()
        controller = doc.getCurrentController()
        if (keys == 1):
            controller.addKeyHandler(self.key_handler)
        if (mouse == 1):
            controller.addMouseClickHandler(self.mouse_handler)
        print("timestamp scanner activated")

    def _get_link_url(self):
        doc = self.desktop.getCurrentComponent()
        doc_prop = doc.getDocumentProperties()
        doc_uprop = doc_prop.getUserDefinedProperties()
        set = doc_uprop.getPropertySetInfo()
        if set.hasPropertyByName('Parlatype') is False:
            return None
        else:
            return doc_uprop.getPropertyValue('Parlatype')

    def open(self):
        ''' Note: This is called in a different instance of ParlatypeController
            than "link". '''
        url = None
        url = self._get_link_url()
        if url is not None:
            Popen(["parlatype", url])
        else:
            Popen(["parlatype"])

    def setLinkedStatus(self, status):
        self.linked = status

    def unlinkMedia(self):
        try:
            doc = self.desktop.getCurrentComponent()
            doc_prop = doc.getDocumentProperties()
            doc_uprop = doc_prop.getUserDefinedProperties()
            doc_uprop.removeProperty('Parlatype')
        except Exception as e:
            print(str(e))
        print("unlink")
        self.linked = False

    def linkMedia(self):
        doc = self.desktop.getCurrentComponent()
        doc_prop = doc.getDocumentProperties()
        doc_uprop = doc_prop.getUserDefinedProperties()
        set = doc_uprop.getPropertySetInfo()
        if set.hasPropertyByName('Parlatype'):
            print('Already linked to ' + doc_uprop.getPropertyValue())
            return

        iface = pt_utils.getDBUSService()
        if iface is None:
            try:
                showMessage(self.ctx, _("Please open Parlatype first"))
            except Exception as e:
                print(str(e))
            return
        try:
            media = iface.GetURI()
            if media == "":
                showMessage(self.ctx, _("Please open a media file first"))
                return
        except Exception as e:
            print(str(e))

        doc_uprop.addProperty('Parlatype',
                              MAYBEVOID + BOUND + REMOVEABLE,
                              "")  # default value
        doc_uprop.setPropertyValue('Parlatype', media)
        self.linked = True

    def link(self):
        ''' This is a toggle type method, it can mean link or unlink. '''
        if self.linked:
            self.unlinkMedia()
            self.deactivateTimestampScanner()
            return True
        else:
            self.linkMedia()
            if self.linked:
                self.activateTimestampScanner()
                return True
            else:
                return False


class EventListener(unohelper.Base, XDocumentEventListener):
    def __init__(self, parent):
        self.parent = parent
        pass

    def documentEventOccured(self, event):
        if event.EventName == "OnLayoutFinished":
            self.parent.removeDocumentListener()
        if event.EventName == "OnLoad":
            self.parent.updateLinkButton()

    def disposing(event):
        pass


class ToolbarHandler(unohelper.Base, XServiceInfo,
                     XDispatchProvider, XDispatch):

    ''' This class is called for each new view and in each view for each
        command ("open" and "link"). '''

    def __init__(self, ctx):
        self.ctx = ctx
        self.listener = None
        self.status = False
        self.ev = None
        self.doc_listener = None
        self.pt = ParlatypeController(ctx)
        self.GEB = self.ctx.getValueByName(
            "/singletons/com.sun.star.frame.theGlobalEventBroadcaster")
        pt_utils.setGettextDomain(ctx)

    # XServiceInfo
    def supportsService(self, name):
        return (name == ServiceName)

    def getImplementationName(self):
        return ImplementationName

    def getSupportedServiceNames(self):
        return (ServiceName,)

    # XDispatchProvider
    def queryDispatch(self, url, target_frame_name, search_flags):
        if url.Protocol != Protocol:
            return None
        if url.Path == "link":
            ''' Add a DocumentEventListener. On event "OnLoad" we want to
                check, if the document is already linked and set the toolbar
                button appropriately.
                We don't add the listener to our document, because
                queryDispatch is called even before there is a document object.
                Therefore we use the Global Event Broadcaster which notifies of
                all documents. It removes itself "OnLayoutFinished" which
                happens after "OnLoad" or "OnNew" respectively.
                An alternative approach didn't work: A Job triggered on event
                "OnLoad". I was not able to change the button's state. '''
            self.doc_listener = EventListener(self)
            self.GEB.addDocumentEventListener(self.doc_listener)
        return self

    def queryDispatches(self, requests):
        # This is actually never called
        dispatches = \
            [self.queryDispatch(r.FeatureURL, r.FrameName, r.SearchFlags)
                for r in requests]
        return dispatches

    # XDispatch
    def dispatch(self, url, args):
        if url.Protocol == Protocol:
            if url.Path == "open":
                self.pt.open()
            elif url.Path == "link":
                if self.pt.link() is True:
                    self.status = not self.status
                    self.ev.State = self.status
                    self.listener.statusChanged(self.ev)

    def addStatusListener(self, control, url):
        ''' The StatusListener enables controlling toolbar items. We are only
            interested in the "link" item to control its toggle state. State
            false means unpressed, state true is pressed in. To change the
            state, a FeatureEventState has to be sent via the listener's
            statusChanged method. This is done in self.dispatch. '''
        self.listener = control
        self.ev = FeatureStateEvent()
        self.ev.FeatureURL = url
        self.ev.IsEnabled = True
        self.ev.Requery = False
        self.ev.Source = self
        self.ev.State = self.status

    def removeStatusListener(self, control, url):
        pass

    def removeDocumentListener(self):
        self.GEB.removeDocumentEventListener(self.doc_listener)

    def updateLinkButton(self):
        url = None
        url = self.pt._get_link_url()
        if url is not None:
            self.pt.setLinkedStatus(True)
            self.pt.activateTimestampScanner()
            self.status = True
            self.ev.State = self.status
            self.listener.statusChanged(self.ev)


# uno implementation
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(
    ToolbarHandler,
    ImplementationName,
    (ServiceName,),)
