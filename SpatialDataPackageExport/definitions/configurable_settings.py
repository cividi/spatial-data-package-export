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
import enum
import json
from typing import Union, List, Dict

from ..qgis_plugin_tools.tools.exceptions import QgsPluginException
from ..qgis_plugin_tools.tools.i18n import tr
from ..qgis_plugin_tools.tools.resources import resources_path
from ..qgis_plugin_tools.tools.settings import get_setting, set_setting, get_project_setting, set_project_setting


@enum.unique
class LayerFormatOptions(enum.Enum):
    memory = 'memory'
    geojson = 'geojson'
    none = 'none'


@enum.unique
class Settings(enum.Enum):
    extent_precision = 8
    export_config_template = resources_path('templates', 'export-config.json')
    snapshot_template = resources_path('templates', 'snapshot-template.json')
    layer_format = 'memory'
    crop_layers = True
    licences = {
        'Creative Commons CC Zero': {'type': 'CC0-1.0',
                                     'url': 'https://creativecommons.org/publicdomain/zero/1.0/'},
        'Open Data Commons Public Domain Dedication and Licence': {'type': 'PDDL-1.0',
                                                                   'url': 'https://opendatacommons.org/licenses/pddl/'},
        'Creative Commons Attribution 4.0': {'type': 'CC-BY-4.0',
                                             'url': 'https://creativecommons.org/licenses/by/4.0/'},
        'Open Data Commons Attribution License': {'type': 'ODC-BY-1.0',
                                                  'url': 'https://opendefinition.org/licenses/odc-by'},
        'Creative Commons Attribution Share-Alike 4.0': {'type': 'CC-BY-SA-4.0',
                                                         'url': 'https://creativecommons.org/licenses/by-sa/4.0/'},
        'Open Data Commons Open Database License': {'type': 'ODbL-1.0',
                                                    'url': 'https://opendatacommons.org/licenses/odbl/'},
    }

    _options = {'layer_format': [option.value for option in LayerFormatOptions]}

    def get(self) -> any:
        """Gets the value of the setting"""
        typehint: type = str
        if self == Settings.crop_layers:
            typehint = bool
        elif self == Settings.extent_precision:
            typehint = int
        elif self == Settings.licences:
            return json.loads(get_setting(self.name, json.dumps(self.value), str))
        return get_setting(self.name, self.value, typehint)

    def set(self, value: Union[str, int, float, bool]) -> bool:
        """Sets the value of the setting"""
        options = self.get_options()
        if options and value not in options:
            raise QgsPluginException(tr('Invalid option. Choose something from values {}', options))
        if self == Settings.licences:
            value = json.dumps(value)
        return set_setting(self.name, value)

    def get_options(self) -> List[any]:
        """Get options for the setting"""
        return Settings._options.value.get(self.name, [])


@enum.unique
class ProjectSettings(enum.Enum):
    snapshot_configs = '{}'

    def get(self) -> any:
        """Gets the value of the setting"""
        value = get_project_setting(self.name, self.value, str)
        if self == ProjectSettings.snapshot_configs:
            value = json.loads(value)
        return value

    def set(self, value: Union[str, int, float, bool, Dict, List]) -> bool:
        """Sets the value of the setting"""
        if self == ProjectSettings.snapshot_configs:
            value = json.dumps(value)
        return set_project_setting(self.name, value)

    def reset(self) -> bool:
        """Resets the setting back to its default value"""
        return set_project_setting(self.name, self.value)
