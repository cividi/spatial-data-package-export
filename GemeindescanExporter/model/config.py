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
"""
Generated using https://app.quicktype.io/ from json file
"""

from dataclasses import dataclass
from typing import Optional, Any, List, Dict

from .model_utils import (from_str, to_class, from_list, from_union, from_none, from_list_dict)


@dataclass
class GemeindescanMeta:
    topic: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'GemeindescanMeta':
        assert isinstance(obj, dict)
        topic = from_union([from_str, from_none], obj.get("topic"))
        return GemeindescanMeta(topic)

    def to_dict(self) -> dict:
        result: dict = {}
        result["topic"] = from_union([from_str, from_none], self.topic)
        return result


@dataclass
class Source:
    url: Optional[str] = None
    title: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Source':
        assert isinstance(obj, dict)
        url = from_union([from_str, from_none], obj.get("url"))
        title = from_union([from_str, from_none], obj.get("title"))
        return Source(url, title)

    def to_dict(self) -> dict:
        result: dict = {}
        result["url"] = from_union([from_str, from_none], self.url)
        result["title"] = from_union([from_str, from_none], self.title)
        return result


@dataclass
class SnapshotConfig:
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    gemeindescan_meta: Optional[GemeindescanMeta] = None
    bounds: Optional[List[str]] = None
    sources: Optional[List[Source]] = None
    resources: Optional[List[str]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'SnapshotConfig':
        assert isinstance(obj, dict)
        title = from_union([from_str, from_none], obj.get("title"))
        description = from_union([from_str, from_none], obj.get("description"))
        keywords = from_union([lambda x: from_list(from_str, x), from_none], obj.get("keywords"))
        gemeindescan_meta = from_union([GemeindescanMeta.from_dict, from_none], obj.get("gemeindescan_meta"))
        bounds = from_union([lambda x: from_list(from_str, x), from_none], obj.get("bounds"))
        sources = from_union([lambda x: from_list(Source.from_dict, x), from_none], obj.get("sources"))
        resources = from_union([lambda x: from_list(from_str, x), from_none], obj.get("resources"))
        return SnapshotConfig(title, description, keywords, gemeindescan_meta, bounds, sources, resources)

    def to_dict(self) -> dict:
        result: dict = {}
        result["title"] = from_union([from_str, from_none], self.title)
        result["description"] = from_union([from_str, from_none], self.description)
        result["keywords"] = from_union([lambda x: from_list(from_str, x), from_none], self.keywords)
        result["gemeindescan_meta"] = from_union([lambda x: to_class(GemeindescanMeta, x), from_none],
                                                 self.gemeindescan_meta)
        result["bounds"] = from_union([lambda x: from_list(from_str, x), from_none], self.bounds)
        result["sources"] = from_union([lambda x: from_list(lambda x: to_class(Source, x), x), from_none], self.sources)
        result["resources"] = from_union([lambda x: from_list(from_str, x), from_none], self.resources)
        return result


@dataclass
class Config:
    project_name: Optional[str] = None
    data_dir: Optional[str] = None
    snapshots_dir: Optional[str] = None
    dp_template_file: Optional[str] = None
    snapshots: Optional[List[Dict[str, SnapshotConfig]]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Config':
        assert isinstance(obj, dict)
        project_name = from_union([from_str, from_none], obj.get("project_name"))
        data_dir = from_union([from_str, from_none], obj.get("data_dir"))
        snapshots_dir = from_union([from_str, from_none], obj.get("snapshots_dir"))
        dp_template_file = from_union([from_str, from_none], obj.get("dp_template_file"))
        snapshots = from_union([lambda x: from_list_dict(SnapshotConfig.from_dict, x), from_none], obj.get("snapshots"))
        return Config(project_name, data_dir, snapshots_dir, dp_template_file, snapshots)

    def to_dict(self) -> dict:
        result: dict = {}
        result["project_name"] = from_union([from_str, from_none], self.project_name)
        result["data_dir"] = from_union([from_str, from_none], self.data_dir)
        result["snapshots_dir"] = from_union([from_str, from_none], self.snapshots_dir)
        result["dp_template_file"] = from_union([from_str, from_none], self.dp_template_file)
        result["snapshots"] = from_union(
            [lambda x: from_list_dict(lambda x: to_class(SnapshotConfig, x), x), from_none],
            self.snapshots)
        return result
