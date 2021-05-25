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
#
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
#
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

from qgis._core import QgsFeatureRenderer
from qgis.core import QgsCategorizedSymbolRenderer, QgsRendererCategory, QgsVectorLayer

from SpatialDataPackageExport.definitions.symbols import SymbolType
from SpatialDataPackageExport.definitions.types import StyleType
from SpatialDataPackageExport.model.snapshot import Legend
from SpatialDataPackageExport.qgis_plugin_tools.tools.resources import plugin_name

LOGGER = logging.getLogger(plugin_name())


class AttributesToStyles:
    def __init__(self, layer: QgsVectorLayer, legend: List[Legend]) -> None:
        self.layer = layer
        self.legend = legend
        self.style_type: StyleType = StyleType.from_layer(layer)
        self.symbol_type = SymbolType.categorizedSymbol

    def set_style_based_on_attributes(self) -> None:
        """
        Sets layer style based on the attribute values
        """
        renderer = self._create_renderer()
        self.layer.setRenderer(renderer)

    def _create_renderer(self) -> QgsFeatureRenderer:
        """ Creates a simple categorized renderer based on feature id """
        symbols = {}

        for feat in self.layer.getFeatures():
            style = self.style_type.get_style()
            style.fill_based_on_feature(feat)
            symbols[feat.id()] = style.create_qgis_symbol()

        categories = [
            QgsRendererCategory(f_id, symbol, str(f_id))
            for f_id, symbol in symbols.items()
        ]
        renderer = QgsCategorizedSymbolRenderer("$id", categories)
        return renderer
