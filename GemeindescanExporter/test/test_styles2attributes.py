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

STYLE_FIELDS = {'fill', "fill-opacity", "stroke", "stroke-opacity", "stroke-width"}


def test_fields(new_project, layer_simple_poly):
    converter = StylesToAttributes(layer_simple_poly, layer_simple_poly.name())
    fields = [f.name() for f in converter.fields.toList()]
    assert len(fields) == len(layer_simple_poly.fields().toList()) + 5
    assert STYLE_FIELDS.difference(fields) == set()


def test_simple_poly(new_project, categorized_poly, layer_empty_poly):
    converter = StylesToAttributes(categorized_poly, categorized_poly.name())
    assert converter.symbol_type == SymbolType.categorizedSymbol

    update_fields(converter, layer_empty_poly)
    layer_empty_poly.startEditing()
    converter.run(layer_empty_poly, QgsProcessingFeedback())
    layer_empty_poly.commitChanges()

    expected_symbols, expected_legend = get_symbols_and_legend('categorized_poly')

    assert layer_empty_poly.featureCount() == categorized_poly.featureCount()
    common_asserts(converter, expected_legend, expected_symbols, layer_empty_poly)


def common_asserts(converter, expected_legend, expected_symbols, layer):
    assert converter.legend == expected_legend
    assert converter.symbols == expected_symbols
    for i in range(layer.featureCount()):
        # Memory layer indexing starts with 1 instead of 0 (possibly a BUG)
        f = layer.getFeature(i + 1)
        symbol = expected_symbols[i]
        for key in STYLE_FIELDS:
            assert f[key] == symbol['style'][key]


def update_fields(converter: StylesToAttributes, layer: QgsVectorLayer):
    dp: QgsVectorDataProvider = layer.dataProvider()
    dp.addAttributes(converter.fields)
    layer.updateFields()
