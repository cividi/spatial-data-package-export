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
import os
import tempfile
from dataclasses import dataclass
from typing import List, Dict

from qgis.core import QgsVectorFileWriter, QgsCoordinateReferenceSystem, QgsProject

from .snapshot import Legend
from ..qgis_plugin_tools.tools.resources import resources_path


@dataclass
class StyledLayer:
    resource_name: str
    layer_id: str
    legend: List[Legend]

    @property
    def layer(self):
        return QgsProject.instance().mapLayer(self.layer_id)

    def get_geojson_data(self) -> Dict:
        source = self.layer.source()
        if source.lower().endswith('.geojson') or source.lower().endswith('.json'):
            with open(source) as f:
                data = json.load(f)
        else:
            with tempfile.TemporaryDirectory(dir=resources_path()) as tmpdirname:
                f_name = os.path.join(tmpdirname, f'{self.resource_name}.geojson')
                _writer = QgsVectorFileWriter.writeAsVectorFormat(self.layer, f_name, "utf-8",
                                                                  QgsCoordinateReferenceSystem("EPSG:4326"),
                                                                  driverName="GeoJSON")
                with open(f_name) as f:
                    data = json.load(f)
        return data
