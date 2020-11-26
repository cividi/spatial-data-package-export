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

from typing import Optional, Dict, List

from PyQt5.QtCore import QVariant
from qgis.core import (QgsVectorLayer, QgsFields, QgsField, QgsFeatureSink, QgsFillSymbol, QgsLineSymbol,
                       QgsFeature, QgsProcessingFeedback, QgsRectangle, QgsSpatialIndex, QgsFeatureRequest,
                       QgsMarkerSymbol, QgsSymbol, QgsSymbolLayer, QgsPropertyCollection, QgsProperty)

from ..definitions.style import Style, PointStyle
from ..definitions.symbols import SymbolLayerType, SymbolType
from ..definitions.types import StyleType
from ..model.snapshot import Legend
from ..qgis_plugin_tools.tools.exceptions import QgsPluginNotImplementedException
from ..qgis_plugin_tools.tools.i18n import tr


class StylesToAttributes:

    def __init__(self, layer: QgsVectorLayer, layer_name: str, feedback: QgsProcessingFeedback,
                 primary_layer: bool = False, legend_shape: Optional[str] = None):
        self.layer = layer
        self.layer_name = layer_name
        self.feedback = feedback
        self.legend_shape = legend_shape

        self.renderer = self.layer.renderer()
        self.symbol_type: SymbolType = SymbolType[self.renderer.type()]

        self.style_type: StyleType = StyleType.from_layer(layer)
        self.field_template = self.style_type.get_style().to_dict()

        if self.symbol_type in [SymbolType.categorizedSymbol, SymbolType.graduatedSymbol]:
            self.mapped_col = self.renderer.classAttribute()
        else:
            self.mapped_col = ''

        self.symbols = {}
        self.primary_layer = primary_layer

        self.fields: QgsFields = self._generate_fields()
        self.legend = {}


    @staticmethod
    def _rgb_extract(prop):
        _prop = list(map(int, prop.split(",")))
        _rgb = '#' + ('%02x%02x%02x' % tuple(_prop[0:-1]))
        alpha = round(_prop[-1] / 255, 2)
        return _rgb, alpha

    def get_legend(self) -> Dict:
        return {label: legend.to_dict() for label, legend in self.legend.items()}

    def get_symbols(self) -> Dict:
        return {key: {**val, 'style': val['style'].to_dict()} for key, val in self.symbols.items()}

    def extract_styles_to_layer(self, sink: QgsFeatureSink, extent: Optional[QgsRectangle] = None):
        try:
            self._update_symbols()
            self._copy_fields(sink, extent)
            self._update_legend()
        except Exception as e:
            self.feedback.reportError(tr('Error occurred: {}', e), True)
            self.feedback.cancel()

    def _get_style(self, symbol: QgsSymbol) -> Style:
        self.feedback.pushDebugInfo(str(type(symbol)))

        symbol_opacity: float = symbol.opacity()

        symbol_layer: QgsSymbolLayer = symbol.symbolLayers()[0]
        if symbol_layer.subSymbol() is not None:
            return self._get_style(symbol_layer.subSymbol())

        style: Style = self.style_type.get_style()
        sym_type = SymbolLayerType[symbol_layer.layerType()]
        sym = symbol_layer.properties()

        # Add data defined properties for the style
        if symbol_layer.hasDataDefinedProperties():
            data_defined_props: QgsPropertyCollection = symbol_layer.dataDefinedProperties()
            for key in data_defined_props.propertyKeys():
                prop: QgsProperty = data_defined_props.property(key)
                if prop.field() != '':
                    style.add_data_defined_expression(prop.field(), prop.asExpression())

        if isinstance(symbol, QgsFillSymbol):
            if sym_type == SymbolLayerType.SimpleLine:
                style.type = "line"
                style.fill = "#000000"
                style.fill_opacity = 0
                style.stroke = self._rgb_extract(sym['outline_color'])[0]
                style.stroke_opacity = symbol_opacity * self._rgb_extract(sym['outline_color'])[1]
                style.stroke_width = float(sym['outline_width'])
            if sym_type in [SymbolLayerType.CentroidFill, SymbolLayerType.SimpleFill]:
                if sym_type == SymbolLayerType.CentroidFill:
                    style.type = "circle"
                else:
                    style.type = "square"
                style.fill = self._rgb_extract(sym['color'])[0]
                style.fill_opacity = symbol_opacity * self._rgb_extract(sym['color'])[1]
                style.stroke = self._rgb_extract(sym['outline_color'])[0]
                style.stroke_opacity = symbol_opacity * self._rgb_extract(sym['outline_color'])[1]
                style.stroke_width = float(sym['outline_width'])

        elif isinstance(symbol, QgsLineSymbol):
            if sym_type == SymbolLayerType.SimpleLine:
                self.feedback.pushDebugInfo(symbol_layer.properties())
                style.type = "line"
                style.fill = "transparent"
                style.fill_opacity = 0
                style.stroke = self._rgb_extract(sym['line_color'])[0]
                style.stroke_opacity = symbol_opacity * self._rgb_extract(sym['line_color'])[1]
                style.stroke_width = float(sym['line_width'])
        elif isinstance(symbol, QgsMarkerSymbol):
            if sym_type == SymbolLayerType.SimpleMarker:
                style: PointStyle
                style.type = "circle"
                style.fill = self._rgb_extract(sym['color'])[0]
                style.fill_opacity = symbol_opacity * self._rgb_extract(sym['color'])[1]
                style.has_fill = style.fill_opacity > 0.0
                style.stroke = self._rgb_extract(sym['outline_color'])[0]
                style.stroke_opacity = symbol_opacity * self._rgb_extract(sym['outline_color'])[1]
                style.stroke_width = float(sym['outline_width'])
                style.has_stroke = style.stroke_opacity > 0.0
                style.radius = sym['size']

        else:
            raise ValueError(f"Unkown symbol type: {symbol_layer.layerType()}")
        return style

    def _update_symbols(self):
        i = 0

        if self.symbol_type == SymbolType.graduatedSymbol:
            for sym_range in self.renderer.ranges():
                style = self._get_style(sym_range.symbol())
                self.symbols[i] = {'range_lower': sym_range.lowerValue(), 'range_upper': sym_range.upperValue(),
                                   'label': sym_range.label(), 'style': style}
                i = i + 1
        elif self.symbol_type == SymbolType.categorizedSymbol:
            for c in self.renderer.categories():
                style = self._get_style(c.symbol())
                self.symbols[i] = {'value': c.value(), 'label': c.label(), 'style': style}
                i = i + 1
        elif self.symbol_type == SymbolType.singleSymbol:
            style = self._get_style(self.renderer.symbol())
            self.symbols[0] = {'range_lower': None, 'range_upper': None, 'label': self.layer_name, 'style': style}

    def _copy_fields(self, sink: QgsFeatureSink, extent: Optional[QgsRectangle] = None):
        total = 100.0 / self.layer.featureCount() if self.layer.featureCount() > 0 else 100
        if extent is not None and not extent.isEmpty():
            self.feedback.pushDebugInfo(f'Extent: {extent.toString()}')
            source_index = QgsSpatialIndex(self.layer, self.feedback)
            ids = source_index.intersects(extent)
            features = self.layer.getFeatures(QgsFeatureRequest().setFilterFids(ids))
        else:
            features = self.layer.getFeatures()

        f: QgsFeature
        for current, f in enumerate(features):
            if self.feedback.isCanceled():
                break

            if not f.hasGeometry():
                sink.addFeature(f, QgsFeatureSink.FastInsert)
            else:
                feat = QgsFeature()
                attributes = self._get_attributes_for_feature(f)
                feat.setAttributes(attributes)
                feat.setGeometry(f.geometry())
                succeeded = sink.addFeature(feat, QgsFeatureSink.FastInsert)
                if not succeeded:
                    raise ValueError(tr('Could not add feature to target layer. Attributes: {}', attributes))
            self.feedback.setProgress(int(current * total))

    def _generate_fields(self) -> QgsFields:
        fields: QgsFields = self.layer.fields()
        for field_template_name, field_template_value in self.field_template.items():
            if field_template_name not in self.layer.fields().names():
                if isinstance(field_template_value, str):
                    field = QgsField(field_template_name, QVariant.String)
                elif isinstance(field_template_value, float):
                    field = QgsField(field_template_name, QVariant.Double)
                elif isinstance(field_template_value, bool):
                    field = QgsField(field_template_name, QVariant.Bool)
                else:
                    raise QgsPluginNotImplementedException(
                        tr('Field type not implemented: {}', type(field_template_value)))
                fields.append(field)

        return fields

    def _get_attributes_for_feature(self, feature: QgsFeature) -> List[any]:
        attributes = {i: feature[field.name()] for i, field in enumerate(feature.fields().toList())}
        if self.symbol_type == SymbolType.graduatedSymbol:
            feature_value = feature[self.mapped_col]
            matched = None
            if feature_value is not None:
                for index, s in self.symbols.items():
                    if s['range_lower'] <= feature_value < s['range_upper']:
                        matched = index
                        break
                if matched is not None:
                    for field_name in self.field_template.keys():
                        style: Style = self.symbols[matched]['style']
                        style.evaluate_data_defined_expressions(feature)
                        attributes[self.fields.names().index(field_name)] = style.to_dict()[
                            field_name]

        elif self.symbol_type == SymbolType.categorizedSymbol:
            feature_value = feature[self.mapped_col]
            matched = None
            if feature_value is not None:
                for index, s in self.symbols.items():
                    if str(feature_value) == str(s['value']):
                        matched = index
                if matched is not None:
                    for field_name in self.field_template.keys():
                        style = self.symbols[matched]['style']
                        style.evaluate_data_defined_expressions(feature)
                        attributes[self.fields.names().index(field_name)] = style.to_dict()[
                            field_name]

        elif self.symbol_type == SymbolType.singleSymbol:
            for field_name in self.field_template.keys():
                style = self.symbols[0]['style']
                style.evaluate_data_defined_expressions(feature)
                attributes[self.fields.names().index(field_name)] = style.to_dict()[field_name]

        # TODO: Add more

        return [attributes[key] for key in sorted(attributes.keys())]

    def _update_legend(self):
        legend = {}
        i = 0
        for index, item in self.symbols.items():
            legend_style = item["style"].legend_style
            legend_style["size"] = 1
            legend_style["primary"] = self.primary_layer and (i == 0 or i == (len(self.symbols.items()) - 1))
            legend_style["label"] = item["label"]
            if self.legend_shape:
                legend_style["shape"] = self.legend_shape

            legend[item["label"]] = Legend.from_dict(legend_style)
            i += 1

        self.legend = legend
