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
from typing import Dict, Tuple

from .conftest import IFACE, CANVAS
from ..qgis_plugin_tools.tools.resources import plugin_test_data_path


def get_symbols_and_legend(name: str) -> Tuple[Dict, Dict]:
    f_name = f'{name}.json'
    with open(plugin_test_data_path('symbols', f_name)) as f:
        symbols = json.load(f)
    symbols = {int(key): val for key, val in symbols.items()}

    with open(plugin_test_data_path('legend', f_name)) as f:
        legend = json.load(f)
    return symbols, legend


def get_existing_layer_names():
    return {layer.name() for layer in IFACE.getMockLayers() + CANVAS.layers()}
