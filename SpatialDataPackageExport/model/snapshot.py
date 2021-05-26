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

from typing import Any, Dict, List, Optional, Union

from ..definitions.types import StyleType
from .model_utils import (
    from_bool,
    from_dict,
    from_float,
    from_int,
    from_list,
    from_none,
    from_str,
    from_union,
    to_class,
)


class Contributor:
    def __init__(self, path: str, role: str, email: str, title: str) -> None:
        self.path = path
        self.role = role
        self.email = email
        self.title = title

    @staticmethod
    def from_dict(obj: Any) -> "Contributor":
        assert isinstance(obj, dict)
        path = from_str(obj.get("path"))
        role = from_str(obj.get("role"))
        email = from_str(obj.get("email"))
        title = from_str(obj.get("title"))
        return Contributor(path, role, email, title)

    def to_dict(self) -> dict:
        result: dict = {}
        result["path"] = from_str(self.path)
        result["role"] = from_str(self.role)
        result["email"] = from_str(self.email)
        result["title"] = from_str(self.title)
        return result


class GemeindescanMeta:
    def __init__(self, topic: str) -> None:
        self.topic = topic

    @staticmethod
    def from_dict(obj: Any) -> "GemeindescanMeta":
        assert isinstance(obj, dict)
        topic = from_str(obj.get("topic"))
        return GemeindescanMeta(topic)

    def to_dict(self) -> dict:
        result: dict = {}
        result["topic"] = from_str(self.topic)
        return result


class License:
    def __init__(self, url: str, type: str, title: str) -> None:
        self.url = url
        self.type = type
        self.title = title

    @staticmethod
    def from_dict(obj: Any) -> "License":
        assert isinstance(obj, dict)
        url = from_str(obj.get("url"))
        type = from_str(obj.get("type"))
        title = from_str(obj.get("title"))
        return License(url, type, title)

    @staticmethod
    def from_setting(title: str, vals: Dict[str, str]) -> "License":
        return License.from_dict({**{"title": title}, **vals})

    def to_dict(self) -> dict:
        result: dict = {}
        result["url"] = from_str(self.url)
        result["type"] = from_str(self.type)
        result["title"] = from_str(self.title)
        return result


class Resource:
    def __init__(
        self,
        name: str,
        mediatype: str,
        licenses: List[License],
        data: Optional[Dict] = None,
        path: Optional[str] = None,
    ) -> None:
        self.name = name
        self.mediatype = mediatype
        self.licenses = licenses
        self.data = data
        self.path = path

    @staticmethod
    def from_dict(obj: Any) -> "Resource":
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        mediatype = from_str(obj.get("mediatype"))
        licenses = from_list(License.from_dict, obj.get("licenses", []))
        data = from_union([from_dict, from_none], obj.get("data"))
        path = from_union([from_str, from_none], obj.get("path"))
        return Resource(name, mediatype, licenses, data, path)

    def to_dict(self) -> dict:
        result: dict = {}
        result["name"] = from_str(self.name)
        result["mediatype"] = from_str(self.mediatype)
        result["licenses"] = from_list(lambda x: to_class(License, x), self.licenses)
        if self.data is not None:
            result["data"] = self.data
        if self.path is not None:
            result["path"] = from_union([from_str, from_none], self.path)
        return result


class Source:
    def __init__(self, url: str, title: str) -> None:
        self.url = url
        self.title = title

    @staticmethod
    def from_dict(obj: Any) -> "Source":
        assert isinstance(obj, dict)
        url = from_str(obj.get("url"))
        title = from_str(obj.get("title"))
        return Source(url, title)

    def to_dict(self) -> dict:
        result: dict = {}
        result["url"] = from_str(self.url)
        result["title"] = from_str(self.title)
        return result


class Legend:
    def __init__(
        self,
        label: Union[str, int],
        size: int,
        shape: str,
        primary: bool,
        fill_color: str,
        fill_opacity: float,
        stroke_color: str,
        stroke_width: Union[str, int, float],
        stroke_opacity: float,
    ) -> None:
        self.label = label
        self.size = size
        self.shape = shape
        self.primary = primary
        self.fill_color = fill_color
        self.fill_opacity = fill_opacity
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width
        self.stroke_opacity = stroke_opacity

    @staticmethod
    def from_dict(obj: Any) -> "Legend":
        assert isinstance(obj, dict)
        label = from_union([from_str, from_int], obj.get("label"))
        size = from_int(obj.get("size"))
        shape = from_str(obj.get("shape"))
        primary = from_bool(obj.get("primary"))
        fill_color = from_str(obj.get("fillColor"))
        fill_opacity = from_float(obj.get("fillOpacity"))
        stroke_color = from_str(obj.get("strokeColor"))
        stroke_width = from_union(
            [from_str, from_int, from_float], obj.get("strokeWidth")
        )
        stroke_opacity = from_float(obj.get("strokeOpacity"))
        return Legend(
            label,
            size,
            shape,
            primary,
            fill_color,
            fill_opacity,
            stroke_color,
            stroke_width,
            stroke_opacity,
        )

    def to_dict(self) -> dict:
        result: dict = {}
        result["label"] = from_union([from_str, from_int], self.label)
        result["size"] = from_int(self.size)
        result["shape"] = from_str(self.shape)
        result["primary"] = from_bool(self.primary)
        result["fillColor"] = from_str(self.fill_color)
        result["fillOpacity"] = from_float(self.fill_opacity)
        result["strokeColor"] = from_str(self.stroke_color)
        result["strokeWidth"] = from_union(
            [from_str, from_int, from_float], self.stroke_width
        )
        result["strokeOpacity"] = from_float(self.stroke_opacity)
        return result


class Spec:
    def __init__(
        self,
        title: str,
        description: str,
        attribution: str,
        bounds: List[str],
        legend: List[Legend],
    ) -> None:
        self.title = title
        self.description = description
        self.attribution = attribution
        self.bounds = bounds
        self.legend = legend

    @staticmethod
    def from_dict(obj: Any) -> "Spec":
        assert isinstance(obj, dict)
        title = from_str(obj.get("title"))
        description = from_str(obj.get("description"))
        attribution = from_str(obj.get("attribution"))
        bounds = from_list(from_str, obj.get("bounds", []))
        legend = from_list(Legend.from_dict, obj.get("legend", []))
        return Spec(title, description, attribution, bounds, legend)

    def to_dict(self) -> dict:
        result: dict = {}
        result["title"] = from_str(self.title)
        result["description"] = from_str(self.description)
        result["attribution"] = from_str(self.attribution)
        result["bounds"] = from_list(from_str, self.bounds)
        result["legend"] = from_list(lambda x: to_class(Legend, x), self.legend)
        return result


class View:
    def __init__(
        self, name: str, spec_type: str, spec: Spec, resources: List[str]
    ) -> None:
        self.name = name
        self.spec_type = spec_type
        self.spec = spec
        self.resources = resources

    @staticmethod
    def from_dict(obj: Any) -> "View":
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        spec_type = from_str(obj.get("specType"))
        spec = Spec.from_dict(obj.get("spec"))
        resources = from_list(from_str, obj.get("resources", []))
        return View(name, spec_type, spec, resources)

    def to_dict(self) -> dict:
        result: dict = {}
        result["name"] = from_str(self.name)
        result["specType"] = from_str(self.spec_type)
        result["spec"] = to_class(Spec, self.spec)
        result["resources"] = from_list(from_str, self.resources)
        return result


class Snapshot:
    def __init__(
        self,
        name: str,
        title: str,
        description: str,
        version: str,
        datapackage_version: str,
        gemeindescan_version: str,
        gemeindescan_meta: GemeindescanMeta,
        format: str,
        licenses: List[License],
        keywords: List[str],
        views: List[View],
        sources: List[Source],
        resources: List[Resource],
        contributors: List[Contributor],
    ) -> None:
        self.name = name
        self.title = title
        self.description = description
        self.version = version
        self.datapackage_version = datapackage_version
        self.gemeindescan_version = gemeindescan_version
        self.gemeindescan_meta = gemeindescan_meta
        self.format = format
        self.licenses = licenses
        self.keywords = keywords
        self.views = views
        self.sources = sources
        self.resources = resources
        self.contributors = contributors

    @property
    def layer_resources(self) -> List[Resource]:
        return [
            resource
            for resource in self.resources
            if resource.mediatype
            in (
                StyleType.SimpleStyle.media_type,
                StyleType.PointStyle.media_type,
            )
        ]

    @staticmethod
    def from_dict(obj: Any) -> "Snapshot":
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        title = from_str(obj.get("title"))
        description = from_str(obj.get("description"))
        version = from_str(obj.get("version"))
        datapackage_version = from_str(obj.get("datapackage_version"))
        gemeindescan_version = from_str(obj.get("gemeindescan_version"))
        gemeindescan_meta = GemeindescanMeta.from_dict(obj.get("gemeindescan_meta"))
        format = from_str(obj.get("format"))
        licenses = from_list(License.from_dict, obj.get("licenses"))
        keywords = from_list(from_str, obj.get("keywords"))
        views = from_list(View.from_dict, obj.get("views", []))
        sources = from_list(Source.from_dict, obj.get("sources"))
        resources = from_list(Resource.from_dict, obj.get("resources"))
        contributors = from_list(Contributor.from_dict, obj.get("contributors"))
        return Snapshot(
            name,
            title,
            description,
            version,
            datapackage_version,
            gemeindescan_version,
            gemeindescan_meta,
            format,
            licenses,
            keywords,
            views,
            sources,
            resources,
            contributors,
        )

    def to_dict(self) -> dict:
        result: dict = {}
        result["name"] = from_str(self.name)
        result["title"] = from_str(self.title)
        result["description"] = from_str(self.description)
        result["version"] = from_str(self.version)
        result["datapackage_version"] = from_str(self.datapackage_version)
        result["gemeindescan_version"] = from_str(self.gemeindescan_version)
        result["gemeindescan_meta"] = to_class(GemeindescanMeta, self.gemeindescan_meta)
        result["format"] = from_str(self.format)
        result["licenses"] = from_list(lambda x: to_class(License, x), self.licenses)
        result["keywords"] = from_list(from_str, self.keywords)
        result["views"] = from_list(lambda x: to_class(View, x), self.views)
        result["sources"] = from_list(lambda x: to_class(Source, x), self.sources)
        result["resources"] = from_list(lambda x: to_class(Resource, x), self.resources)
        result["contributors"] = from_list(
            lambda x: to_class(Contributor, x), self.contributors
        )
        return result
