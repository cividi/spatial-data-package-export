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
import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Union

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsProject,
    QgsVectorFileWriter,
    QgsVectorLayer,
)

from ..core.exceptions import DataPackageException
from ..core.utils import load_json
from ..definitions.configurable_settings import Settings
from ..definitions.types import StyleType
from ..qgis_plugin_tools.tools.custom_logging import bar_msg
from ..qgis_plugin_tools.tools.i18n import tr
from ..qgis_plugin_tools.tools.resources import plugin_name, resources_path
from .snapshot import Legend, License

LOGGER = logging.getLogger(plugin_name())


class StyledLayer:
    def __init__(
        self,
        resource_name: str,
        layer_id: str,
        legend: List[Legend],
        style_type: Union[str, StyleType],
    ) -> None:
        self.resource_name = resource_name
        self.layer_id = layer_id
        self.legend = legend
        self.style_type: StyleType = (
            StyleType[style_type] if isinstance(style_type, str) else style_type
        )

    @property
    def layer(self) -> QgsVectorLayer:
        return QgsProject.instance().mapLayer(self.layer_id)

    def get_keywords(self) -> List[str]:
        keyword_lists = self.layer.metadata().keywords().values()
        return [keyword for keyword_list in keyword_lists for keyword in keyword_list]

    def get_licenses(self) -> List[License]:
        licenses = self.layer.metadata().licenses()
        available_licenses = Settings.licences.get()
        return [
            License(
                available_licenses.get(license_, {}).get("url", ""),
                available_licenses.get(license_, {}).get("type", ""),
                license_,
            )
            for license_ in licenses
        ]

    def get_geojson_data(self) -> Dict:
        source = self.layer.source()
        if source.lower().endswith(".geojson") or source.lower().endswith(".json"):
            data = load_json(source)
        else:
            with tempfile.TemporaryDirectory(dir=resources_path()) as tmpdirname:
                json_path = self.save_as_geojson(Path(tmpdirname))
                data = load_json(json_path)
        return data

    def save_as_geojson(self, output_path: Path) -> Path:
        output_file = Path(output_path, f"{self.resource_name}.geojson")

        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "GeoJSON"
        options.fileEncoding = "utf-8"

        src_crs = self.layer.crs()
        dst_crs = QgsCoordinateReferenceSystem("EPSG:4326")
        options.ct = QgsCoordinateTransform(src_crs, dst_crs, QgsProject.instance())

        if hasattr(QgsVectorFileWriter, "writeAsVectorFormatV3"):
            writer_, msg, _, _ = QgsVectorFileWriter.writeAsVectorFormatV3(
                self.layer,
                str(output_file),
                QgsProject.instance().transformContext(),
                options,
            )
        else:
            writer_, msg = QgsVectorFileWriter.writeAsVectorFormatV2(
                self.layer,
                str(output_file),
                QgsProject.instance().transformContext(),
                options,
            )
        if msg != "":
            raise DataPackageException(
                tr("Could not write layer {} to disk", output_file),
                bar_msg(tr("Check the log for more details")),
            )

        return output_file
