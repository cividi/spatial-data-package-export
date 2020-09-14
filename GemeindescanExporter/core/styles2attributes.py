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

from typing import Optional

from PyQt5.QtCore import QVariant
from qgis.core import (QgsVectorLayer, QgsFields, QgsField, QgsFeatureSink, QgsFillSymbol, QgsLineSymbol,
                       QgsFeature, QgsProcessingFeedback, QgsRectangle, QgsSpatialIndex, QgsFeatureRequest)

from ..definitions.symbols import SymbolLayerType, SymbolType


class StylesToAttributes:
    field_mapper = {"fill": "fillColor", "fill-opacity": "fillOpacity", "stroke": "strokeColor",
                    "stroke-opacity": "strokeOpacity", "stroke-width": "strokeWidth", "type": "shape"}

    DEFAULT_TEMPLATE = {
        "fill": "#000000",
        "fill-opacity": 1.0,
        "stroke": "#ffffff",
        "stroke-opacity": 1.0,
        "stroke-width": 1.0
    }

    def __init__(self, layer: QgsVectorLayer, layer_name: str, feedback: QgsProcessingFeedback,
                 field_template: Optional = None,
                 primary_layer: bool = False):
        self.layer = layer
        self.layer_name = layer_name
        self.feedback = feedback

        self.renderer = self.layer.renderer()
        self.symbol_type: SymbolType = SymbolType[self.renderer.type()]

        if self.symbol_type in [SymbolType.categorizedSymbol, SymbolType.graduatedSymbol]:
            self.mapped_col = self.renderer.classAttribute()
        else:
            self.mapped_col = ''

        self.symbols = {}
        self.primary_layer = primary_layer

        field_template = field_template if field_template is not None else StylesToAttributes.DEFAULT_TEMPLATE
        self.field_template = field_template.copy()

        self.fields: QgsFields = self._generate_fields()

    @staticmethod
    def _rgb_extract(prop):
        _prop = list(map(int, prop.split(",")))
        _rgb = '#' + ('%02x%02x%02x' % tuple(_prop[0:-1]))
        alpha = round(_prop[-1] / 255, 2)
        return _rgb, alpha

    def _get_style(self, symbol):
        self.feedback.pushDebugInfo(str(type(symbol)))
        style = self.field_template.copy()
        sym_type = SymbolLayerType[symbol.symbolLayers()[0].layerType()]
        if isinstance(symbol, QgsFillSymbol):
            sym = symbol.symbolLayers()[0].properties()
            if sym_type == SymbolLayerType.SimpleLine:
                sym = symbol.symbolLayers()[0].properties()
                style["type"] = "line"
                style["fill"] = "#000000"
                style["fill-opacity"] = 0
                style["stroke"] = self._rgb_extract(sym['outline_color'])[0]
                style["stroke-opacity"] = self._rgb_extract(sym['outline_color'])[1]
                style["stroke-width"] = sym['outline_width']
            if sym_type in [SymbolLayerType.CentroidFill, SymbolLayerType.SimpleFill]:
                if sym_type == SymbolLayerType.CentroidFill:
                    style["type"] = "circle"
                else:
                    style["type"] = "rectangle"
                style["fill"] = self._rgb_extract(sym['color'])[0]
                style["fill-opacity"] = self._rgb_extract(sym['color'])[1]
                style["stroke"] = self._rgb_extract(sym['outline_color'])[0]
                style["stroke-opacity"] = self._rgb_extract(sym['outline_color'])[1]
                style["stroke-width"] = sym['outline_width']

        elif isinstance(symbol, QgsLineSymbol):
            if sym_type == "SimpleLine":
                self.feedback.pushDebugInfo(symbol.symbolLayers()[0].properties())
                style["type"] = "line"
                sym = symbol.symbolLayers()[0].properties()
                style["fill"] = "transparent"
                style["fill-opacity"] = 0
                style["stroke"] = self._rgb_extract(sym['line_color'])[0]
                style["stroke-opacity"] = self._rgb_extract(sym['line_color'])[1]
                style["stroke-width"] = sym['line_width']
        else:
            raise ValueError(f"Unkown symbol type: {symbol.symbolLayers()[0].layerType()}")
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

    def run(self, sink: QgsFeatureSink, extent: Optional[QgsRectangle] = None):
        self._update_symbols()
        self._update_legend()
        self._copy_fields(sink, extent)

    def _copy_fields(self, sink: QgsFeatureSink, extent: Optional[QgsRectangle] = None):
        total = 100.0 / self.layer.featureCount()
        if extent is not None:
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
                style_attributes = self._get_style_for_feature(f)

                attributes = f.attributes() + [style_attributes[key] for key in
                                               sorted(style_attributes.keys())]
                feat.setAttributes(attributes)
                feat.setGeometry(f.geometry())
                sink.addFeature(feat, QgsFeatureSink.FastInsert)
            self.feedback.setProgress(int(current * total))

    def _generate_fields(self) -> QgsFields:
        fields: QgsFields = self.layer.fields()
        for field_template_name, field_template_value in self.field_template.items():
            if field_template_name not in self.layer.fields().names():
                if isinstance(field_template_value, str):
                    field = QgsField(field_template_name, QVariant.String)
                    fields.append(field)
                elif isinstance(field_template_value, float):
                    field = QgsField(field_template_name, QVariant.Double)
                    fields.append(field)

        return fields

    def _get_style_for_feature(self, feature: QgsFeature):
        ret_val = {}
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
                        ret_val[self.fields.names().index(field_name)] = self.symbols[matched]['style'][field_name]

        elif self.symbol_type == SymbolType.categorizedSymbol:
            feature_value = feature[self.mapped_col]
            matched = None
            if feature_value is not None:
                for index, s in self.symbols.items():
                    if str(feature_value) == str(s['value']):
                        matched = index
                if matched is not None:
                    for field_name in self.field_template.keys():
                        ret_val[self.fields.names().index(field_name)] = self.symbols[matched]['style'][field_name]

        elif self.symbol_type == SymbolType.singleSymbol:
            for field_name in self.field_template.keys():
                ret_val[self.fields.names().index(field_name)] = self.symbols[0]['style'][field_name]

        # TODO: Add more

        return ret_val

    def _update_legend(self):
        legend = {}
        i = 0
        for index, item in self.symbols.items():
            legend_style = item["style"].copy()
            legend_style = {self.field_mapper[key]: value for key, value in legend_style.items()}
            if self.primary_layer and (i == 0 or i == (len(self.symbols.items()) - 1)):
                legend_style["primary"] = True
            legend[item["label"]] = legend_style
            i = i + 1

        self.legend = legend
