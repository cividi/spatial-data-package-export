# type: ignore
#  Gispo Ltd., hereby disclaims all copyright interest in the program
#  SpatialDataPackageExport
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

from typing import Dict, List, Set, Tuple

from ..core.utils import load_json
from ..model.snapshot import Legend
from ..qgis_plugin_tools.tools.resources import plugin_test_data_path
from .conftest import CANVAS, IFACE


def get_symbols_and_legend(name: str) -> Tuple[Dict, Dict]:
    f_name = f"{name}.json"

    symbols = load_json(plugin_test_data_path("symbols", f_name))
    symbols = {int(key): val for key, val in symbols.items()}

    legend = load_json(plugin_test_data_path("legend", f_name))

    return symbols, legend


def get_legend(name: str) -> List[Legend]:
    _, legend = get_symbols_and_legend(name)
    return [Legend.from_dict(lgnd) for lgnd in legend]


def get_test_json(*args: str) -> Dict:
    f_path = plugin_test_data_path(*args)
    if not (f_path.endswith(".json") or f_path.endswith(".geojson")):
        raise ValueError("Invalid path")

    data = load_json(f_path)

    return data


def get_existing_layer_names() -> Set[str]:
    return {layer.name() for layer in IFACE.getMockLayers() + CANVAS.layers()}
