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

from typing import TypeVar, Any, Type, cast, Callable, List

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
