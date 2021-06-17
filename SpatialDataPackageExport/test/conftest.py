# type: ignore
# flake8: noqa ANN201, ANN001

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

import tempfile
from pathlib import Path

import pytest
from qgis.core import QgsProject, QgsVectorDataProvider, QgsVectorLayer

from ..model.snapshot import License
from ..qgis_plugin_tools.testing.utilities import get_qgis_app
from ..qgis_plugin_tools.tools.resources import plugin_test_data_path

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

QGIS_INSTANCE = QgsProject.instance()


@pytest.fixture
def new_project() -> None:
    """Initializes new iface project"""
    yield IFACE.newProject()


@pytest.fixture(scope="session")
def test_gpkg():
    return plugin_test_data_path("test_data_4326.gpkg")


@pytest.fixture
def layer_simple_poly(test_gpkg):
    return get_layer("simple_poly", test_gpkg)


@pytest.fixture
def layer_points(test_gpkg):
    return get_layer("points_with_radius", test_gpkg)


@pytest.fixture
def layer_lines(test_gpkg):
    return get_layer("simple_lines", test_gpkg)


@pytest.fixture
def points_with_no_fill_and_no_stroke_with_style_attrs(test_gpkg):
    return get_layer("points_with_radius_and_styles", test_gpkg)


@pytest.fixture
def graduated_poly_attrs(test_gpkg):
    return get_layer("graduated_poly", test_gpkg)


@pytest.fixture
def simple_lines_attrs(test_gpkg):
    return get_layer("simple_lines_w_styles", test_gpkg)


@pytest.fixture
def layer_with_non_ascii_chars(test_gpkg):
    return get_layer("layer_with_non_ascii_chars", test_gpkg)


@pytest.fixture
def categorized_poly(layer_simple_poly):
    add_layer(layer_simple_poly)
    set_styles(layer_simple_poly, "categorized_poly.qml")
    return layer_simple_poly


@pytest.fixture
def centroid_poly(layer_simple_poly):
    add_layer(layer_simple_poly)
    set_styles(layer_simple_poly, "centroid_poly.qml")
    return layer_simple_poly


@pytest.fixture
def gratuated_poly(layer_simple_poly):
    add_layer(layer_simple_poly)
    set_styles(layer_simple_poly, "gratuated_poly.qml")
    return layer_simple_poly


@pytest.fixture
def points_with_radius(layer_points):
    add_layer(layer_points)
    set_styles(layer_points, "points_with_radius.qml")
    return layer_points


@pytest.fixture
def layer_with_non_ascii_simple_style(layer_with_non_ascii_chars):
    add_layer(layer_with_non_ascii_chars)
    set_styles(layer_with_non_ascii_chars, "simple_points.qml")
    return layer_with_non_ascii_chars


@pytest.fixture
def points_with_no_fill_and_no_stroke(layer_points):
    add_layer(layer_points)
    set_styles(layer_points, "points_with_no_fill_and_no_stroke.qml")
    return layer_points


@pytest.fixture
def points_with_no_fill_and_no_stroke_rule_based(layer_points):
    add_layer(layer_points)
    set_styles(layer_points, "points_with_no_fill_and_no_stroke_rule_based.qml")
    return layer_points


@pytest.fixture
def layer_empty_poly(layer_simple_poly):
    dp: QgsVectorDataProvider = layer_simple_poly.dataProvider()
    layer = QgsVectorLayer("Polygon", "test_poly", "memory")
    layer.setCrs(dp.crs())
    assert layer.isValid()
    return layer


@pytest.fixture
def layer_empty_points(layer_points):
    dp: QgsVectorDataProvider = layer_points.dataProvider()
    layer = QgsVectorLayer("Point", "test_point", "memory")
    layer.setCrs(dp.crs())
    verify_layer_copy(layer, layer_points)
    return layer


@pytest.fixture
def layer_empty_lines(layer_lines):
    dp: QgsVectorDataProvider = layer_lines.dataProvider()
    layer = QgsVectorLayer("LineString", "test_lines", "memory")
    layer.setCrs(dp.crs())
    verify_layer_copy(layer, layer_lines)
    return layer


@pytest.fixture
def odc_1_0_license():
    return License(
        "https://opendatacommons.org/licenses/by/1.0/",
        "ODC-By-1.0",
        "Open Data Commons Attribution License",
    )


@pytest.fixture
def tmp_path(tmpdir):
    return Path(tmpdir)


# Helper functions
def verify_layer_copy(layer, orig_layer):
    assert layer.wkbType() == orig_layer.wkbType()
    assert layer.isValid()


def get_layer(name: str, gpkg):
    layer = QgsVectorLayer(f"{gpkg}|layername={name}", name, "ogr")
    assert layer.isValid()
    return layer


def set_styles(layer_simple_poly, style_file):
    style_file = plugin_test_data_path("style", style_file)
    msg, succeeded = layer_simple_poly.loadNamedStyle(style_file)
    assert succeeded, msg


def add_layer(layer: QgsVectorLayer) -> None:
    initial_layers = QGIS_INSTANCE.mapLayers()
    QGIS_INSTANCE.addMapLayer(layer, False)
    assert len(QGIS_INSTANCE.mapLayers()) > len(initial_layers)
