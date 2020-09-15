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
import uuid
from dataclasses import dataclass
from functools import partial
from typing import List, Dict, Callable

from qgis.core import (QgsApplication, QgsProcessingAlgRunnerTask, QgsRectangle, QgsVectorLayer, QgsProcessingFeedback,
                       QgsProcessingContext)

from .algorithms import StyleToAttributesAlg
from .provider import GemeindescanProcessingProvider


@dataclass
class TaskWrapper:
    """
    Helper class for task parameters. Could be replaced with TypedDict, but support for Python 3.8 is not that wide yet
    """
    id: uuid.UUID
    layer: QgsVectorLayer
    name: str
    extent: QgsRectangle
    output: str
    feedback: QgsProcessingFeedback
    context: QgsProcessingContext
    executed: Callable

    @property
    def params(self) -> Dict[str, any]:
        return {
            'EXTENT': self.extent,
            'INPUT': self.layer,
            'NAME': self.name,
            'OUTPUT': self.output
        }

    def __str__(self) -> str:
        return str(self.params)


def create_styles_to_attributes_tasks(task_wrappers: List[TaskWrapper], completed: Callable):
    tasks = []
    if len(task_wrappers) == 0:
        # TODO: custom execption
        raise ValueError()
    for task_wrapper in task_wrappers:
        alg = QgsApplication.processingRegistry().algorithmById(
            f'{GemeindescanProcessingProvider.ID}:{StyleToAttributesAlg.ID}')
        task = QgsProcessingAlgRunnerTask(alg, task_wrapper.params, task_wrapper.context, task_wrapper.feedback)
        # noinspection PyUnresolvedReferences
        task.executed.connect(partial(task_wrapper.executed, task_wrapper.layer, task_wrapper.context, task_wrapper.id))
        # noinspection PyUnresolvedReferences
        task.taskCompleted.connect(completed)
        tasks.append(task)

    main_task = tasks[0]
    for i in range(1, len(tasks)):
        main_task.addSubTask(tasks[i])

    QgsApplication.taskManager().addTask(main_task)
