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

from typing import Dict, Any

from qgis.core import (
    QgsProcessingContext, QgsProcessingFeedback, QgsProcessingParameterFeatureSink,
    QgsProcessingException,
    QgsFeatureSink, QgsProcessingParameterVectorLayer,
    QgsVectorLayer, QgsRectangle, QgsProcessingParameterExtent, QgsProcessingParameterString)

from ..styles2attributes import StylesToAttributes
from ...qgis_plugin_tools.tools.algorithm_processing import BaseProcessingAlgorithm
from ...qgis_plugin_tools.tools.i18n import tr


class StyleToAttributesAlg(BaseProcessingAlgorithm):
    """
    https://gis.stackexchange.com/questions/282773/writing-a-python-processing-script-with-qgis-3-0
    """
    ID = 'styletoattributes'
    INPUT = 'INPUT'
    NAME = 'NAME'
    OUTPUT = 'OUTPUT'
    OUTPUT_LEGEND = 'OUTPUT_LEGEND'
    EXTENT = 'EXTENT'

    def name(self) -> str:
        return StyleToAttributesAlg.ID

    def shortHelpString(self):
        return tr('Extracts styles of the vector layer as attributes for the features')

    def displayName(self) -> str:
        return tr('Style to attributes')

    def group(self):
        return tr('Vector')

    def groupId(self):
        return 'vector'

    # noinspection PyMethodOverriding
    def initAlgorithm(self, config: Dict[str, Any]):
        self.addParameter(QgsProcessingParameterVectorLayer(self.INPUT, tr('Input layer')))
        self.addParameter(QgsProcessingParameterString(self.NAME, tr('Output Layer name')))
        self.addParameter(QgsProcessingParameterExtent(self.EXTENT, tr('Input extent'), defaultValue=None))

        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT, tr('Layer with attributes')))

    # noinspection PyMethodOverriding
    def processAlgorithm(self, parameters: Dict[str, Any], context: QgsProcessingContext,
                         feedback: QgsProcessingFeedback):
        source: QgsVectorLayer = self.parameterAsVectorLayer(parameters, self.INPUT, context)
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        output_name = self.parameterAsString(parameters, self.NAME, context)
        if output_name is None:
            output_name = f'{source.name()}-snapshot'

        wrkr = StylesToAttributes(source, output_name, feedback)

        extent: QgsRectangle = self.parameterAsExtent(parameters, self.EXTENT, context, crs=source.sourceCrs())

        sink: QgsFeatureSink
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context,
                                               wrkr.fields, source.wkbType(), source.sourceCrs())
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        wrkr.extract_styles_to_layer(sink, extent)

        ret_val = {self.OUTPUT: dest_id,
                   self.OUTPUT_LEGEND: wrkr.get_legend(),
                   }
        return ret_val
