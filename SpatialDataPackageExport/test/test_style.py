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
#
import pytest

from ..core.exceptions import StyleException
from ..definitions.style import PointStyle, Style


def test__hex_to_rgb():
    rgb = Style._hex_to_rgb("#B4FBB8", 1.0)
    assert rgb == "180,251,184,255"


def test__hex_to_rgb_with_opacity():
    rgb = Style._hex_to_rgb("#B4FBB8", 0.6)
    assert rgb == "180,251,184,153"


def test_rgb_extract():
    hex, alpha = Style.rgb_extract("180,251,184,153")
    assert hex == "#b4fbb8"
    assert alpha == 0.6


def test_convert_to_pixels_mm():
    pixel_value = Style.convert_to_pixels(2, "MM")
    assert pixel_value == 7.1429


def test_convert_to_pixels_pixel():
    pixel_value = Style.convert_to_pixels(2, "Pixel")
    assert pixel_value == 2


def test_convert_to_pixels_pixel_invalid_format():
    with pytest.raises(StyleException):
        Style.convert_to_pixels(2, "invalid")


def test_fill_based_on_feature(points_with_no_fill_and_no_stroke_with_style_attrs):
    style = PointStyle()
    style.fill_based_on_feature(
        points_with_no_fill_and_no_stroke_with_style_attrs.getFeature(1)
    )
    assert style.to_dict() == {
        "color": "#101010",
        "fill": False,
        "fillColor": "#76a8c8",
        "fillOpacity": 0.0,
        "opacity": 0.8,
        "radius": 50.0,
        "stroke": True,
        "weight": 3.0,
    }
    style.fill_based_on_feature(
        points_with_no_fill_and_no_stroke_with_style_attrs.getFeature(2)
    )
    assert style.to_dict() == {
        "color": "#ffffff",
        "fill": True,
        "fillColor": "#a6cd6a",
        "fillOpacity": 0.8,
        "opacity": 0.0,
        "radius": 25.982587430391774,
        "stroke": False,
        "weight": 3.0,
    }
