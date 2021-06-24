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
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..definitions.configurable_settings import ProjectSettings, Settings
from ..model.config import Config, SnapshotConfig
from ..model.snapshot import Legend, License, Resource, Snapshot
from ..model.styled_layer import StyledLayer
from ..qgis_plugin_tools.tools.resources import plugin_name
from ..qgis_plugin_tools.tools.settings import get_project_setting, get_setting
from .utils import load_json

LOGGER = logging.getLogger(plugin_name())


class DataPackageHandler:
    PROJECT_AUTHOR = "project_author"

    def __init__(
        self, config: Config, snapshot_template: Snapshot, legend_template: Legend
    ) -> None:
        self.config = config
        self.snapshot_template: Snapshot = snapshot_template
        self.snapshot_template.name = config.project_name if config.project_name else ""
        self.legend_template: Legend = legend_template

    @staticmethod
    def create(
        config: Optional[Config] = None,
        snapshot_template: Optional[Snapshot] = None,
        legend_template: Optional[Legend] = None,
    ) -> "DataPackageHandler":
        """
        Creates an instance of  DataPackageHandler.
        Template locations can be configured via settings
        :param config:
        :param snapshot_template:
        :param legend_template:
        :return:
        """

        config = (
            config
            if config is not None
            else DataPackageHandler.load_config_from_template()
        )
        snap_temp, leg_temp = DataPackageHandler.load_default_template()
        snapshot_template = (
            snapshot_template if snapshot_template is not None else snap_temp
        )
        legend_template = legend_template if legend_template is not None else leg_temp
        return DataPackageHandler(config, snapshot_template, legend_template)

    @staticmethod
    def load_default_template() -> Tuple[Snapshot, Legend]:
        """
        Load default Snapshot and Legend templates
        """
        template_path = get_setting(
            Settings.snapshot_template.name, Settings.snapshot_template.value, str
        )
        template = load_json(template_path)

        return Snapshot.from_dict(template["snapshot"]), Legend.from_dict(
            template["legend"]
        )

    @staticmethod
    def load_config_from_template() -> Config:
        """
        Load default configuration template
        """
        template_path = get_setting(
            Settings.export_config_template.name,
            Settings.export_config_template.value,
            str,
        )
        return Config.from_dict(load_json(template_path))

    @staticmethod
    def get_available_settings_from_project() -> Dict[str, Config]:
        """
        Get Snapshot configurations stored in a project
        :return: Available Snapshot configurations
        """
        existing_confs: Dict[str, Config] = {
            name: Config.from_dict(config)
            for name, config in (
                ProjectSettings.snapshot_configs.get().items()  # type: ignore
            )
        }
        return existing_confs

    @staticmethod
    def save_settings_to_project(snapshot_name: str, config: Config) -> bool:
        """
        Saves snapshot configuration to the project settings
        :param snapshot_name: Name of the snapshot
        :param config: Snapshot configuration
        :return: Whether saving is successful or not
        """
        existing_confs = DataPackageHandler.get_available_settings_from_project()
        confs = {
            name: config
            for name, config in existing_confs.items()
            if name != snapshot_name
        }
        confs[snapshot_name] = config
        return ProjectSettings.snapshot_configs.set(
            {name: conf.to_dict() for name, conf in confs.items()}
        )

    @staticmethod
    def load_snapshot_from_file(snapshot_path: Path) -> Config:
        """Loads snapshot configuration and layers from the file"""
        snapshot = Snapshot.from_dict(load_json(str(snapshot_path)))

        # TODO: Take in use again when implementing #49
        """
        for resource in snapshot.layer_resources:
            if resource.data is not None:
                geojson = resource.data
                path = Path(snapshot_path.parent, f"{resource.name}.geojson")
                write_json(path, geojson)
                layer = QgsVectorLayer(str(path), resource.name)
                if layer.isValid() and layer.featureCount():
                    styler = AttributesToStyles(layer)
                    styler.set_style_based_on_attributes()
                    QgsProject.instance().addMapLayer(layer)
                else:
                    raise DataPackageException(
                        tr("The layer {} is not valid", resource.name),
                        bar_msg(
                            tr(
                                "Please check the snapshot and "
                                "make sure it contains valid GeoJSON"
                            )
                        ),
                    )
        """

        return Config.from_snapshot(snapshot)

    @staticmethod
    def get_project_author() -> str:
        """
        Get the author of the project
        :return: Author or the default value
        """
        return str(
            get_project_setting(DataPackageHandler.PROJECT_AUTHOR, "", internal=False)
        )

    def create_snapshot(
        self,
        snapshot_name: str,
        snapshot_config: SnapshotConfig,
        styled_layers: List[StyledLayer],
        snapshot_license: Optional[License] = None,
    ) -> Snapshot:
        """
        Creates new Snapshot with data
        :param snapshot_name:
        :param snapshot_config:
        :param styled_layers:
        :param snapshot_license:
        :return:
        """
        snapshot = Snapshot.from_dict(self.snapshot_template.to_dict())
        snapshot.name = snapshot_name
        snapshot.title = snapshot_config.title if snapshot_config.title else ""
        snapshot.views[0].spec.bounds = (
            snapshot_config.bounds if snapshot_config.bounds else []
        )
        snapshot.views[0].spec.title = (
            snapshot_config.title if snapshot_config.title else ""
        )
        snapshot.views[0].spec.description = (
            snapshot_config.description if snapshot_config.description else ""
        )
        snapshot.description = (
            snapshot_config.description if snapshot_config.description else ""
        )
        snapshot.sources = snapshot_config.sources if snapshot_config.sources else []
        assert snapshot_config.gemeindescan_meta
        snapshot.gemeindescan_meta = snapshot_config.gemeindescan_meta
        if snapshot_license:
            snapshot.licenses = [snapshot_license]
        snapshot.contributors = (
            snapshot_config.contributors
            if snapshot_config.contributors is not None
            else []
        )

        LOGGER.debug("Updating resources")
        initial_resources = snapshot.resources
        snapshot.resources = []
        keywords = snapshot_config.keywords if snapshot_config.keywords else []

        for styled_layer in styled_layers:
            resource = Resource(
                styled_layer.resource_name,
                mediatype=styled_layer.style_type.media_type,
                licenses=styled_layer.get_licenses(),
                data=styled_layer.get_geojson_data(),
            )
            kwords = styled_layer.get_keywords()
            keywords += kwords if kwords else []
            snapshot.resources.append(resource)

        snapshot.keywords = keywords if keywords else []
        snapshot.resources += initial_resources
        snapshot.views[0].resources = [res.name for res in snapshot.resources]

        LOGGER.debug("Updating legends")
        for styled_layer in styled_layers:
            snapshot.views[0].spec.legend += styled_layer.legend

        return snapshot
