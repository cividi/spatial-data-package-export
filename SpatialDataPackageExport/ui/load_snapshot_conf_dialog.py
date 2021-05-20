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
from typing import List

from qgis.PyQt.QtWidgets import QComboBox, QDialog, QWidget

from ..qgis_plugin_tools.tools.resources import load_ui, plugin_name

FORM_CLASS: QWidget = load_ui("load_snapshot_conf_dialog.ui")
LOGGER = logging.getLogger(plugin_name())


class LoadSnapshotConfDialog(QDialog, FORM_CLASS):
    def __init__(self, snapshot_conf_names: List[str]) -> None:
        QDialog.__init__(self)
        self.setupUi(self)
        self.cb_snapshot_confs: QComboBox = self.cb_snapshot_confs
        self.cb_snapshot_confs.addItems(snapshot_conf_names)

    def get_chosen_snapshot_config_name(self) -> str:
        return self.cb_snapshot_confs.currentText()
