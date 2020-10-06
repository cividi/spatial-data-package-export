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
from qgis.core import QgsProcessingProvider

from .algorithms import StyleToAttributesAlg


class SpatialDataPackageProcessingProvider(QgsProcessingProvider):
    ID = 'spatial_data_package'

    def __init__(self):
        QgsProcessingProvider.__init__(self)

    def loadAlgorithms(self):
        for alg in [StyleToAttributesAlg()]:
            self.addAlgorithm(alg)

    def id(self) -> str:
        return SpatialDataPackageProcessingProvider.ID

    def name(self):
        return self.tr('Spatial Data Package')

    def longName(self):
        return self.name()
