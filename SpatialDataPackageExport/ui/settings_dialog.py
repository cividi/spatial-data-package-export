#  Gispo Ltd., hereby disclaims all copyright interest in the program
#  SpatialDataPackageExport
#  Copyright (C) 2020 Gispo Ltd (https://www.gispo.fi/).
#
#
#  This file is part of SpatialDataPackageExport.
#
#  SpatialDataPackageExport is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SpatialDataPackageExport is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SpatialDataPackageExport.  If not, see <https://www.gnu.org/licenses/>.

import logging
from typing import Optional, Type

from PyQt5.QtWidgets import QDialog, QRadioButton, QWidget

from ..definitions.configurable_settings import Settings
from ..qgis_plugin_tools.tools.custom_logging import bar_msg
from ..qgis_plugin_tools.tools.decorations import log_if_fails
from ..qgis_plugin_tools.tools.i18n import tr
from ..qgis_plugin_tools.tools.resources import load_ui, plugin_name

FORM_CLASS: QWidget = load_ui("settings_dialog.ui")
LOGGER = logging.getLogger(plugin_name())


class SettingsDialog(QDialog, FORM_CLASS):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.__set_initial_values()
        self.__initialize_ui()

    @log_if_fails
    def __initialize_ui(self) -> None:
        # Snapshot layer format
        def set_layer_format_setting(is_checked: bool, layer_format: str) -> None:
            if is_checked:
                LOGGER.debug(f"Setting layer_format to {layer_format}")
                Settings.layer_format.set(layer_format)

        self.rb_layer_memory.toggled.connect(
            lambda: set_layer_format_setting(self.rb_layer_memory.isChecked(), "memory")
        )
        self.rb_layer_geojson.toggled.connect(
            lambda: set_layer_format_setting(
                self.rb_layer_geojson.isChecked(), "geojson"
            )
        )
        self.rb_layer_none.toggled.connect(
            lambda: set_layer_format_setting(self.rb_layer_none.isChecked(), "none")
        )

    @log_if_fails
    def __set_initial_values(self) -> None:
        LOGGER.debug("Initializing settings")

        # Snapshot layer format
        snapshot_layer_format = Settings.layer_format.get()
        rb_button: QRadioButton = self.__get_widget(f"rb_layer_{snapshot_layer_format}")
        if rb_button:
            rb_button.setChecked(True)

        # Template paths
        self.f_snapshot_template.setFilePath(Settings.snapshot_template.get())
        self.f_snapshot_template.fileChanged.connect(
            lambda path: Settings.snapshot_template.set(path)
        )
        self.f_snapshot_config_template.setFilePath(
            Settings.export_config_template.get()
        )
        self.f_snapshot_config_template.fileChanged.connect(
            lambda path: Settings.export_config_template.set(path)
        )

    def __get_widget(self, widget_name: str) -> Optional[Type[QWidget]]:
        try:
            LOGGER.debug(widget_name)
            return getattr(self, widget_name)
        except AttributeError:
            LOGGER.warning(tr("Invalid widget for setting"), extra=bar_msg(widget_name))
            return None
