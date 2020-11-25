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

# Have to do absolute import in order to modify module variables
import json
import logging
import os
import tempfile
import uuid
from pathlib import Path
from typing import Dict, Optional

from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QCheckBox, QGridLayout, QPushButton, QWidget, QLineEdit
from qgis.PyQt import QtWidgets
from qgis.core import (QgsProcessingContext, QgsVectorLayer, QgsProject,
                       QgsMapLayerProxyModel, QgsRectangle, QgsApplication)
from qgis.gui import QgsMapLayerComboBox, QgisInterface

from .extent_dialog import ExtentChooserDialog
from .settings_dialog import SettingsDialog
from ..core.datapackage import DatapackageWriter
from ..core.processing.task_runner import TaskWrapper, create_styles_to_attributes_tasks
from ..core.utils import load_config_from_template, extent_to_datapackage_bounds, load_snapshot_template
from ..definitions.configurable_settings import Settings, LayerFormatOptions
from ..model.config import SnapshotConfig
from ..model.snapshot import Legend, Source
from ..model.styled_layer import StyledLayer
from ..qgis_plugin_tools.tools.custom_logging import bar_msg
from ..qgis_plugin_tools.tools.decorations import log_if_fails
from ..qgis_plugin_tools.tools.i18n import tr
from ..qgis_plugin_tools.tools.logger_processing import LoggerProcessingFeedBack
from ..qgis_plugin_tools.tools.resources import load_ui, plugin_name, resources_path
from ..qgis_plugin_tools.tools.settings import get_setting, set_setting

FORM_CLASS = load_ui('main_dialog_dock.ui')
LOGGER = logging.getLogger(plugin_name())


class ExporterDockWidget(QtWidgets.QDockWidget, FORM_CLASS):
    closingPlugin = pyqtSignal()

    def __init__(self, iface: QgisInterface, parent=None):
        super(ExporterDockWidget, self).__init__(parent)
        self.setupUi(self)

        # noinspection PyCallByClass
        self.btn_settings.setIcon(QgsApplication.getThemeIcon('/propertyicons/settings.svg'))

        self.iface = iface
        # Template can be configured via settings
        self.config = load_config_from_template()
        self.snapshot_template = load_snapshot_template()
        self.writer = DatapackageWriter(self.config)
        self.extent: Optional[QgsRectangle] = None
        self.layer_grid: QGridLayout = self.layer_grid
        self.source_grid: QGridLayout = self.source_grid
        self.layer_rows: Dict = {}
        self.source_rows: Dict = {}
        # TODO: add items here
        self.responsive_items = [self.btn_export]

        self.sb_extent_precision.setValue(
            get_setting(Settings.extent_precision.name, Settings.extent_precision.value, int))
        self.le_extent.setText(
            self.extent.toString(self.sb_extent_precision.value()) if self.extent is not None else '')

        self.btn_add_layer_row.setIcon(QgsApplication.getThemeIcon('/mActionAdd.svg'))
        self.btn_add_layer_row.clicked.connect(lambda _: self._add_layer_row(len(self.layer_rows) + 1))

        self.btn_add_source_row.setIcon(QgsApplication.getThemeIcon('/mActionAdd.svg'))
        self.btn_add_source_row.clicked.connect(lambda _: self._add_source_row(len(self.source_rows) + 1))

        self.btn_export.clicked.connect(self.run)
        self.btn_reset_settings.clicked.connect(self._set_initial_values)
        self._set_initial_values()

    def _set_initial_values(self):
        for name, snapshot_config in self.config.snapshots[0].items():
            self.input_name.setText(name)
            self.input_title.setText(snapshot_config.title)
            self.input_description.setText(snapshot_config.description)
            break

        for i, source in enumerate(self.snapshot_template.sources, start=1):
            self._add_source_row(1, source.url, source.title)
        self._add_layer_row(1)

    def _create_snapshot_config(self):
        snapshot_config_template = None
        for snapshot_config_template in self.config.snapshots[0].values():
            break

        if snapshot_config_template is None:
            LOGGER.warning(tr('Check your snapshot configuration'),
                           extra=bar_msg(tr('Configuration does not contain snapshot configuration template')))
            # TODO: custom exception
            raise ValueError()

        # noinspection PyUnboundLocalVariable
        snapshot_config = SnapshotConfig.from_dict(snapshot_config_template.to_dict())

        snapshot_config.title = self.input_title.text()
        snapshot_config.description = self.input_description.toPlainText()
        snapshot_config.bounds = extent_to_datapackage_bounds(self.extent, self.sb_extent_precision.value())
        snapshot_config.sources = [Source(row['url'].text(), row['title'].text()) for row in self.source_rows.values()]
        return snapshot_config

    def run(self):
        if len(self.f_output.filePath()) == 0 or len(self.input_name.text()) == 0:
            LOGGER.warning(tr('No output path filled'),
                           extra=bar_msg(tr('Fill output path and snapshot name')))
            return

        task_wrappers = []
        for id, row in self.layer_rows.items():
            cb: QgsMapLayerComboBox = row['layer']
            layer_name = cb.currentText()
            row['layer_name'] = layer_name
            new_layer_name = f'{layer_name}-snapshot'
            row['new_layer_name'] = new_layer_name
            row['finished'] = False
            is_primary = row['primary'].isChecked()

            task_wrapper = TaskWrapper(id=id, layer=cb.currentLayer(), name=layer_name, extent=self.extent,
                                       primary=is_primary, output=f'memory:{new_layer_name}', feedback=row['feedback'],
                                       context=row['context'], executed=self.styles_to_attributes_finished
                                       )
            LOGGER.info(f"Exporting {layer_name}")
            task_wrappers.append(task_wrapper)

        LOGGER.info(f'Tasks are: {[str(w) for w in task_wrappers]}')

        if len(task_wrappers) == 0:
            LOGGER.warning(tr('No layers selected'),
                           extra=bar_msg(tr('Select at least one layer to create snapshot')))
        else:
            create_styles_to_attributes_tasks(task_wrappers, completed=lambda *args, **kwargs: self.completed())
            self._disable_ui()

    def completed(self, *args, **kwargs):
        all_finished = all(map(lambda x: x['finished'], self.layer_rows.values()))
        if not all_finished:
            return

        self._enable_ui()
        LOGGER.info(tr('Finished exporting style to attributes'))

        output_path = Path(self.f_output.filePath())

        snapshot_config = self._create_snapshot_config()
        snapshot_name = self.input_name.text()
        styled_layers = [row['styled_layer'] for row in self.layer_rows.values()]
        snapshot = self.writer.create_snapshot(snapshot_name, snapshot_config, styled_layers)

        output_file = Path(output_path, f'{snapshot_name}.json')

        with open(output_file, 'w') as f:
            json.dump(snapshot.to_dict(), f)

        if Settings.layer_format.get() == LayerFormatOptions.none.value:
            LOGGER.debug('Removing memory layers')
            for row in self.layer_rows.values():
                QgsProject.instance().removeMapLayer(row['styled_layer'].layer_id)

        LOGGER.info(tr('Snapshot succesfully exported'),
                    extra=bar_msg(tr('Snapshot can be found in {}', str(output_file)), success=True))

    def styles_to_attributes_finished(self, input_layer: QgsVectorLayer, context: QgsProcessingContext, id: uuid.UUID,
                                      succesful: bool, results: Dict[str, any]) -> None:
        row = self.layer_rows[id]
        if succesful:
            legends = [Legend.from_dict(legend) for legend in results["OUTPUT_LEGEND"].values()]
            style_type = results['OUTPUT_STYLE_TYPE']
            LOGGER.info(tr('Exporting styles for {} ({}) finished successfully', input_layer.name(), style_type))

            output_layer: QgsVectorLayer = context.takeResultLayer(results['OUTPUT'])
            if output_layer and output_layer.isValid():
                QgsProject.instance().addMapLayer(output_layer)
                styled_layer = StyledLayer(row['layer_name'], output_layer.id(), legends, style_type)

                if Settings.layer_format.get() == LayerFormatOptions.geojson.value:
                    geojson_path = styled_layer.save_as_geojson(Path(self.f_output.filePath()))
                    output_layer = QgsVectorLayer(str(geojson_path), output_layer.name())
                    QgsProject.instance().removeMapLayer(styled_layer.layer_id)
                    QgsProject.instance().addMapLayer(output_layer)
                    styled_layer.layer_id = output_layer.id()

                with tempfile.TemporaryDirectory(dir=resources_path()) as tmpdirname:
                    style_file = os.path.join(tmpdirname, 'style.qml')
                    msg, succeeded = input_layer.saveNamedStyle(style_file)
                    if succeeded:
                        output_layer.loadNamedStyle(style_file)
                    else:
                        LOGGER.error(tr('Could not load style'), extra=bar_msg(msg))

                row['styled_layer'] = styled_layer

            row['finished'] = True
        else:
            feedback: LoggerProcessingFeedBack = row['feedback']
            error_msg = feedback.last_report_error
            LOGGER.error(tr('Exporting styles for {} finished with errors', input_layer.name()),
                         extra=bar_msg(details=tr(f'Details: {error_msg}. Check log file for more details')))
            self._enable_ui()

    # noinspection PyUnresolvedReferences
    @log_if_fails
    def _add_layer_row(self, row_index: int):
        row_uuid = str(uuid.uuid4())
        b_rm = QPushButton(text='', icon=QgsApplication.getThemeIcon('/mActionRemove.svg'))
        b_rm.setToolTip(tr('Remove row'))
        b_rm.clicked.connect(lambda _: self._remove_row(row_uuid, self.layer_rows, self.layer_grid))

        bx_layer = QgsMapLayerComboBox()
        bx_layer.setFilters(QgsMapLayerProxyModel.Filters(QgsMapLayerProxyModel.Filter.PointLayer |
                                                          QgsMapLayerProxyModel.Filter.PolygonLayer |
                                                          QgsMapLayerProxyModel.Filter.LineLayer))
        cb_primary = QCheckBox(text='')

        row = {
            'layer': bx_layer,
            'primary': cb_primary,
            'rm': b_rm,
            'feedback': LoggerProcessingFeedBack(use_logger=True),
            'context': QgsProcessingContext()
        }
        self.layer_rows[row_uuid] = row
        self.layer_grid.addWidget(b_rm, row_index, 0)
        self.layer_grid.addWidget(bx_layer, row_index, 1)
        self.layer_grid.addWidget(cb_primary, row_index, 2)

    # noinspection PyUnresolvedReferences
    @log_if_fails
    def _add_source_row(self, row_index: int, url: str = '', title: str = ''):
        row_uuid = str(uuid.uuid4())
        b_rm = QPushButton(text='', icon=QgsApplication.getThemeIcon('/mActionRemove.svg'))
        b_rm.setToolTip(tr('Remove row'))
        b_rm.clicked.connect(lambda _: self._remove_row(row_uuid, self.source_rows, self.source_grid))

        le_url = QLineEdit(url)
        le_title = QLineEdit(title)
        row = {
            'rm': b_rm,
            'url': le_url,
            'title': le_title
        }

        self.source_rows[row_uuid] = row
        self.source_grid.addWidget(b_rm, row_index, 0)
        self.source_grid.addWidget(le_url, row_index, 1)
        self.source_grid.addWidget(le_title, row_index, 2)

    @log_if_fails
    def _remove_row(self, row_uuid: str, row_dict: Dict, grid: QGridLayout):
        row = row_dict.pop(row_uuid)
        for widget in row.values():
            if isinstance(widget, QWidget):
                grid.removeWidget(widget)
                widget.hide()
                widget.setParent(None)
            # noinspection PyUnusedLocal
            widget = None

    def on_sb_extent_precision_valueChanged(self, new_val: int):
        set_setting(Settings.extent_precision.name, new_val)

    @pyqtSlot()
    def on_btn_calculate_extent_clicked(self):
        canvas = self.iface.mapCanvas()
        crs = canvas.mapSettings().destinationCrs()

        extent_chooser = ExtentChooserDialog(canvas, crs)
        result = extent_chooser.exec()
        if result:
            self.extent = extent_chooser.get_extent(self.sb_extent_precision.value())
            self.le_extent.setText(self.extent.toString(self.sb_extent_precision.value()))

    @pyqtSlot()
    def on_btn_settings_clicked(self):
        settings_dialog = SettingsDialog()
        settings_dialog.exec()

    def _disable_ui(self):
        for item in self.responsive_items:
            item.setEnabled(False)

    def _enable_ui(self):
        for item in self.responsive_items:
            item.setEnabled(True)
