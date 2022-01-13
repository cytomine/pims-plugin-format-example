#  * Copyright (c) 2020-2021. Authors: see NOTICE file.
#  *
#  * Licensed under the GNU Lesser General Public License, Version 2.1 (the "License");
#  * you may not use this file except in compliance with the License.
#  * You may obtain a copy of the License at
#  *
#  *      https://www.gnu.org/licenses/lgpl-2.1.txt
#  *
#  * Unless required by applicable law or agreed to in writing, software
#  * distributed under the License is distributed on an "AS IS" BASIS,
#  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  * See the License for the specific language governing permissions and
#  * limitations under the License.

VERSION = (0, 0, 0)

name = "example" # replace "example" by the name of your format
__title__ = f'pims-plugin-format-{name}'
__description__ = f'{name} plugin for PIMS'
__plugin__ = f'{name}'
__url__ = 'https://doc.uliege.cytomine.org' # URL for plugin format documentation
__version__ = '.'.join(map(str, VERSION))
__license__ = ''
__copyright__ = ''
__author__ = ''
__email__ = ''
