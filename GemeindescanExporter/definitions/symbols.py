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
import enum


@enum.unique
class SymbolType(enum.Enum):
    categorizedSymbol = 'categorizedSymbol'
    graduatedSymbol = 'graduatedSymbol'
    singleSymbol = 'singleSymbol'


@enum.unique
class SymbolLayerType(enum.Enum):
    SimpleLine = 'SimpleLine'
    CentroidFill = 'CentroidFill'
    SimpleFill = 'SimpleFill'