#!
# -*- coding: utf-8 -*-

import unohelper
from com.sun.star.awt import XContainerWindowEventHandler
from com.sun.star.beans import PropertyValue
import gettext
import parlatype_utils as pt_utils

_ = gettext.gettext


class OptionsDialogHandler(unohelper.Base, XContainerWindowEventHandler):
    def __init__(self, ctx):
        self.ctx = ctx
        smgr = ctx.getServiceManager()
        self.cfg = smgr.createInstanceWithContext(
            'com.sun.star.configuration.ConfigurationProvider', ctx)
        self.node = PropertyValue()
        self.node.Name = 'nodepath'
        self.node.Value = '/xyz.parlatype.config'
        self.orig_keys_value = 0
        self.orig_mouse_value = 0
        pt_utils.setGettextDomain(ctx)

    # XContainerWindowEventHandler
    def callHandlerMethod(self, window, eventObject, method):
        if method == "external_event":
            try:
                self._handleExternalEvent(window, eventObject)
            except Exception as e:
                print(e)
            return True

    # XContainerWindowEventHandler
    def getSupportedMethodNames(self):
        return ("external_event",)

    def _handleExternalEvent(self, window, eventName):
        if eventName == "ok":
            self._saveData(window)
        elif eventName == "back":
            self._loadData(window, eventName)
        elif eventName == "initialize":
            self._loadData(window, eventName)
        return True

    def _saveData(self, window):
        name = window.getModel().Name
        if name != "ParlatypeOptionsDialog":
            return
        writer = self.cfg.createInstanceWithArguments(
            'com.sun.star.configuration.ConfigurationUpdateAccess',
            (self.node,))
        check_keys = window.getControl("CheckboxKeys")
        check_mouse = window.getControl("CheckboxMouse")
        new_keys_value = check_keys.getState()
        new_mouse_value = check_mouse.getState()
        if self.orig_keys_value != new_keys_value:
            writer.setPropertyValue('TimestampKeys', new_keys_value)
        if self.orig_mouse_value != new_mouse_value:
            writer.setPropertyValue('TimestampMouse', new_mouse_value)
        writer.commitChanges()

    def _loadData(self, window, eventName):
        name = window.getModel().Name
        if name != "ParlatypeOptionsDialog":
            return

        check_keys = window.getControl("CheckboxKeys")
        check_mouse = window.getControl("CheckboxMouse")

        if eventName == "initialize":
            label = window.getControl("Label1")
            label.setText(_("Go to timestamp"))
            check_mouse.setLabel(_("On mouseclick"))
            check_keys.setLabel(_("On key cursor"))

        reader = self.cfg.createInstanceWithArguments(
            'com.sun.star.configuration.ConfigurationAccess', (self.node,))
        self.orig_keys_value = reader.getPropertyValue('TimestampKeys')
        self.orig_mouse_value = reader.getPropertyValue('TimestampMouse')
        check_keys.setState(self.orig_keys_value)
        check_mouse.setState(self.orig_mouse_value)


# uno implementation
ImplementationName = "xyz.parlatype.OptionsDialog"

g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(
    OptionsDialogHandler,
    ImplementationName,
    (ImplementationName,),)
