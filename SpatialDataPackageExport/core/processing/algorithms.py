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

from typing import Any, Dict, Optional

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeatureSink,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterExtent,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterString,
    QgsProcessingParameterVectorLayer,
    QgsRectangle,
    QgsVectorLayer,
)

from ...qgis_plugin_tools.tools.algorithm_processing import BaseProcessingAlgorithm
from ...qgis_plugin_tools.tools.i18n import tr
from ..styles2attributes import StylesToAttributes


class StyleToAttributesAlg(BaseProcessingAlgorithm):
    """
    https://gis.stackexchange.com/questions/282773/writing-a-python-processing-script-with-qgis-3-0
    """

    ID = "styletoattributes"
    INPUT = "INPUT"
    NAME = "NAME"
    PRIMARY = "PRIMARY"
    LEGEND_SHAPE = "LEGEND_SHAPE"
    OUTPUT = "OUTPUT"
    OUTPUT_LEGEND = "OUTPUT_LEGEND"
    OUTPUT_STYLE_TYPE = "OUTPUT_STYLE_TYPE"
    EXTENT = "EXTENT"

    def name(self) -> str:
        return StyleToAttributesAlg.ID

    def shortHelpString(self) -> str:  # noqa: N802
        return tr("Extracts styles of the vector layer as attributes for the features")

    def displayName(self) -> str:  # noqa: N802
        return tr("Style to attributes")

    def group(self) -> str:
        return tr("Vector")

    def groupId(self) -> str:  # noqa: N802
        return "vector"

    # noinspection PyMethodOverriding
    def initAlgorithm(self, config: Dict[str, Any]) -> None:  # noqa: N802
        self.addParameter(
            QgsProcessingParameterVectorLayer(self.INPUT, tr("Input layer"))
        )
        self.addParameter(
            QgsProcessingParameterString(self.NAME, tr("Output Layer name"))
        )
        self.addParameter(
            QgsProcessingParameterExtent(
                self.EXTENT, tr("Input extent"), defaultValue=None
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.PRIMARY, tr("Is layer a primary layer"), defaultValue=False
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                self.LEGEND_SHAPE,
                tr(
                    "Shape of a legend. Leave empty for automatic "
                    "choice or choose one of: "
                    "automatic, circle, square or line"
                ),
                defaultValue="automatic",
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, tr("Layer with attributes"))
        )

    # noinspection PyMethodOverriding
    def processAlgorithm(  # noqa: N802
        self,
        parameters: Dict[str, Any],
        context: QgsProcessingContext,
        feedback: QgsProcessingFeedback,
    ) -> Dict[str, Any]:
        source: QgsVectorLayer = self.parameterAsVectorLayer(
            parameters, self.INPUT, context
        )
        if source is None:
            raise QgsProcessingException(
                self.invalidSourceError(parameters, self.INPUT)
            )

        output_name = self.parameterAsString(parameters, self.NAME, context)
        if output_name is None:
            output_name = f"{source.name()}-snapshot"

        primary_layer: bool = self.parameterAsBool(parameters, self.PRIMARY, context)
        legend_shape: Optional[str] = self.parameterAsString(
            parameters, self.LEGEND_SHAPE, context
        )
        if legend_shape == "automatic":
            legend_shape = None

        wrkr = StylesToAttributes(
            source,
            output_name,
            feedback,
            primary_layer=primary_layer,
            legend_shape=legend_shape,
        )

        extent_crs = QgsCoordinateReferenceSystem("EPSG:4326")
        extent: QgsRectangle = self.parameterAsExtent(
            parameters, self.EXTENT, context, crs=extent_crs
        )

        if extent_crs != source.crs() and extent is not None:
            transform = QgsCoordinateTransform(
                extent_crs, source.crs(), context.project()
            )
            extent_transformed = transform.transformBoundingBox(extent)
        else:
            extent_transformed = extent

        sink: QgsFeatureSink
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            wrkr.fields,
            source.wkbType(),
            source.sourceCrs(),
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        wrkr.extract_styles_to_layer(sink, extent_transformed)

        ret_val = {
            self.OUTPUT: dest_id,
            self.OUTPUT_LEGEND: wrkr.get_legend(),
            self.OUTPUT_STYLE_TYPE: wrkr.style_type.name,
        }
        return ret_val
