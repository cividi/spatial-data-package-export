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
import logging
from typing import List, Optional, Tuple

from .utils import load_json
from ..definitions.configurable_settings import Settings
from ..model.config import Config, SnapshotConfig
from ..model.snapshot import Snapshot, Resource, Legend
from ..model.styled_layer import StyledLayer
from ..qgis_plugin_tools.tools.resources import plugin_name
from ..qgis_plugin_tools.tools.settings import get_setting

LOGGER = logging.getLogger(plugin_name())


class DatapackageWriter:

    def __init__(self, config: Config, snapshot_template: Optional[Snapshot] = None,
                 legend_template: Optional[Legend] = None) -> None:
        self.config = config

        snap_temp, leg_temp = self._load_default_template()
        self.snapshot_template: Snapshot = snapshot_template if snapshot_template is not None else snap_temp
        self.snapshot_template.name = config.project_name
        self.legend_template: Legend = legend_template if legend_template is not None else leg_temp

    def _load_default_template(self) -> Tuple[Snapshot, Legend]:
        template_path = get_setting(Settings.snapshot_template.name, Settings.snapshot_template.value, str)
        template = load_json(template_path)

        return Snapshot.from_dict(template['snapshot']), Legend.from_dict(template['legend'])

    def create_snapshot(self, snapshot_name: str, snapshot_config: SnapshotConfig, styled_layers: List[StyledLayer]):
        snapshot = Snapshot.from_dict(self.snapshot_template.to_dict())
        snapshot.name = snapshot_name
        snapshot.title = snapshot_config.title
        snapshot.views[0].spec.bounds = snapshot_config.bounds
        snapshot.views[0].spec.title = snapshot_config.title
        snapshot.views[0].spec.description = snapshot_config.description
        snapshot.description = snapshot_config.description
        snapshot.keywords = snapshot_config.keywords
        snapshot.sources = snapshot_config.sources
        snapshot.gemeindescan_meta = snapshot_config.gemeindescan_meta

        LOGGER.debug('Updating resources')
        initial_resources = snapshot.resources
        snapshot.resources = []

        for styled_layer in styled_layers:
            resource = Resource(styled_layer.resource_name, mediatype=styled_layer.style_type.media_type,
                                data=styled_layer.get_geojson_data())
            snapshot.resources.append(resource)

        snapshot.resources += initial_resources
        snapshot.views[0].resources = [res.name for res in snapshot.resources]

        LOGGER.debug('Updating legends')
        for styled_layer in styled_layers:
            snapshot.views[0].spec.legend += styled_layer.legend

        return snapshot
