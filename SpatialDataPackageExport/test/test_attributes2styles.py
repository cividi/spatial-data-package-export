#  Gispo Ltd., hereby disclaims all copyright interest in the program
#  SpatialDataPackageExport
#  Copyright (C) 2020-2021 Gispo Ltd (https://www.gispo.fi/).
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


# type: ignore
# noqa
import json

import pytest
import xmltodict
from qgis.core import QgsVectorLayer

from ..core.attributes2styles import AttributesToStyles
from ..definitions.symbols import SymbolType
from ..qgis_plugin_tools.tools.resources import plugin_test_data_path
from .utils import get_legend


@pytest.mark.parametrize(
    "src_layer,legend_name,expected_symbol_type,expected_style_file",
    (
        (
            "points_with_no_fill_and_no_stroke_with_style_attrs",
            "points_with_no_fill_and_no_stroke",
            "categorizedSymbol",
            "points_with_radius_reverse_engineered.qml",
        ),
    ),
)
def test_set_style_based_on_attributes(
    new_project,
    tmp_path,
    request,
    src_layer,
    legend_name,
    expected_symbol_type,
    expected_style_file,
):
    src_layer: QgsVectorLayer = request.getfixturevalue(src_layer)
    styler = AttributesToStyles(src_layer, get_legend(legend_name))

    assert styler.symbol_type == SymbolType[expected_symbol_type]
    styler.set_style_based_on_attributes()

    style_path = tmp_path / "style.qml"

    msg, succeeded = src_layer.saveNamedStyle(str(style_path))
    assert succeeded, msg
    assert style_path.exists()

    with open(plugin_test_data_path("style", expected_style_file)) as f:
        expected_content = json.loads(
            json.dumps(xmltodict.parse(f.read())["qgis"]["renderer-v2"])
        )
    with open(style_path) as f:
        style_content = json.loads(
            json.dumps(xmltodict.parse(f.read())["qgis"]["renderer-v2"])
        )

    assert style_content == expected_content
