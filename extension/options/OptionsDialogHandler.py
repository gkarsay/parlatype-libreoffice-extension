#!
# -*- coding: utf-8 -*-

import os
import unohelper
from com.sun.star.awt import XContainerWindowEventHandler
from com.sun.star.beans import PropertyValue
import gettext
_ = gettext.gettext


class OptionsDialogHandler(unohelper.Base, XContainerWindowEventHandler):
    def __init__(self, ctx):
        self.ctx = ctx
        smgr = ctx.getServiceManager()
        self.cfg = smgr.createInstanceWithContext(
            'com.sun.star.configuration.ConfigurationProvider', ctx)
        self.node = PropertyValue()
        self.node.Name = 'nodepath'
        self.node.Value = '/org.parlatype.config'

        gettext.bindtextdomain('parlatype_lo', self._get_locale_path())
        gettext.textdomain('parlatype_lo')
        return

    def _get_locale_path(self):
        pip = self.ctx.getByName(
            "/singletons/com.sun.star.deployment.PackageInformationProvider")
        # Get extension path without "file://"
        ext_path = pip.getPackageLocation("org.parlatype.loextension")[7:]
        loc_path = os.path.join(ext_path, 'locale')
        return loc_path

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
        writer.setPropertyValue('TimestampKeys', check_keys.getState())
        writer.setPropertyValue('TimestampMouse', check_mouse.getState())
        writer.commitChanges()
        return

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
        check_keys.setState(reader.getPropertyValue('TimestampKeys'))
        check_mouse.setState(reader.getPropertyValue('TimestampMouse'))
        return


# uno implementation
ImplementationName = "org.parlatype.OptionsDialog"

g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(
    OptionsDialogHandler,
    ImplementationName,
    (ImplementationName,),)
