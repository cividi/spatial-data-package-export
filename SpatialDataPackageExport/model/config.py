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
"""
Generated using https://app.quicktype.io/ from json file
"""

from typing import Any, Dict, List, Optional

from .model_utils import (
    from_bool,
    from_int,
    from_list,
    from_list_dict,
    from_none,
    from_str,
    from_union,
    to_class,
)
from .snapshot import GemeindescanMeta, License, Snapshot, Source


class SnapshotResource:
    def __init__(self, name: str, primary: bool, shape: str) -> None:
        self.name = name
        self.primary = primary
        self.shape = shape

    @staticmethod
    def from_dict(obj: Any) -> "SnapshotResource":
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        primary = from_bool(obj.get("primary"))
        shape = from_str(obj.get("shape"))
        return SnapshotResource(name, primary, shape)

    def to_dict(self) -> dict:
        result: dict = {}
        result["name"] = from_str(self.name)
        result["primary"] = from_bool(self.primary)
        result["shape"] = from_str(self.shape)
        return result


class SnapshotConfig:
    def __init__(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        gemeindescan_meta: Optional[GemeindescanMeta] = None,
        bounds: Optional[List[str]] = None,
        sources: Optional[List[Source]] = None,
        resources: Optional[List[SnapshotResource]] = None,
        licenses: Optional[List[License]] = None,
        bounds_precision: Optional[int] = None,
        crop_layers: Optional[bool] = None,
    ) -> None:
        self.title = title
        self.description = description
        self.keywords = keywords
        self.gemeindescan_meta = gemeindescan_meta
        self.bounds = bounds
        self.sources = sources
        self.resources = resources
        self.licenses = licenses
        self.bounds_precision = bounds_precision
        self.crop_layers = crop_layers

    @staticmethod
    def from_dict(obj: Any) -> "SnapshotConfig":
        assert isinstance(obj, dict)
        title = from_union([from_str, from_none], obj.get("title"))
        description = from_union([from_str, from_none], obj.get("description"))
        keywords = from_union(
            [lambda x: from_list(from_str, x), from_none], obj.get("keywords")
        )
        gemeindescan_meta = from_union(
            [GemeindescanMeta.from_dict, from_none], obj.get("gemeindescan_meta")
        )
        bounds = from_union(
            [lambda x: from_list(from_str, x), from_none], obj.get("bounds")
        )
        sources = from_union(
            [lambda x: from_list(Source.from_dict, x), from_none], obj.get("sources")
        )
        resources = from_union(
            [lambda x: from_list(SnapshotResource.from_dict, x), from_none],
            obj.get("resources"),
        )
        licenses = from_union(
            [lambda x: from_list(License.from_dict, x), from_none], obj.get("licenses")
        )
        bounds_precision = from_union(
            [from_int, from_none], obj.get("bounds_precision")
        )
        crop_layers = from_union([from_bool, from_none], obj.get("crop_layers"))
        return SnapshotConfig(
            title,
            description,
            keywords,
            gemeindescan_meta,
            bounds,
            sources,
            resources,
            licenses,
            bounds_precision,
            crop_layers,
        )

    @staticmethod
    def from_snapshot(snapshot: Snapshot) -> "SnapshotConfig":
        legend = snapshot.views[0].spec.legend
        snapshot_resources: List[SnapshotResource] = []
        for i, res in enumerate(snapshot.layer_resources):
            # This logic works only if there are 1 or 2 resources
            # since it is hard to conclude which legend belongs to which resource
            if i == 0:
                snapshot_resources.append(
                    SnapshotResource(res.name, legend[0].primary, legend[0].shape)
                )
            else:
                snapshot_resources.append(
                    SnapshotResource(res.name, legend[-1].primary, legend[-1].shape)
                )

        bounds = snapshot.views[0].spec.bounds
        bounds_precision: Optional[int] = None
        try:
            bounds_precision = len(bounds[0].split(",")[0].split(":")[1].split(".")[1])
        except IndexError:
            bounds_precision = None
        return SnapshotConfig(
            title=snapshot.title,
            description=snapshot.description,
            keywords=snapshot.keywords,
            gemeindescan_meta=snapshot.gemeindescan_meta,
            sources=snapshot.sources,
            bounds=bounds,
            resources=snapshot_resources,
            licenses=snapshot.licenses,
            bounds_precision=bounds_precision,
            crop_layers=False,
        )

    def to_dict(self) -> dict:
        result: dict = {}
        result["title"] = from_union([from_str, from_none], self.title)
        result["description"] = from_union([from_str, from_none], self.description)
        result["keywords"] = from_union(
            [lambda x: from_list(from_str, x), from_none], self.keywords
        )
        result["gemeindescan_meta"] = from_union(
            [lambda x: to_class(GemeindescanMeta, x), from_none], self.gemeindescan_meta
        )
        result["bounds"] = from_union(
            [lambda x: from_list(from_str, x), from_none], self.bounds
        )
        result["sources"] = from_union(
            [lambda x: from_list(lambda x: to_class(Source, x), x), from_none],
            self.sources,
        )
        result["resources"] = from_union(
            [
                lambda x: from_list(lambda x: to_class(SnapshotResource, x), x),
                from_none,
            ],
            self.resources,
        )
        result["licenses"] = from_union(
            [lambda x: from_list(lambda x: to_class(License, x), x), from_none],
            self.licenses,
        )
        result["bounds_precision"] = from_union(
            [from_int, from_none], self.bounds_precision
        )
        result["crop_layers"] = from_union([from_bool, from_none], self.crop_layers)
        return result


class Config:
    def __init__(
        self,
        project_name: Optional[str] = None,
        data_dir: Optional[str] = None,
        snapshots_dir: Optional[str] = None,
        dp_template_file: Optional[str] = None,
        snapshots: Optional[List[Dict[str, SnapshotConfig]]] = None,
    ) -> None:
        self.project_name = project_name
        self.data_dir = data_dir
        self.snapshots_dir = snapshots_dir
        self.dp_template_file = dp_template_file
        self.snapshots = snapshots

    @staticmethod
    def from_dict(obj: Any) -> "Config":
        assert isinstance(obj, dict)
        project_name = from_union([from_str, from_none], obj.get("project_name"))
        data_dir = from_union([from_str, from_none], obj.get("data_dir"))
        snapshots_dir = from_union([from_str, from_none], obj.get("snapshots_dir"))
        dp_template_file = from_union(
            [from_str, from_none], obj.get("dp_template_file")
        )
        snapshots = from_union(
            [lambda x: from_list_dict(SnapshotConfig.from_dict, x), from_none],
            obj.get("snapshots"),
        )
        return Config(
            project_name, data_dir, snapshots_dir, dp_template_file, snapshots
        )

    @staticmethod
    def from_snapshot(snapshot: Snapshot) -> "Config":
        return Config(
            project_name=snapshot.name,
            snapshots=[{snapshot.name: SnapshotConfig.from_snapshot(snapshot)}],
        )

    def to_dict(self) -> dict:
        result: dict = {}
        result["project_name"] = from_union([from_str, from_none], self.project_name)
        result["data_dir"] = from_union([from_str, from_none], self.data_dir)
        result["snapshots_dir"] = from_union([from_str, from_none], self.snapshots_dir)
        result["dp_template_file"] = from_union(
            [from_str, from_none], self.dp_template_file
        )
        result["snapshots"] = from_union(
            [
                lambda x: from_list_dict(lambda x: to_class(SnapshotConfig, x), x),
                from_none,
            ],
            self.snapshots,
        )
        return result

    def get_snapshot_config(self) -> Optional[SnapshotConfig]:
        if self.snapshots:
            values = list(self.snapshots[0].values())
            if values:
                return values[0]
        return None
