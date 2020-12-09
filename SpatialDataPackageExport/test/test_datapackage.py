#  Gispo Ltd., hereby disclaims all copyright interest in the program SpatialDataPackageExport
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
import json
from pathlib import Path

from qgis.core import QgsProcessingFeedback, QgsVectorLayer, QgsVectorDataProvider

from .conftest import add_layer
from .utils import get_test_json
from ..core.datapackage import DataPackageHandler
from ..core.styles2attributes import StylesToAttributes
from ..definitions.types import StyleType
from ..model.config import Config
from ..model.styled_layer import StyledLayer
from ..qgis_plugin_tools.tools.resources import plugin_test_data_path


def mock_auth(*args, **kwargs):
    return 'test_author'


def test_categorized_poly(new_project, categorized_poly, layer_empty_poly, odc_1_0_license, monkeypatch):
    # Mock get_project_author
    monkeypatch.setattr(DataPackageHandler, 'get_project_author', mock_auth)

    converter = StylesToAttributes(categorized_poly, categorized_poly.name(), QgsProcessingFeedback())
    update_fields(converter, layer_empty_poly)
    layer_empty_poly.startEditing()
    converter.extract_styles_to_layer(layer_empty_poly)
    layer_empty_poly.commitChanges()
    add_layer(layer_empty_poly)
    metadata = layer_empty_poly.metadata()
    metadata.setKeywords({'test': ['kw1', 'kw2'], 'test2': ['kw3']})
    metadata.setLicenses(['Creative Commons CC Zero', 'Creative Commons Attribution Share-Alike 4.0'])
    layer_empty_poly.setMetadata(metadata)

    styled_layer: StyledLayer = StyledLayer('asd', layer_empty_poly.id(), list(converter.legend.values()),
                                            StyleType.SimpleStyle)
    with open(plugin_test_data_path('config', 'config_simple_poly.json')) as f:
        config = Config.from_dict(json.load(f))

    handler = DataPackageHandler.create(config)
    snapshot_config = config.snapshots[0]
    name = list(snapshot_config.keys())[0]
    snapshot_config = list(snapshot_config.values())[0]
    snapshot_config.description = 'test description'
    snapshot_config.title = 'test title'

    snapshot = handler.create_snapshot(name, snapshot_config, [styled_layer], odc_1_0_license)
    expected_snapshot_dict = get_test_json('snapshots', 'categorized_poly_custom_config.json')
    assert snapshot.to_dict() == expected_snapshot_dict


def test_gratuated_poly(new_project, gratuated_poly, layer_empty_poly, monkeypatch):
    # Mock get_project_author
    monkeypatch.setattr(DataPackageHandler, 'get_project_author', mock_auth)

    converter = StylesToAttributes(gratuated_poly, gratuated_poly.name(), QgsProcessingFeedback())
    update_fields(converter, layer_empty_poly)
    layer_empty_poly.startEditing()
    converter.extract_styles_to_layer(layer_empty_poly)
    layer_empty_poly.commitChanges()
    add_layer(layer_empty_poly)
    metadata = layer_empty_poly.metadata()
    layer_empty_poly.setMetadata(metadata)

    styled_layer: StyledLayer = StyledLayer('asd', layer_empty_poly.id(), list(converter.legend.values()),
                                            StyleType.SimpleStyle)
    with open(plugin_test_data_path('config', 'config_simple_poly.json')) as f:
        config = Config.from_dict(json.load(f))

    handler = DataPackageHandler.create(config)
    snapshot_config = config.snapshots[0]
    name = list(snapshot_config.keys())[0]
    snapshot_config = list(snapshot_config.values())[0]
    snapshot_config.description = 'test description'
    snapshot_config.title = 'test title'

    snapshot = handler.create_snapshot(name, snapshot_config, [styled_layer])
    expected_snapshot_dict = get_test_json('snapshots', 'gratuated_poly.json')
    print(json.dumps(snapshot.to_dict()))

    assert snapshot.to_dict() == expected_snapshot_dict


def test_points_with_radius(new_project, points_with_radius, layer_empty_points, monkeypatch):
    # Mock get_project_author
    monkeypatch.setattr(DataPackageHandler, 'get_project_author', mock_auth)

    converter = StylesToAttributes(points_with_radius, points_with_radius.name(), QgsProcessingFeedback(),
                                   primary_layer=True)
    update_fields(converter, layer_empty_points)
    layer_empty_points.startEditing()
    converter.extract_styles_to_layer(layer_empty_points)
    layer_empty_points.commitChanges()
    add_layer(layer_empty_points)

    styled_layer: StyledLayer = StyledLayer('point-sample-snapshot', layer_empty_points.id(),
                                            list(converter.legend.values()),
                                            StyleType.PointStyle)
    with open(plugin_test_data_path('config', 'config_points_with_radius.json')) as f:
        config = Config.from_dict(json.load(f))

    handler = DataPackageHandler.create(config)
    snapshot_config = config.snapshots[0]
    name = list(snapshot_config.keys())[0]
    snapshot_config = list(snapshot_config.values())[0]
    snapshot = handler.create_snapshot(name, snapshot_config, [styled_layer])
    expected_snapshot_dict = get_test_json('snapshots', 'points_with_radius.json')
    assert snapshot.to_dict() == expected_snapshot_dict


def test_styled_layer(tmp_path, points_with_radius):
    styled_layer: StyledLayer = StyledLayer('point-sample-snapshot', points_with_radius.id(),
                                            [],
                                            StyleType.PointStyle)
    styled_layer.save_as_geojson(tmp_path)
    assert Path(tmp_path, 'point-sample-snapshot.geojson').exists()


def test_config_saving_and_loading(new_project):
    with open(plugin_test_data_path('config', 'config_simple_poly.json')) as f:
        config = Config.from_dict(json.load(f))
    config.snapshots = [{'test': config.get_snapshot_config()}]
    DataPackageHandler.save_settings_to_project('test', config)

    available_configs = DataPackageHandler.get_available_settings_from_project()
    assert 'test' in available_configs
    loaded_conf = available_configs['test']
    assert loaded_conf.to_dict() == config.to_dict()


def update_fields(converter: StylesToAttributes, layer: QgsVectorLayer):
    dp: QgsVectorDataProvider = layer.dataProvider()
    dp.addAttributes(converter.fields)
    layer.updateFields()
