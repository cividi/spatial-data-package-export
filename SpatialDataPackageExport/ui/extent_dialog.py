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
from typing import Optional

from PyQt5.QtWidgets import QDialog, QWidget
from qgis.core import QgsCoordinateReferenceSystem, QgsRectangle
from qgis.gui import QgsExtentGroupBox, QgsMapCanvas

from ..qgis_plugin_tools.tools.resources import load_ui, plugin_name

FORM_CLASS: QWidget = load_ui("extent_chooser_dialog.ui")
LOGGER = logging.getLogger(plugin_name())


class ExtentChooserDialog(QDialog, FORM_CLASS):
    def __init__(
        self,
        canvas: QgsMapCanvas,
        crs: QgsCoordinateReferenceSystem,
        parent: Optional[QWidget] = None,
    ) -> None:
        QDialog.__init__(self, parent)
        self.setupUi(self)

        extent_gb: QgsExtentGroupBox = self.gb_extent
        extent_gb.setOriginalExtent(canvas.extent(), crs)
        extent_gb.setCurrentExtent(canvas.extent(), crs)
        extent_gb.setOutputCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
        # TODO: fix bug - QGIS crashes when drawing from canvas
        # extent_gb.setMapCanvas(canvas)

    def get_extent(self, precision: int) -> QgsRectangle:
        extent_gb: QgsExtentGroupBox = self.gb_extent
        extent: QgsRectangle = extent_gb.outputExtent()
        LOGGER.debug(f"Extent is {extent.toString(precision)}")
        return extent
