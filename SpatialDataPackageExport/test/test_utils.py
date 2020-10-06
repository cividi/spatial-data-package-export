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
import pytest
from qgis.core import QgsRectangle, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject

from ..core.utils import extent_to_datapackage_bounds, datapackage_bounds_to_extent


@pytest.fixture
def bounds():
    return ["geo:59.599242,21.540037", "geo:61.029195,31.618383"]


@pytest.fixture
def extent():
    return QgsRectangle(21.54003660, 59.59924232, 31.61838268, 61.02919460)


@pytest.fixture
def extent2():
    return QgsRectangle(21.55787082699999857, 59.40132140899999769, 27.46496583600000108, 62.1826135000000022)


@pytest.fixture
def rounded_extent():
    return QgsRectangle(21.540037, 59.59924, 31.618383, 61.029195)


def test_extent_to_datapackage_bounds(extent, bounds):
    got_bounds = extent_to_datapackage_bounds(extent, 6)
    assert got_bounds == bounds


@pytest.mark.skip('Rounding issues...')
def test_datapackage_bounds_to_extent(bounds, rounded_extent):
    extent = datapackage_bounds_to_extent(bounds)
    assert extent == rounded_extent


def test_transformations(extent):
    extent_crs = QgsCoordinateReferenceSystem('EPSG:4326')
    source_crs = QgsCoordinateReferenceSystem('EPSG:3067')
    transform = QgsCoordinateTransform(extent_crs, source_crs, QgsProject.instance())
    extent_transformed = transform.transformBoundingBox(extent)
    assert not extent_transformed == extent
