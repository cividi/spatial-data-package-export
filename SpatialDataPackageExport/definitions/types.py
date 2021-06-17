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

import enum

from qgis.core import QgsVectorLayer

from ..qgis_plugin_tools.tools.layers import LayerType
from .style import PointStyle, SimpleStyle, Style


@enum.unique
class StyleType(enum.Enum):
    SimpleStyle = {"mediatype": "application/geo+json", "style_cls": SimpleStyle}
    PointStyle = {
        "mediatype": "application/vnd.simplestyle-extended",
        "style_cls": PointStyle,
    }

    @staticmethod
    def from_layer(layer: QgsVectorLayer) -> "StyleType":
        if LayerType.from_layer(layer) == LayerType.Point:
            return StyleType.PointStyle
        else:
            return StyleType.SimpleStyle

    @property
    def media_type(self) -> str:
        return self.value["mediatype"]  # type: ignore

    def get_style(self) -> Style:
        return self.value["style_cls"]()  # type: ignore
