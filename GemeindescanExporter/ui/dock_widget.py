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

# Have to do absolute import in order to modify module variables
import json
import logging
import os
import sys
import tempfile
from importlib import reload
from typing import Dict

from PyQt5.QtCore import pyqtSignal
from qgis.PyQt import QtWidgets
from qgis.core import (QgsProcessingContext, QgsVectorLayer, QgsProject,
                       QgsMapLayerProxyModel, QgsRectangle)
from qgis.gui import QgsMapLayerComboBox, QgisInterface, QgsFileWidget

from .extent_dialog import ExtentChooserDialog
from ..core.datapackage import DatapackageWriter
from ..core.utils import load_config_from_template, extent_to_datapackage_bounds
from ..definitions.configurable_settings import Settings
from ..model.snapshot import Legend
from ..model.styled_layer import StyledLayer
from ..qgis_plugin_tools.tools.custom_logging import bar_msg
from ..qgis_plugin_tools.tools.i18n import tr
from ..qgis_plugin_tools.tools.logger_processing import LoggerProcessingFeedBack
from ..qgis_plugin_tools.tools.resources import plugin_path, load_ui, plugin_name, resources_path
from ..qgis_plugin_tools.tools.settings import get_setting, set_setting

processing_path = plugin_path('core', 'processing')
if processing_path not in sys.path:
    sys.path.append(processing_path)
import task_variables

FORM_CLASS = load_ui('main_dialog_dock.ui')
LOGGER = logging.getLogger(plugin_name())


class ExporterDockWidget(QtWidgets.QDockWidget, FORM_CLASS):
    closingPlugin = pyqtSignal()

    def __init__(self, iface: QgisInterface, parent=None):
        super(ExporterDockWidget, self).__init__(parent)
        self.setupUi(self)
        self.iface = iface
        # Template can be configured via settings
        self.config = load_config_from_template()
        self.writer = DatapackageWriter(self.config)
        self.responsive_items = [self.pushButtonExport]
        self.extent: QgsRectangle = self.iface.mapCanvas().extent()
        self.sb_extent_precision.setValue(
            get_setting(Settings.extent_precision.name, Settings.extent_precision.value, int))
        self.le_extent.setText(self.extent.toString(self.sb_extent_precision.value()))

        self.m_layer_cb.setFilters(QgsMapLayerProxyModel.Filters(QgsMapLayerProxyModel.Filter.PointLayer |
                                                                 QgsMapLayerProxyModel.Filter.PolygonLayer |
                                                                 QgsMapLayerProxyModel.Filter.LineLayer))
        self.pushButtonExport.clicked.connect(self.run)
        self._set_initial_values()

    def _set_initial_values(self):

        snap = self.config.snapshots[0]
        snapshot_config = list(snap.values())[0]

        self.input_title.setText(snapshot_config.title)
        self.input_description.setText(snapshot_config.description)

    def on_sb_extent_precision_valueChanged(self, new_val: int):
        set_setting(Settings.extent_precision.name, new_val)

    def on_btn_calculate_extent_clicked(self):
        curr_layer = self.m_layer_cb.currentLayer()
        canvas = self.iface.mapCanvas()
        crs = curr_layer.crs() if curr_layer is not None else canvas.mapSettings().destinationCrs()
        extent_chooser = ExtentChooserDialog(canvas, crs)

        result = extent_chooser.exec()
        if result:
            self.extent = extent_chooser.get_extent(self.sb_extent_precision.value())
            self.le_extent.setText(self.extent.toString(self.sb_extent_precision.value()))

    def disable_ui(self):
        for item in self.responsive_items:
            item.setEnabled(False)

    def completed(self, *args, **kwargs):
        print(1)
        for item in self.responsive_items:
            item.setEnabled(True)
        LOGGER.info("Finished!!")

    def run(self):
        cb: QgsMapLayerComboBox = self.m_layer_cb
        layer_name = cb.currentText()
        LOGGER.info(f"Exporting {layer_name}")

        task_variables.CONTEXT = QgsProcessingContext()
        task_variables.FEEDBACK = LoggerProcessingFeedBack(use_logger=True)
        task_variables.EXTENT = self.extent
        task_variables.LAYER = cb.currentLayer()
        task_variables.NAME = f'{layer_name}-snapshot'
        task_variables.OUTPUT = f'memory:{task_variables.NAME}'
        task_variables.COMPLETED = lambda *args, **kwargs: self.completed()
        task_variables.EXECUTED = self.styles_to_attributes_finished

        # Start the task in a weird way, check task_runner for more info
        modulename = 'GemeindescanExporter.core.processing.task_runner'
        if modulename in sys.modules:
            from ..core.processing import task_runner
            # noinspection PyTypeChecker
            reload(task_runner)
        else:
            from ..core.processing import task_runner
        self.disable_ui()

    def styles_to_attributes_finished(self, input_layer: QgsVectorLayer, context: QgsProcessingContext, succesful: bool,
                                      results: Dict[str, any]):
        if succesful:
            legends = [Legend.from_dict(legend) for legend in results["OUTPUT_LEGEND"].values()]
            LOGGER.info('Task finished successfully',
                        extra=bar_msg(f'Legend: {legends}'))
            # output_layer: QgsVectorLayer = context.getMapLayer(results['OUTPUT'])
            output_layer = context.takeResultLayer(results['OUTPUT'])
            # because getMapLayer doesn't transfer ownership, the layer will
            # be deleted when context goes out of scope and you'll get a
            # crash.
            # takeMapLayer transfers ownership so it's then safe to add it
            # to the project and give the project ownership.
            if output_layer and output_layer.isValid():
                with tempfile.TemporaryDirectory(dir=resources_path()) as tmpdirname:
                    style_file = os.path.join(tmpdirname, 'style.qml')
                    msg, succeeded = input_layer.saveNamedStyle(style_file)
                    if succeeded:
                        output_layer.loadNamedStyle(style_file)
                    else:
                        LOGGER.error(tr('Could not load style'), extra=bar_msg(msg))

                QgsProject.instance().addMapLayer(output_layer)

                styled_layer = StyledLayer(task_variables.NAME, output_layer, legends)

                snap = self.config.snapshots[0]
                snap_name = list(snap.keys())[0]
                snapshot_config = list(snap.values())[0]
                snapshot_config.bounds = extent_to_datapackage_bounds(self.extent, self.sb_extent_precision.value())
                snapshot = self.writer.create_snapshot(snap_name, snapshot_config, [styled_layer])
                output: QgsFileWidget = self.f_output
                path = output.filePath()

                with open(path, 'w') as f:
                    json.dump(snapshot.to_dict(), f)
