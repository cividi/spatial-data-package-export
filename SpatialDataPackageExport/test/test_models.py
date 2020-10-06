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

from .utils import get_test_json
from ..model.config import Config
from ..model.snapshot import Snapshot
from ..qgis_plugin_tools.tools.resources import resources_path


def test_snapshot_from_categorized_polygons():
    snapshot_data = get_test_json('snapshots', 'snapshot_categorized_poly.json')
    snapshot = Snapshot.from_dict(snapshot_data)
    assert snapshot.name == snapshot_data['name']


def test_config_from_template():
    with open(resources_path('templates', 'export-config.json')) as f:
        config_data = json.load(f)
    config = Config.from_dict(config_data)
    assert config.project_name == 'PROJECT-FOLDER-NAME'
