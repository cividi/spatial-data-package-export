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
from PyQt5.QtWidgets import QCheckBox, QGridLayout, QPushButton, QWidget, QLineEdit, QComboBox
from qgis.PyQt import QtWidgets
from qgis.core import (QgsProcessingContext, QgsVectorLayer, QgsProject,
                       QgsMapLayerProxyModel, QgsRectangle, QgsApplication)
from qgis.gui import QgsMapLayerComboBox, QgisInterface

from .extent_dialog import ExtentChooserDialog
from .load_snapshot_conf_dialog import LoadSnapshotConfDialog
from .settings_dialog import SettingsDialog
from ..core.datapackage import DataPackageHandler
from ..core.processing.task_runner import TaskWrapper, create_styles_to_attributes_tasks
from ..core.utils import extent_to_datapackage_bounds, datapackage_bounds_to_extent
from ..definitions.configurable_settings import Settings, LayerFormatOptions
from ..model.config import SnapshotConfig
from ..model.snapshot import Legend, Source
from ..model.styled_layer import StyledLayer
from ..qgis_plugin_tools.tools.custom_logging import bar_msg
from ..qgis_plugin_tools.tools.decorations import log_if_fails
from ..qgis_plugin_tools.tools.i18n import tr
from ..qgis_plugin_tools.tools.logger_processing import LoggerProcessingFeedBack
from ..qgis_plugin_tools.tools.resources import load_ui, plugin_name, resources_path
from ..qgis_plugin_tools.tools.settings import set_setting

FORM_CLASS = load_ui('main_dialog_dock.ui')
LOGGER = logging.getLogger(plugin_name())


class ExporterDockWidget(QtWidgets.QDockWidget, FORM_CLASS):
    closingPlugin = pyqtSignal()

    # noinspection PyCallByClass
    def __init__(self, iface: QgisInterface, parent=None):
        super(ExporterDockWidget, self).__init__(parent)
        self.setupUi(self)

        self.btn_open_conf.setIcon(QgsApplication.getThemeIcon('/mActionFileOpen.svg'))
        self.btn_save_conf.setIcon(QgsApplication.getThemeIcon('/mActionFileSave.svg'))
        self.btn_settings.setIcon(QgsApplication.getThemeIcon('/propertyicons/settings.svg'))

        self.iface = iface
        # Template can be configured via settings
        self.data_pkg_handler = DataPackageHandler.create()
        self.extent: Optional[QgsRectangle] = None
        self.layer_grid: QGridLayout = self.layer_grid
        self.source_grid: QGridLayout = self.source_grid
        self.layer_rows: Dict = {}
        self.source_rows: Dict = {}
        # TODO: add items here
        self.responsive_items = (
            self.btn_export, self.btn_reset_settings, self.btn_calculate_extent, self.btn_open_conf,
            self.btn_save_conf, self.btn_settings
        )

        self.__set_initial_values()

    # noinspection PyUnresolvedReferences,PyCallByClass
    def __set_initial_values(self):
        # Dialog items
        self.sb_extent_precision.setValue(Settings.extent_precision.get())
        self.le_extent.setText(
            self.extent.toString(self.sb_extent_precision.value()) if self.extent is not None else '')

        self.btn_add_layer_row.setIcon(QgsApplication.getThemeIcon('/mActionAdd.svg'))
        self.btn_add_layer_row.clicked.connect(lambda _: self.__add_layer_row(len(self.layer_rows) + 1))

        self.btn_add_source_row.setIcon(QgsApplication.getThemeIcon('/mActionAdd.svg'))
        self.btn_add_source_row.clicked.connect(lambda _: self.__add_source_row(len(self.source_rows) + 1))

        self.btn_export.clicked.connect(self.run)
        self.btn_reset_settings.clicked.connect(self.__set_initial_values)

        self.cb_crop_layers: QCheckBox
        self.cb_crop_layers.setChecked(Settings.crop_layers.get())
        self.cb_crop_layers.stateChanged.connect(lambda: Settings.crop_layers.set(self.cb_crop_layers.isChecked()))

        for name, snapshot_config in self.data_pkg_handler.config.snapshots[0].items():
            self.input_name.setText(name)
            self.input_title.setText(snapshot_config.title)
            self.input_description.setText(snapshot_config.description)
            break

        for i, source in enumerate(self.data_pkg_handler.snapshot_template.sources, start=1):
            self.__add_source_row(1, source.url, source.title)
        self.__add_layer_row(1)

    def __create_snapshot_config(self):
        snapshot_config_template = None
        for snapshot_config_template in self.data_pkg_handler.config.snapshots[0].values():
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
        snapshot_config.resources = [row['layer'].currentText() for row in self.layer_rows.values()]
        return snapshot_config

    def __set_ui_based_on_snapshot_configuration(self, config_name: str, snaphot_conf: SnapshotConfig):
        self.input_title.setText(snaphot_conf.title)
        self.input_name.setText(config_name)
        self.input_description.setText(snaphot_conf.description)
        self.extent = datapackage_bounds_to_extent(snaphot_conf.bounds)
        self.le_extent.setText(
            self.extent.toString(self.sb_extent_precision.value()) if self.extent is not None else '')

        for row_uuid in list(self.source_rows.keys()):
            self.__remove_row(row_uuid, self.source_rows, self.source_grid)
        for i, source in enumerate(snaphot_conf.sources, start=1):
            self.__add_source_row(i, source.url, source.title)

        for row_uuid in list(self.layer_rows.keys()):
            self.__remove_row(row_uuid, self.layer_rows, self.layer_grid)
        for i, layer_name in enumerate(snaphot_conf.resources, start=1):
            self.__add_layer_row(i)
            layers = QgsProject.instance().mapLayersByName(layer_name)
            if layers:
                row = self.layer_rows[list(self.layer_rows.keys())[i - 1]]
                row['layer'].setLayer(layers[0])
            else:
                LOGGER.warning(tr('Unable to set layer'),
                               extra=bar_msg(tr('There is no layer named {} in the project.', layer_name)))

    def run(self):
        if len(self.f_output.filePath()) == 0 or len(self.input_name.text()) == 0:
            LOGGER.warning(tr('No output path filled'),
                           extra=bar_msg(tr('Fill output path and snapshot name')))
            return
        if self.extent is None:
            LOGGER.warning(tr('No bounds filled'),
                           extra=bar_msg(tr('Fill bounds by clicking Calculate Bounds')))
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
            legend_shape = row['legend_shape'].currentText()
            extent = self.extent if self.cb_crop_layers.isChecked() else None

            task_wrapper = TaskWrapper(id=id, layer=cb.currentLayer(), name=layer_name, extent=extent,
                                       primary=is_primary, legend_shape=legend_shape, output=f'memory:{new_layer_name}',
                                       feedback=row['feedback'],
                                       context=row['context'], executed=self.__styles_to_attributes_finished
                                       )
            LOGGER.info(f"Exporting {layer_name}")
            task_wrappers.append(task_wrapper)

        LOGGER.info(f'Tasks are: {[str(w) for w in task_wrappers]}')

        if len(task_wrappers) == 0:
            LOGGER.warning(tr('No layers selected'),
                           extra=bar_msg(tr('Select at least one layer to create snapshot')))
        else:
            create_styles_to_attributes_tasks(task_wrappers, completed=lambda *args, **kwargs: self.__completed())
            self.__disable_ui()

    def __completed(self, *args, **kwargs):
        all_finished = all(map(lambda x: x['finished'], self.layer_rows.values()))
        if not all_finished:
            return

        self.__enable_ui()
        LOGGER.info(tr('Finished exporting style to attributes'))

        output_path = Path(self.f_output.filePath())

        snapshot_config = self.__create_snapshot_config()
        snapshot_name = self.input_name.text()
        styled_layers = [row['styled_layer'] for row in self.layer_rows.values()]
        snapshot = self.data_pkg_handler.create_snapshot(snapshot_name, snapshot_config, styled_layers)

        output_file = Path(output_path, f'{snapshot_name}.json')

        with open(output_file, 'w') as f:
            json.dump(snapshot.to_dict(), f)

        if Settings.layer_format.get() == LayerFormatOptions.none.value:
            LOGGER.debug('Removing memory layers')
            for row in self.layer_rows.values():
                QgsProject.instance().removeMapLayer(row['styled_layer'].layer_id)

        LOGGER.info(tr('Snapshot succesfully exported'),
                    extra=bar_msg(tr('Snapshot can be found in {}', str(output_file)), success=True))

    def __styles_to_attributes_finished(self, input_layer: QgsVectorLayer, context: QgsProcessingContext, id: uuid.UUID,
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

                output_layer.setMetadata(input_layer.metadata())

                row['styled_layer'] = styled_layer

            row['finished'] = True
        else:
            feedback: LoggerProcessingFeedBack = row['feedback']
            error_msg = feedback.last_report_error
            LOGGER.error(tr('Exporting styles for {} finished with errors', input_layer.name()),
                         extra=bar_msg(details=tr(f'Details: {error_msg}. Check log file for more details')))
            self.__enable_ui()

    # noinspection PyUnresolvedReferences
    @log_if_fails
    def __add_layer_row(self, row_index: int):
        row_uuid = str(uuid.uuid4())
        b_rm = QPushButton(text='', icon=QgsApplication.getThemeIcon('/mActionRemove.svg'))
        b_rm.setToolTip(tr('Remove row'))
        b_rm.clicked.connect(lambda _: self.__remove_row(row_uuid, self.layer_rows, self.layer_grid))

        bx_layer = QgsMapLayerComboBox()
        bx_layer.setFilters(QgsMapLayerProxyModel.Filters(QgsMapLayerProxyModel.Filter.PointLayer |
                                                          QgsMapLayerProxyModel.Filter.PolygonLayer |
                                                          QgsMapLayerProxyModel.Filter.LineLayer))
        cb_primary = QCheckBox(text='')
        combo_box_shape = QComboBox()
        combo_box_shape.addItems(('automatic', 'circle', 'square', 'line'))

        row = {
            'layer': bx_layer,
            'primary': cb_primary,
            'legend_shape': combo_box_shape,
            'rm': b_rm,
            'feedback': LoggerProcessingFeedBack(use_logger=True),
            'context': QgsProcessingContext()
        }
        self.layer_rows[row_uuid] = row
        self.layer_grid.addWidget(b_rm, row_index, 0)
        self.layer_grid.addWidget(bx_layer, row_index, 1)
        self.layer_grid.addWidget(cb_primary, row_index, 2)
        self.layer_grid.addWidget(combo_box_shape, row_index, 3)

    # noinspection PyUnresolvedReferences
    @log_if_fails
    def __add_source_row(self, row_index: int, url: str = '', title: str = ''):
        row_uuid = str(uuid.uuid4())
        b_rm = QPushButton(text='', icon=QgsApplication.getThemeIcon('/mActionRemove.svg'))
        b_rm.setToolTip(tr('Remove row'))
        b_rm.clicked.connect(lambda _: self.__remove_row(row_uuid, self.source_rows, self.source_grid))

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
    def __remove_row(self, row_uuid: str, row_dict: Dict, grid: QGridLayout):
        row = row_dict.pop(row_uuid)
        for widget in row.values():
            if isinstance(widget, QWidget):
                grid.removeWidget(widget)
                widget.hide()
                widget.setParent(None)
            # noinspection PyUnusedLocal
            widget = None

    def __disable_ui(self):
        for item in self.responsive_items:
            item.setEnabled(False)

    def __enable_ui(self):
        for item in self.responsive_items:
            item.setEnabled(True)

    '''
    Pyqt slots (called automatically based on method names)
    '''

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

    @pyqtSlot()
    def on_btn_save_conf_clicked(self):
        LOGGER.debug("Save conf clicked")
        try:
            config = self.__create_snapshot_config()
            name = self.input_name.text()
            self.data_pkg_handler.save_settings_to_project(name, config)
            LOGGER.info(tr('Snapshot configuration saved'),
                        extra=bar_msg(tr('Configuration {} saved successfully', name), success=True))
        except (KeyError, AttributeError):
            LOGGER.warning(tr('Unable to save Snapshot configuration'),
                           extra=bar_msg(tr('Please select layer and bounding box before saving the configuration')))
        except Exception as e:
            LOGGER.exception(tr('Error occurred'),
                             extra=bar_msg(tr('Traceback: {}. Check log file for more details', str(e))))

    @pyqtSlot()
    def on_btn_open_conf_clicked(self):
        LOGGER.info("Open conf clicked")
        confs = self.data_pkg_handler.get_available_settings_from_project()
        if not confs:
            LOGGER.info(tr('No saved Snapshot configurations'),
                        extra=bar_msg(tr('There are no saved snapshot configurations in the project')))
            return

        load_dialog = LoadSnapshotConfDialog(list(confs.keys()))
        result = load_dialog.exec()
        if result:
            config_name = load_dialog.get_chosen_snapshot_config_name()
            LOGGER.debug(f"Chosen snapshot config: {config_name}")
            self.__set_ui_based_on_snapshot_configuration(config_name, confs[config_name])
            LOGGER.info(tr('Snapshot configuration loaded'),
                        extra=bar_msg(tr('Configuration {} loaded successfully', config_name), success=True))
