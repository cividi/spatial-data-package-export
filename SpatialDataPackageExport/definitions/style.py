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
from typing import Any, Dict, Union

from qgis.core import QgsExpression, QgsFeature

from ..qgis_plugin_tools.tools.exceptions import QgsPluginExpressionException
from ..qgis_plugin_tools.tools.i18n import tr
from ..qgis_plugin_tools.tools.layers import evaluate_expressions
from ..qgis_plugin_tools.tools.resources import plugin_name

LOGGER = logging.getLogger(plugin_name())


class Style:
    LEGEND_MAPPER = {
        "fill": "fillColor",
        "fill-opacity": "fillOpacity",
        "stroke": "strokeColor",
        "stroke-opacity": "strokeOpacity",
        "stroke-width": "strokeWidth",
        "type": "shape",
    }
    FIELD_MAPPER = {
        "fill": "fill",
        "fill-opacity": "fill_opacity",
        "stroke": "stroke",
        "stroke-opacity": "stroke_opacity",
        "stroke-width": "stroke_width",
    }

    def __init__(self) -> None:
        self.fill = "#000000"
        self.fill_opacity = 1.0
        self.stroke = "#ffffff"
        self.stroke_opacity = 1.0
        self.stroke_width = 1.0

        # Not in template
        self.type = ""

        self.data_defined_expressions: Dict[str, QgsExpression] = {}

    @property
    def legend_style(self) -> Dict[str, Any]:
        values = self.to_dict(for_legend=True)
        return {
            self.LEGEND_MAPPER[key]: value
            for key, value in values.items()
            if key in self.LEGEND_MAPPER.keys()
        }

    def add_data_defined_expression(self, field_name: str, expression: str) -> None:
        exp = QgsExpression(expression)
        if not exp.hasParserError():
            self.data_defined_expressions[field_name] = exp
        else:
            LOGGER.warning(
                tr(
                    "Skipping data defined field {} for having parse error: {}",
                    field_name,
                    exp.parserErrorString(),
                )
            )

    def evaluate_data_defined_expressions(self, feature: QgsFeature) -> None:
        for fld_name, exp in self.data_defined_expressions.items():
            try:
                value = evaluate_expressions(exp, feature)
                self.__dict__[fld_name] = value
            except QgsPluginExpressionException as e:
                LOGGER.warning(
                    tr(
                        "Skipping data defined field {} for "
                        "having evaluation error: {}",
                        fld_name,
                        e.bar_msg["details"],
                    )
                )

    def to_dict(
        self, for_legend: bool = False
    ) -> Dict[str, Union[int, float, str, bool]]:
        values_dict = self.__dict__
        values = {
            f_name: values_dict[c_name] for f_name, c_name in self.FIELD_MAPPER.items()
        }

        if for_legend:
            values["type"] = self.type
        return values


class SimpleStyle(Style):
    pass


class PointStyle(Style):
    LEGEND_MAPPER = {
        "fillColor": "fillColor",
        "fillOpacity": "fillOpacity",
        "color": "strokeColor",
        "opacity": "strokeOpacity",
        "weight": "strokeWidth",
        "type": "shape",
    }
    FIELD_MAPPER = {
        "fill": "has_fill",
        "fillColor": "fill",
        "fillOpacity": "fill_opacity",
        "stroke": "has_stroke",
        "color": "stroke",
        "opacity": "stroke_opacity",
        "weight": "stroke_width",
        "radius": "radius",
        # 'title': 'title',
    }

    def __init__(self) -> None:
        super().__init__()
        self.radius: Union[int, float, str] = 2.0  # based on QGIS default mm radius
        self.has_fill = True
        self.has_stroke = True
        self.title = ""
