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

import pytest
from qgis.core import QgsProject, QgsVectorLayer, QgsVectorDataProvider

from ..model.snapshot import License
from ..qgis_plugin_tools.testing.utilities import get_qgis_app
from ..qgis_plugin_tools.tools.resources import plugin_test_data_path

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

QGIS_INSTANCE = QgsProject.instance()


@pytest.fixture
def new_project() -> None:
    """Initializes new iface project"""
    yield IFACE.newProject()


@pytest.fixture(scope='session')
def test_gpkg():
    return plugin_test_data_path('test_data_4326.gpkg')


@pytest.fixture
def layer_simple_poly(test_gpkg):
    name = 'simple_poly'
    layer = get_layer(name, test_gpkg)
    return layer


@pytest.fixture
def layer_points(test_gpkg):
    name = 'points_with_radius'
    layer = get_layer(name, test_gpkg)
    return layer


@pytest.fixture
def layer_lines(test_gpkg):
    name = 'simple_lines'
    layer = get_layer(name, test_gpkg)
    return layer


@pytest.fixture
def categorized_poly(layer_simple_poly):
    add_layer(layer_simple_poly)
    set_styles(layer_simple_poly, 'categorized_poly.qml')
    return layer_simple_poly


@pytest.fixture
def centroid_poly(layer_simple_poly):
    add_layer(layer_simple_poly)
    set_styles(layer_simple_poly, 'centroid_poly.qml')
    return layer_simple_poly


@pytest.fixture
def gratuated_poly(layer_simple_poly):
    add_layer(layer_simple_poly)
    set_styles(layer_simple_poly, 'gratuated_poly.qml')
    return layer_simple_poly


@pytest.fixture
def points_with_radius(layer_points):
    add_layer(layer_points)
    set_styles(layer_points, 'points_with_radius.qml')
    return layer_points


@pytest.fixture
def points_with_no_fill_and_no_stroke(layer_points):
    add_layer(layer_points)
    set_styles(layer_points, 'points_with_no_fill_and_no_stroke.qml')
    return layer_points


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory(dir=plugin_test_data_path()) as tmpdirname:
        yield tmpdirname


@pytest.fixture
def layer_empty_poly(tmp_dir, layer_simple_poly):
    dp: QgsVectorDataProvider = layer_simple_poly.dataProvider()
    layer = QgsVectorLayer('Polygon', 'test_poly', 'memory')
    layer.setCrs(dp.crs())
    assert layer.isValid()
    return layer


@pytest.fixture
def layer_empty_points(tmp_dir, layer_points):
    dp: QgsVectorDataProvider = layer_points.dataProvider()
    layer = QgsVectorLayer('Point', 'test_point', 'memory')
    layer.setCrs(dp.crs())
    verify_layer_copy(layer, layer_points)
    return layer


@pytest.fixture
def layer_empty_lines(tmp_dir, layer_lines):
    dp: QgsVectorDataProvider = layer_lines.dataProvider()
    layer = QgsVectorLayer('LineString', 'test_lines', 'memory')
    layer.setCrs(dp.crs())
    verify_layer_copy(layer, layer_lines)
    return layer


@pytest.fixture
def odc_1_0_license():
    return License("https://opendatacommons.org/licenses/by/1.0/", "ODC-By-1.0",
                   "Open Data Commons Attribution License")


# Helper functions

def verify_layer_copy(layer, orig_layer):
    assert layer.wkbType() == orig_layer.wkbType()
    assert layer.isValid()


def get_layer(name: str, gpkg):
    layer = QgsVectorLayer(f'{gpkg}|layername={name}', name, 'ogr')
    assert layer.isValid()
    return layer


def set_styles(layer_simple_poly, style_file):
    style_file = plugin_test_data_path('style', style_file)
    msg, succeeded = layer_simple_poly.loadNamedStyle(style_file)
    assert succeeded, msg


def add_layer(layer: QgsVectorLayer) -> None:
    initial_layers = QGIS_INSTANCE.mapLayers()
    QGIS_INSTANCE.addMapLayer(layer, False)
    assert len(QGIS_INSTANCE.mapLayers()) > len(initial_layers)
