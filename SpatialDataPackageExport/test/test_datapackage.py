# type: ignore
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
import shutil
from pathlib import Path

import pytest
from qgis.core import QgsProcessingFeedback, QgsVectorDataProvider, QgsVectorLayer

from ..core.datapackage import DataPackageHandler
from ..core.styles2attributes import StylesToAttributes
from ..core.utils import load_json
from ..definitions.types import StyleType
from ..model.config import Config
from ..model.snapshot import Contributor, Snapshot
from ..model.styled_layer import StyledLayer
from ..qgis_plugin_tools.tools.resources import plugin_test_data_path
from .conftest import add_layer
from .utils import get_test_json


def mock_auth(*args, **kwargs):
    return "test_author"


def test_categorized_poly(
    new_project, categorized_poly, layer_empty_poly, odc_1_0_license, monkeypatch
):
    # Mock get_project_author
    monkeypatch.setattr(DataPackageHandler, "get_project_author", mock_auth)

    converter = StylesToAttributes(
        categorized_poly, categorized_poly.name(), QgsProcessingFeedback()
    )
    update_fields(converter, layer_empty_poly)
    layer_empty_poly.startEditing()
    converter.extract_styles_to_layer(layer_empty_poly)
    layer_empty_poly.commitChanges()
    add_layer(layer_empty_poly)
    metadata = layer_empty_poly.metadata()
    metadata.setKeywords({"test": ["kw1", "kw2"], "test2": ["kw3"]})
    metadata.setLicenses(
        ["Creative Commons CC Zero", "Creative Commons Attribution Share-Alike 4.0"]
    )
    layer_empty_poly.setMetadata(metadata)

    styled_layer: StyledLayer = StyledLayer(
        "asd",
        layer_empty_poly.id(),
        list(converter.legend.values()),
        StyleType.SimpleStyle,
    )

    config_data = load_json(plugin_test_data_path("config", "config_simple_poly.json"))
    config = Config.from_dict(config_data)

    handler = DataPackageHandler.create(config)
    snapshot_config = config.snapshots[0]
    name = list(snapshot_config.keys())[0]
    snapshot_config = list(snapshot_config.values())[0]
    snapshot_config.description = "test description"
    snapshot_config.title = "test title"

    snapshot = handler.create_snapshot(
        name, snapshot_config, [styled_layer], odc_1_0_license
    )
    expected_snapshot_dict = get_test_json(
        "snapshots", "categorized_poly_custom_config.json"
    )
    assert snapshot.to_dict() == expected_snapshot_dict


def test_gratuated_poly(new_project, gratuated_poly, layer_empty_poly, monkeypatch):
    # Mock get_project_author
    monkeypatch.setattr(DataPackageHandler, "get_project_author", mock_auth)

    converter = StylesToAttributes(
        gratuated_poly, gratuated_poly.name(), QgsProcessingFeedback()
    )
    update_fields(converter, layer_empty_poly)
    layer_empty_poly.startEditing()
    converter.extract_styles_to_layer(layer_empty_poly)
    layer_empty_poly.commitChanges()
    add_layer(layer_empty_poly)
    metadata = layer_empty_poly.metadata()
    layer_empty_poly.setMetadata(metadata)

    styled_layer: StyledLayer = StyledLayer(
        "asd",
        layer_empty_poly.id(),
        list(converter.legend.values()),
        StyleType.SimpleStyle,
    )

    config_data = load_json(plugin_test_data_path("config", "config_simple_poly.json"))
    config = Config.from_dict(config_data)
    config.get_snapshot_config().contributors = [
        Contributor("author", DataPackageHandler.get_project_author())
    ]

    handler = DataPackageHandler.create(config)
    snapshot_config = config.snapshots[0]
    name = list(snapshot_config.keys())[0]
    snapshot_config = list(snapshot_config.values())[0]
    snapshot_config.description = "test description"
    snapshot_config.title = "test title"

    snapshot = handler.create_snapshot(name, snapshot_config, [styled_layer])
    expected_snapshot_dict = get_test_json("snapshots", "gratuated_poly.json")
    print(json.dumps(snapshot.to_dict()))

    assert snapshot.to_dict() == expected_snapshot_dict


def test_points_with_radius(new_project, points_with_radius, layer_empty_points):
    converter = StylesToAttributes(
        points_with_radius,
        points_with_radius.name(),
        QgsProcessingFeedback(),
        primary_layer=True,
    )
    update_fields(converter, layer_empty_points)
    layer_empty_points.startEditing()
    converter.extract_styles_to_layer(layer_empty_points)
    layer_empty_points.commitChanges()
    add_layer(layer_empty_points)

    styled_layer: StyledLayer = StyledLayer(
        "point-sample-snapshot",
        layer_empty_points.id(),
        list(converter.legend.values()),
        StyleType.PointStyle,
    )

    config_data = load_json(
        plugin_test_data_path("config", "config_points_with_radius.json")
    )
    config = Config.from_dict(config_data)

    handler = DataPackageHandler.create(config)
    snapshot_config = config.snapshots[0]
    name = list(snapshot_config.keys())[0]
    snapshot_config = list(snapshot_config.values())[0]
    snapshot = handler.create_snapshot(name, snapshot_config, [styled_layer])
    expected_snapshot_dict = get_test_json("snapshots", "points_with_radius.json")
    assert snapshot.to_dict() == expected_snapshot_dict


def test_export_of_non_ascii_layer(
    new_project, layer_with_non_ascii_simple_style, layer_empty_points
):
    converter = StylesToAttributes(
        layer_with_non_ascii_simple_style,
        layer_with_non_ascii_simple_style.name(),
        QgsProcessingFeedback(),
        primary_layer=True,
    )
    update_fields(converter, layer_empty_points)
    layer_empty_points.startEditing()
    converter.extract_styles_to_layer(layer_empty_points)
    layer_empty_points.commitChanges()
    add_layer(layer_empty_points)

    styled_layer = StyledLayer(
        "point-sample-snapshot",
        layer_empty_points.id(),
        list(converter.legend.values()),
        StyleType.PointStyle,
    )

    config_data = load_json(plugin_test_data_path("config", "config_non_ascii.json"))
    config = Config.from_dict(config_data)

    snapshot_config = config.snapshots[0]
    name = list(snapshot_config.keys())[0]
    snapshot_config = list(snapshot_config.values())[0]

    handler = DataPackageHandler.create(config)
    snapshot = handler.create_snapshot(name, snapshot_config, [styled_layer])
    snapshot_dict = snapshot.to_dict()
    expected_snapshot_dict = get_test_json("snapshots", "with_non_ascii_chars.json")

    assert snapshot_dict == expected_snapshot_dict


def test_styled_layer(tmp_path, points_with_radius):
    styled_layer: StyledLayer = StyledLayer(
        "point-sample-snapshot", points_with_radius.id(), [], StyleType.PointStyle
    )
    styled_layer.save_as_geojson(tmp_path)
    assert Path(tmp_path, "point-sample-snapshot.geojson").exists()


def test_config_saving_and_loading(new_project):
    config_data = load_json(plugin_test_data_path("config", "config_simple_poly.json"))
    config = Config.from_dict(config_data)

    config.snapshots = [{"test": config.get_snapshot_config()}]
    DataPackageHandler.save_settings_to_project("test", config)

    available_configs = DataPackageHandler.get_available_settings_from_project()
    assert "test" in available_configs
    loaded_conf = available_configs["test"]
    assert loaded_conf.to_dict() == config.to_dict()


@pytest.mark.parametrize(
    "snapshot_name",
    (
        ("categorized_poly.json"),
        ("categorized_poly_custom_config.json"),
        ("gratuated_poly.json"),
        ("points_with_radius.json"),
        ("snapshot_categorized_poly.json"),
        ("with_non_ascii_chars.json"),
    ),
)
def test_load_snapshot_from_file(new_project, tmp_path, snapshot_name):
    p = tmp_path / "snapshot.json"
    shutil.copy(Path(plugin_test_data_path("snapshots", snapshot_name)), p)

    snapshot_data = load_json(p)
    snapshot = Snapshot.from_dict(snapshot_data)

    config = DataPackageHandler.load_snapshot_from_file(p)

    assert config.project_name == snapshot.name

    # TODO: Take in use again when implementing #49
    """
    assert len(config.snapshots[0][snapshot.name].resources) == len(
        snapshot.layer_resources
    )
    assert all(
        [
            (tmp_path / f"{resource.name}.geojson").exists()
            for resource in snapshot.layer_resources
        ]
    )
    """


def update_fields(converter: StylesToAttributes, layer: QgsVectorLayer):
    dp: QgsVectorDataProvider = layer.dataProvider()
    dp.addAttributes(converter.fields)
    layer.updateFields()
