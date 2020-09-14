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
from typing import Any, List, Optional, TypeVar, Type, cast, Callable, Dict

T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def to_float(x: Any) -> float:
    assert isinstance(x, float)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


@dataclass
class Contributor:
    web: str
    role: str
    email: str
    title: str

    @staticmethod
    def from_dict(obj: Any) -> 'Contributor':
        assert isinstance(obj, dict)
        web = from_str(obj.get("web"))
        role = from_str(obj.get("role"))
        email = from_str(obj.get("email"))
        title = from_str(obj.get("title"))
        return Contributor(web, role, email, title)

    def to_dict(self) -> dict:
        result: dict = {}
        result["web"] = from_str(self.web)
        result["role"] = from_str(self.role)
        result["email"] = from_str(self.email)
        result["title"] = from_str(self.title)
        return result


@dataclass
class GemeindescanMeta:
    topic: str

    @staticmethod
    def from_dict(obj: Any) -> 'GemeindescanMeta':
        assert isinstance(obj, dict)
        topic = from_str(obj.get("topic"))
        return GemeindescanMeta(topic)

    def to_dict(self) -> dict:
        result: dict = {}
        result["topic"] = from_str(self.topic)
        return result


@dataclass
class License:
    url: str
    type: str

    @staticmethod
    def from_dict(obj: Any) -> 'License':
        assert isinstance(obj, dict)
        url = from_str(obj.get("url"))
        type = from_str(obj.get("type"))
        return License(url, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["url"] = from_str(self.url)
        result["type"] = from_str(self.type)
        return result


@dataclass
class Maintainer:
    web: str
    name: str

    @staticmethod
    def from_dict(obj: Any) -> 'Maintainer':
        assert isinstance(obj, dict)
        web = from_str(obj.get("web"))
        name = from_str(obj.get("name"))
        return Maintainer(web, name)

    def to_dict(self) -> dict:
        result: dict = {}
        result["web"] = from_str(self.web)
        result["name"] = from_str(self.name)
        return result


@dataclass
class Resource:
    name: str
    mediatype: str
    data: Optional[Dict] = None
    path: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Resource':
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        mediatype = from_str(obj.get("mediatype"))
        data = obj.get("data")
        path = from_union([from_str, from_none], obj.get("path"))
        return Resource(name, mediatype, data, path)

    def to_dict(self) -> dict:
        result: dict = {}
        result["name"] = from_str(self.name)
        result["mediatype"] = from_str(self.mediatype)
        if self.data is not None:
            result["data"] = self.data
        result["path"] = from_union([from_str, from_none], self.path)
        return result


@dataclass
class Source:
    url: str
    title: str

    @staticmethod
    def from_dict(obj: Any) -> 'Source':
        assert isinstance(obj, dict)
        url = from_str(obj.get("url"))
        title = from_str(obj.get("title"))
        return Source(url, title)

    def to_dict(self) -> dict:
        result: dict = {}
        result["url"] = from_str(self.url)
        result["title"] = from_str(self.title)
        return result


@dataclass
class Legend:
    label: str
    size: int
    shape: str
    primary: bool
    fill_color: str
    fill_opacity: float
    stroke_color: str
    stroke_width: str
    stroke_opacity: float

    @staticmethod
    def from_dict(obj: Any) -> 'Legend':
        assert isinstance(obj, dict)
        label = from_str(obj.get("label"))
        size = from_int(obj.get("size"))
        shape = from_str(obj.get("shape"))
        primary = from_bool(obj.get("primary"))
        fill_color = from_str(obj.get("fillColor"))
        fill_opacity = from_float(obj.get("fillOpacity"))
        stroke_color = from_str(obj.get("strokeColor"))
        stroke_width = from_str(obj.get("strokeWidth"))
        stroke_opacity = from_float(obj.get("strokeOpacity"))
        return Legend(label, size, shape, primary, fill_color, fill_opacity, stroke_color, stroke_width, stroke_opacity)

    def to_dict(self) -> dict:
        result: dict = {}
        result["label"] = from_str(self.label)
        result["size"] = from_int(self.size)
        result["shape"] = from_str(self.shape)
        result["primary"] = from_bool(self.primary)
        result["fillColor"] = from_str(self.fill_color)
        result["fillOpacity"] = from_int(self.fill_opacity)
        result["strokeColor"] = from_str(self.stroke_color)
        result["strokeWidth"] = from_str(self.stroke_width)
        result["strokeOpacity"] = from_int(self.stroke_opacity)
        return result


@dataclass
class Spec:
    title: str
    description: str
    attribution: str
    bounds: List[str]
    legend: List[Legend]

    @staticmethod
    def from_dict(obj: Any) -> 'Spec':
        assert isinstance(obj, dict)
        title = from_str(obj.get("title"))
        description = from_str(obj.get("description"))
        attribution = from_str(obj.get("attribution"))
        bounds = from_list(from_str, obj.get("bounds"))
        legend = from_list(Legend.from_dict, obj.get("legend"))
        return Spec(title, description, attribution, bounds, legend)

    def to_dict(self) -> dict:
        result: dict = {}
        result["title"] = from_str(self.title)
        result["description"] = from_str(self.description)
        result["attribution"] = from_str(self.attribution)
        result["bounds"] = from_list(from_str, self.bounds)
        result["legend"] = from_list(lambda x: to_class(Legend, x), self.legend)
        return result


@dataclass
class View:
    name: str
    spec_type: str
    spec: Spec
    resources: List[str]

    @staticmethod
    def from_dict(obj: Any) -> 'View':
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        spec_type = from_str(obj.get("specType"))
        spec = Spec.from_dict(obj.get("spec"))
        resources = from_list(from_str, obj.get("resources"))
        return View(name, spec_type, spec, resources)

    def to_dict(self) -> dict:
        result: dict = {}
        result["name"] = from_str(self.name)
        result["specType"] = from_str(self.spec_type)
        result["spec"] = to_class(Spec, self.spec)
        result["resources"] = from_list(from_str, self.resources)
        return result


@dataclass
class Snapshot:
    name: str
    title: str
    description: str
    version: str
    datapackage_version: str
    gemeindescan_version: str
    gemeindescan_meta: GemeindescanMeta
    format: str
    license: str
    licenses: List[License]
    keywords: List[str]
    views: List[View]
    sources: List[Source]
    resources: List[Resource]
    maintainers: List[Maintainer]
    contributors: List[Contributor]

    @staticmethod
    def from_dict(obj: Any) -> 'Snapshot':
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        title = from_str(obj.get("title"))
        description = from_str(obj.get("description"))
        version = from_str(obj.get("version"))
        datapackage_version = from_str(obj.get("datapackage_version"))
        gemeindescan_version = from_str(obj.get("gemeindescan_version"))
        gemeindescan_meta = GemeindescanMeta.from_dict(obj.get("gemeindescan_meta"))
        format = from_str(obj.get("format"))
        license = from_str(obj.get("license"))
        licenses = from_list(License.from_dict, obj.get("licenses"))
        keywords = from_list(from_str, obj.get("keywords"))
        views = from_list(View.from_dict, obj.get("views"))
        sources = from_list(Source.from_dict, obj.get("sources"))
        resources = from_list(Resource.from_dict, obj.get("resources"))
        maintainers = from_list(Maintainer.from_dict, obj.get("maintainers"))
        contributors = from_list(Contributor.from_dict, obj.get("contributors"))
        return Snapshot(name, title, description, version, datapackage_version, gemeindescan_version, gemeindescan_meta,
                        format, license, licenses, keywords, views, sources, resources, maintainers, contributors)

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
        result["license"] = from_str(self.license)
        result["licenses"] = from_list(lambda x: to_class(License, x), self.licenses)
        result["keywords"] = from_list(from_str, self.keywords)
        result["views"] = from_list(lambda x: to_class(View, x), self.views)
        result["sources"] = from_list(lambda x: to_class(Source, x), self.sources)
        result["resources"] = from_list(lambda x: to_class(Resource, x), self.resources)
        result["maintainers"] = from_list(lambda x: to_class(Maintainer, x), self.maintainers)
        result["contributors"] = from_list(lambda x: to_class(Contributor, x), self.contributors)
        return result
