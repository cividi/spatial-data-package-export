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
from typing import List

from qgis.core import QgsRectangle


def load_json(template_path):
    with open(template_path) as f:
        template = json.load(f)
    return template


def extent_to_datapackage_bounds(extent: QgsRectangle, precision: int) -> List[str]:
    """
    Datapackage bounds are in format ["geo:ymin,xmin", "geo:ymax,xmax"]
    """
    rnd = lambda c: round(c, precision)

    return [f'geo:{rnd(extent.yMinimum())},{rnd(extent.xMinimum())}',
            f'geo:{rnd(extent.yMaximum())},{rnd(extent.xMaximum())}']


def datapackage_bounds_to_extent(bounds: List[str]) -> QgsRectangle:
    """
    Datapackage bounds are in format ["geo:ymin,xmin", "geo:ymax,xmax"]
    """
    min_values = [float(v) for v in bounds[0].replace('geo:', '').split(',')]
    max_values = [float(v) for v in bounds[1].replace('geo:', '').split(',')]
    return QgsRectangle(min_values[1], min_values[0], max_values[1], max_values[0])
