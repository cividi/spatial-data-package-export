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
from typing import Any, Dict, List, Tuple, Union

from qgis.core import (
    QgsExpression,
    QgsFeature,
    QgsMarkerSymbol,
    QgsSymbol,
    QgsUnitTypes,
)

from ..core.exceptions import StyleException
from ..qgis_plugin_tools.tools.custom_logging import bar_msg
from ..qgis_plugin_tools.tools.exceptions import QgsPluginExpressionException
from ..qgis_plugin_tools.tools.i18n import tr
from ..qgis_plugin_tools.tools.layers import evaluate_expressions
from ..qgis_plugin_tools.tools.resources import plugin_name

LOGGER = logging.getLogger(plugin_name())


class Style:
    MILLIMETER_SIZE_UNIT = "MM"
    PIXEL_SIZE_UNIT = "Pixel"
    MM_TO_PIXEL = 0.28  # Taken from qgssymbollayerutils.cpp

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

    @staticmethod
    def _hex_to_rgb(hex_color: str, opacity: float) -> str:
        hex_val = hex_color.lstrip("#")
        rgb: List[int] = list(int(hex_val[i : i + 2], 16) for i in (0, 2, 4))
        rgb.append(int(opacity * 255))
        return ",".join(map(str, rgb))

    @staticmethod
    def rgb_extract(prop: str) -> Tuple[str, float]:
        _prop = list(map(int, prop.split(",")))
        _rgb = "#" + ("%02x%02x%02x" % tuple(_prop[0:-1]))
        alpha = round(_prop[-1] / 255, 2)
        return _rgb, alpha

    @staticmethod
    def convert_to_pixels(value: float, size_unit: str) -> float:
        """
        Converts size unit into pixel values.

        This method is partly applied from https://github.com/UnfoldedInc/qgis-plugin
        created by Gispo Ltd.
        Licensed under GPLv2 License.
        """
        if size_unit == Style.MILLIMETER_SIZE_UNIT:
            value = round(value / Style.MM_TO_PIXEL, 4)

        if size_unit in (Style.MILLIMETER_SIZE_UNIT, Style.PIXEL_SIZE_UNIT):
            return value
        else:
            raise StyleException(
                tr('Size unit "{}" is unsupported.', size_unit),
                bar_msg=bar_msg(
                    tr(
                        "Please use {} instead",
                        tr("or").join(
                            (Style.MILLIMETER_SIZE_UNIT, Style.PIXEL_SIZE_UNIT)
                        ),
                    )
                ),
            )

    @property
    def legend_style(self) -> Dict[str, Any]:
        values = self.to_dict(for_legend=True)
        return {
            self.LEGEND_MAPPER[key]: value
            for key, value in values.items()
            if key in self.LEGEND_MAPPER.keys()
        }

    def fill_based_on_feature(self, feature: QgsFeature) -> None:
        for f_name, c_name in self.FIELD_MAPPER.items():
            self.__dict__[c_name] = feature[f_name]

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

    def create_qgis_symbol(self) -> QgsSymbol:
        pass


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
        # based on QGIS default mm radius converted to pixels
        self.radius: Union[int, float, str] = 7.14
        self.has_fill = True
        self.has_stroke = True
        self.title = ""

    # noinspection PyArgumentList
    def create_qgis_symbol(self) -> QgsMarkerSymbol:
        marker_symbol = QgsMarkerSymbol.createSimple(
            {
                "color": self._hex_to_rgb(self.fill, self.fill_opacity),
                "outline_color": self._hex_to_rgb(self.stroke, self.stroke_opacity),
                "outline_width": str(self.stroke_width),
                "outline_width_unit": self.PIXEL_SIZE_UNIT,
                "size": self.radius,
                "size_unit": self.PIXEL_SIZE_UNIT,
            }
        )
        marker_symbol.setSizeUnit(QgsUnitTypes.RenderPixels)
        marker_symbol.sizeMapUnitScale()
        return marker_symbol  # noqa
