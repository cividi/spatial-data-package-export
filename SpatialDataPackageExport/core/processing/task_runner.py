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
import uuid
from functools import partial
from typing import Any, Callable, Dict, List, Optional

from qgis.core import (
    QgsApplication,
    QgsProcessingAlgRunnerTask,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsRectangle,
    QgsVectorLayer,
)

from .algorithms import StyleToAttributesAlg
from .provider import SpatialDataPackageProcessingProvider


class TaskWrapper:
    """
    Helper class for task parameters. Could be replaced with TypedDict,
    but support for Python 3.8 is not that wide yet
    """

    def __init__(
        self,
        id: uuid.UUID,
        layer: QgsVectorLayer,
        name: str,
        extent: Optional[QgsRectangle],
        primary: bool,
        legend_shape: str,
        output: str,
        feedback: QgsProcessingFeedback,
        context: QgsProcessingContext,
        executed: Callable,
    ) -> None:
        self.id = id
        self.layer = layer
        self.name = name
        self.extent = extent
        self.primary = primary
        self.legend_shape = legend_shape
        self.output = output
        self.feedback = feedback
        self.context = context
        self.executed = executed

    @property
    def params(self) -> Dict[str, Any]:
        return {
            "EXTENT": self.extent,
            "INPUT": self.layer,
            "NAME": self.name,
            "PRIMARY": self.primary,
            "LEGEND_SHAPE": self.legend_shape,
            "OUTPUT": self.output,
        }

    def __str__(self) -> str:
        return str(self.params)


def create_styles_to_attributes_tasks(
    task_wrappers: List[TaskWrapper], completed: Callable
) -> None:
    tasks = []
    if len(task_wrappers) == 0:
        # TODO: custom execption
        raise ValueError()
    for task_wrapper in task_wrappers:
        alg = QgsApplication.processingRegistry().algorithmById(
            f"{SpatialDataPackageProcessingProvider.ID}:{StyleToAttributesAlg.ID}"
        )
        task = QgsProcessingAlgRunnerTask(
            alg, task_wrapper.params, task_wrapper.context, task_wrapper.feedback
        )
        task.setDependentLayers([task_wrapper.layer])
        # noinspection PyUnresolvedReferences
        task.executed.connect(
            partial(
                task_wrapper.executed,
                task_wrapper.layer,
                task_wrapper.context,
                task_wrapper.id,
            )
        )
        # noinspection PyUnresolvedReferences
        task.taskCompleted.connect(completed)
        tasks.append(task)

    main_task = tasks[0]
    for i in range(1, len(tasks)):
        main_task.addSubTask(tasks[i])

    QgsApplication.taskManager().addTask(main_task)
