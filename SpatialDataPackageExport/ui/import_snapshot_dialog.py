#  Gispo Ltd., hereby disclaims all copyright interest in the program
#  SpatialDataPackageExport
#  Copyright (C) 2020-2021 Gispo Ltd (https://www.gispo.fi/).
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
from pathlib import Path
from typing import Optional

from PyQt5.QtWidgets import QDialog, QWidget

from ..definitions.configurable_settings import Settings
from ..qgis_plugin_tools.tools.resources import load_ui, plugin_name

FORM_CLASS: QWidget = load_ui("import_snapshot_dialog.ui")
LOGGER = logging.getLogger(plugin_name())


class ImportSnapshotDialog(QDialog, FORM_CLASS):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.file_widget.setFilePath(Settings.export_config_template.get())
        self.file_widget.fileChanged.connect(self._on_file_widget_file_changed)
        self.snapshot_file_path: Optional[Path] = None

    def _on_file_widget_file_changed(self, file_path: str) -> None:
        if file_path != "":
            LOGGER.debug(f"File path is {file_path}")
            self.snapshot_file_path = Path(file_path)
        else:
            self.snapshot_file_path = None
