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

import pytest
from qgis.core import QgsVectorDataProvider, QgsProcessingFeedback, QgsVectorLayer, QgsFields

from .utils import get_symbols_and_legend
from ..core.styles2attributes import StylesToAttributes
from ..definitions.style import SimpleStyle, PointStyle, Style
from ..definitions.symbols import SymbolType
from ..qgis_plugin_tools.tools.logger_processing import LoggerProcessingFeedBack


def test_simple_style_fields(new_project, layer_simple_poly):
    converter = StylesToAttributes(layer_simple_poly, layer_simple_poly.name(), QgsProcessingFeedback())
    fields = [f.name() for f in converter.fields.toList()]

    assert len(fields) == len(layer_simple_poly.fields().toList()) + len(SimpleStyle.FIELD_MAPPER)
    assert set(SimpleStyle.FIELD_MAPPER.keys()).difference(fields) == set()


def test_point_style_fields(new_project, layer_points):
    converter = StylesToAttributes(layer_points, layer_points.name(), QgsProcessingFeedback())
    fields = [f.name() for f in converter.fields.toList()]
    # There is radius field already defined
    assert len(fields) == len(layer_points.fields().toList()) + len(PointStyle.FIELD_MAPPER) - 1
    assert set(PointStyle.FIELD_MAPPER.keys()).difference(fields) == set()


def test_simple_poly(new_project, layer_simple_poly, layer_empty_poly):
    simple_asserts(layer_simple_poly, layer_empty_poly)


def test_simple_lines(new_project, layer_lines, layer_empty_lines):
    simple_asserts(layer_lines, layer_empty_lines)


def test_simple_points(new_project, layer_points, layer_empty_points):
    simple_asserts(layer_points, layer_empty_points)


@pytest.mark.skip('TODO: fix styles2attributes for centroid layers')
def test_centroid_poly(new_project, centroid_poly, layer_empty_points):
    simple_asserts(centroid_poly, layer_empty_points)


def test_categorized_poly(new_project, categorized_poly, layer_empty_poly):
    converter = simple_asserts(categorized_poly, layer_empty_poly, SymbolType.categorizedSymbol)

    expected_symbols, expected_legend = get_symbols_and_legend('categorized_poly')
    common_asserts(converter, expected_legend, expected_symbols, layer_empty_poly)


def test_points_with_radius(new_project, points_with_radius, layer_empty_points):
    converter = simple_asserts(points_with_radius, layer_empty_points, SymbolType.categorizedSymbol)

    assert converter.symbols[0]['style'].data_defined_expressions.keys() == {'radius'}

    expected_symbols, expected_legend = get_symbols_and_legend('points_with_radius')
    common_asserts(converter, expected_legend, expected_symbols, layer_empty_points)


def simple_asserts(src_layer, dst_layer, symbol=SymbolType.singleSymbol):
    feedback = LoggerProcessingFeedBack()
    converter = StylesToAttributes(src_layer, src_layer.name(), feedback)
    assert converter.symbol_type == symbol
    update_fields(converter, dst_layer)
    dst_layer.startEditing()
    converter.extract_styles_to_layer(dst_layer)
    succeeded = dst_layer.commitChanges()
    assert succeeded, f'Copying fields failed: {dst_layer.commitErrors()}'
    assert not feedback.isCanceled(), feedback.last_report_error
    assert dst_layer.featureCount() == src_layer.featureCount(), 'feature count is not the same'
    return converter


def common_asserts(converter, expected_legend, expected_symbols, converted_layer):
    assert [val.to_dict() for val in converter.legend.values()] == expected_legend, 'Legends differ'
    assert converter.get_symbols() == expected_symbols, 'Symbols differ'

    if len(converter.symbols[0]['style'].data_defined_expressions) == 0:
        for i in range(converted_layer.featureCount()):
            # Memory layer indexing starts with 1 instead of 0 (possibly a BUG)
            f = converted_layer.getFeature(i + 1)
            symbol = expected_symbols[i]
            style: Style = converter.symbols[i]['style']
            for key, c_key in style.FIELD_MAPPER.items():
                assert f[key] == symbol['style'][key]


def update_fields(converter: StylesToAttributes, layer: QgsVectorLayer):
    dp: QgsVectorDataProvider = layer.dataProvider()
    fields: QgsFields = layer.fields()
    for field in converter.fields:
        if field not in fields:
            dp.addAttributes([field])
    layer.updateFields()
