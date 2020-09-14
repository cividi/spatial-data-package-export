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


from functools import partial

# task_variables has been added to path by importing code
import task_variables
from qgis.core import (QgsApplication, QgsProcessingAlgRunnerTask)

from .algorithms import StyleToAttributesAlg
from .provider import GemeindescanProcessingProvider

"""
There is a bug in QGIS https://github.com/qgis/QGIS/issues/38583 that prevents starting tasks
using processing algorithms

This is a temporary workaround until bug is fixed.
"""

params = {
    'EXTENT': task_variables.EXTENT,
    'INPUT': task_variables.LAYER,
    'NAME': task_variables.NAME,
    'OUTPUT': task_variables.OUTPUT
}

alg = QgsApplication.processingRegistry().algorithmById(
    f'{GemeindescanProcessingProvider.ID}:{StyleToAttributesAlg.ID}')
feedback = task_variables.FEEDBACK
context = task_variables.CONTEXT
task = QgsProcessingAlgRunnerTask(alg, params, context, feedback)
# noinspection PyUnresolvedReferences
task.executed.connect(partial(task_variables.EXECUTED, task_variables.LAYER, context))
# noinspection PyUnresolvedReferences
task.taskCompleted.connect(task_variables.COMPLETED)
QgsApplication.taskManager().addTask(task)
