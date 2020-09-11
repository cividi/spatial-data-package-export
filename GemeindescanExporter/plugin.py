#  Gispo Ltd., hereby disclaims all copyright interest in the program GemeindescanExporter
#  Copyright (C) 2020 Gispo Ltd (https://www.gispo.fi/).
#
#
#  This file is part of GemeindescanExporter.
#
#  GemeindescanExporter is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  GemeindescanExporter is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with GemeindescanExporter.  If not, see <https://www.gnu.org/licenses/>.
from typing import Callable, Optional

from PyQt5.QtCore import QTranslator, QCoreApplication, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QWidget
from qgis.PyQt import QtWidgets
from qgis.core import QgsVectorLayer, QgsApplication
from qgis.gui import QgisInterface

from .core.orig import Exporter
from .core.processing.provider import GemeindescanProcessingProvider
from .qgis_plugin_tools.tools.custom_logging import setup_logger
from .qgis_plugin_tools.tools.i18n import setup_translation, tr
from .qgis_plugin_tools.tools.resources import plugin_name
from .ui.dock_widget import ExporterDockWidget


class Plugin:
    """QGIS Plugin Implementation."""

    def __init__(self, iface: QgisInterface):

        self.iface = iface

        setup_logger(plugin_name(), iface)
        # setup_task_logger(plugin_name())

        # initialize locale
        locale, file_path = setup_translation()
        if file_path:
            self.translator = QTranslator()
            self.translator.load(file_path)
            # noinspection PyCallByClass
            QCoreApplication.installTranslator(self.translator)
        else:
            pass

        self.actions = []
        self.menu = tr(plugin_name())

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.dock_widget: Optional[QtWidgets.QDockWidget] = None
        self.plugin_is_active = False

        self.processing_provider = GemeindescanProcessingProvider()

    def add_action(
            self,
            icon_path: str,
            text: str,
            callback: Callable,
            enabled_flag: bool = True,
            add_to_menu: bool = True,
            add_to_toolbar: bool = True,
            status_tip: Optional[str] = None,
            whats_this: Optional[str] = None,
            parent: Optional[QWidget] = None) -> QAction:
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.

        :param text: Text that should be shown in menu items for this action.

        :param callback: Function to be called when the action is triggered.

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.

        :param parent: Parent widget for the new action. Defaults None.

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        # noinspection PyUnresolvedReferences
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        self.add_action(
            "",
            text=tr(plugin_name()),
            callback=self.run,
            parent=self.iface.mainWindow(),
            add_to_toolbar=False
        )
        self.add_action(
            "",
            text=tr("original script"),
            callback=self.run_orig,
            parent=self.iface.mainWindow(),
            add_to_toolbar=False
        )

        QgsApplication.processingRegistry().addProvider(self.processing_provider)

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""
        if self.dock_widget is not None:
            self.dock_widget.closingPlugin.disconnect(self.onClosePlugin)
            self.plugin_is_active = False

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                tr(plugin_name()),
                action)
            self.iface.removeToolBarIcon(action)

        QgsApplication.processingRegistry().removeProvider(self.processing_provider)

    # noinspection PyArgumentList
    def run(self):
        """Run method that performs all the real work"""
        if not self.plugin_is_active:
            self.plugin_is_active = True

            if self.dock_widget is None:
                self.dock_widget = ExporterDockWidget(self.iface)

        self.dock_widget.closingPlugin.connect(self.onClosePlugin)

        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dock_widget)
        self.dock_widget.show()

    # noinspection PyArgumentList
    def run_orig(self):
        """Run method that performs all the real work"""
        print("Hello QGIS plugin")
        layer: QgsVectorLayer = self.iface.activeLayer()
        if layer is not None:
            exporter = Exporter()
            exporter.write_layer(layer.name())
            # QgsProject.instance().addMapLayer(f"{layer.name()}-snapshot")
