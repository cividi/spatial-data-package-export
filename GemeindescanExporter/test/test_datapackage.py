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
import json

from qgis.core import QgsProcessingFeedback, QgsVectorLayer, QgsVectorDataProvider

from .conftest import add_layer
from .utils import get_test_json
from ..core.datapackage import DatapackageWriter
from ..core.styles2attributes import StylesToAttributes
from ..model.config import Config
from ..model.styled_layer import StyledLayer
from ..qgis_plugin_tools.tools.resources import plugin_test_data_path


def test_simple_poly(new_project, categorized_poly, layer_empty_poly):
    converter = StylesToAttributes(categorized_poly, categorized_poly.name(), QgsProcessingFeedback())
    update_fields(converter, layer_empty_poly)
    layer_empty_poly.startEditing()
    converter.extract_styles_to_layer(layer_empty_poly)
    layer_empty_poly.commitChanges()
    add_layer(layer_empty_poly)

    styled_layer: StyledLayer = StyledLayer('asd', layer_empty_poly.id(), list(converter.legend.values()))
    with open(plugin_test_data_path('config', 'config_simple_poly.json')) as f:
        config = Config.from_dict(json.load(f))

    writer = DatapackageWriter(config)
    snapshot_config = config.snapshots[0]
    name = list(snapshot_config.keys())[0]
    snapshot_config = list(snapshot_config.values())[0]
    snapshot = writer.create_snapshot(name, snapshot_config, [styled_layer])
    expected_snapshot_dict = get_test_json('snapshots', 'categorized_poly.json')
    assert snapshot.to_dict() == expected_snapshot_dict


def update_fields(converter: StylesToAttributes, layer: QgsVectorLayer):
    dp: QgsVectorDataProvider = layer.dataProvider()
    dp.addAttributes(converter.fields)
    layer.updateFields()
