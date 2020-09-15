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

from qgis.core import QgsVectorDataProvider, QgsProcessingFeedback, QgsVectorLayer

from .utils import get_symbols_and_legend
from ..core.styles2attributes import StylesToAttributes
from ..definitions.symbols import SymbolType
from ..qgis_plugin_tools.tools.logger_processing import LoggerProcessingFeedBack

STYLE_FIELDS = {'fill', "fill-opacity", "stroke", "stroke-opacity", "stroke-width"}


def test_fields(new_project, layer_simple_poly):
    converter = StylesToAttributes(layer_simple_poly, layer_simple_poly.name(), QgsProcessingFeedback())
    fields = [f.name() for f in converter.fields.toList()]
    assert len(fields) == len(layer_simple_poly.fields().toList()) + 5
    assert STYLE_FIELDS.difference(fields) == set()


def test_simple_poly(new_project, layer_simple_poly, layer_empty_poly):
    simple_asserts(layer_simple_poly, layer_empty_poly)


def test_simple_lines(new_project, layer_lines, layer_empty_lines):
    simple_asserts(layer_lines, layer_empty_lines)


def test_simple_points(new_project, layer_points, layer_empty_points):
    simple_asserts(layer_points, layer_empty_points)


def test_centroid_poly(new_project, centroid_poly, layer_empty_points):
    simple_asserts(centroid_poly, layer_empty_points)


def test_categorized_poly(new_project, categorized_poly, layer_empty_poly):
    converter = simple_asserts(categorized_poly, layer_empty_poly, SymbolType.categorizedSymbol)

    expected_symbols, expected_legend = get_symbols_and_legend('categorized_poly')
    common_asserts(converter, expected_legend, expected_symbols, categorized_poly, layer_empty_poly)


def simple_asserts(src_layer, dst_layer, symbol=SymbolType.singleSymbol):
    feedback = LoggerProcessingFeedBack()
    converter = StylesToAttributes(src_layer, src_layer.name(), feedback)
    assert converter.symbol_type == symbol
    update_fields(converter, dst_layer)
    dst_layer.startEditing()
    converter.extract_styles_to_layer(dst_layer)
    dst_layer.commitChanges()
    assert not feedback.isCanceled(), feedback.last_report_error
    assert dst_layer.featureCount() == src_layer.featureCount(), 'feature count is not the same'
    return converter


def common_asserts(converter, expected_legend, expected_symbols, src_layer, converted_layer):
    assert converter.get_legend() == expected_legend
    assert converter.symbols == expected_symbols
    for i in range(converted_layer.featureCount()):
        # Memory layer indexing starts with 1 instead of 0 (possibly a BUG)
        f = converted_layer.getFeature(i + 1)
        symbol = expected_symbols[i]
        for key in STYLE_FIELDS:
            assert f[key] == symbol['style'][key]


def update_fields(converter: StylesToAttributes, layer: QgsVectorLayer):
    dp: QgsVectorDataProvider = layer.dataProvider()
    dp.addAttributes(converter.fields)
    layer.updateFields()
