# * Copyright (c) 2020. Authors: see NOTICE file.
# *
# * Licensed under the Apache License, Version 2.0 (the "License");
# * you may not use this file except in compliance with the License.
# * You may obtain a copy of the License at
# *
# *      http://www.apache.org/licenses/LICENSE-2.0
# *
# * Unless required by applicable law or agreed to in writing, software
# * distributed under the License is distributed on an "AS IS" BASIS,
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# * See the License for the specific language governing permissions and
# * limitations under the License.

"""
Here are some packages that may be needed to implement the example plugin format.
Other packages can be added and some can be removed if not used.

"""

from functools import cached_property
from pathlib import Path

import sys, os, io
import numpy as np

from pims.formats.utils.abstract import AbstractChecker, AbstractParser, AbstractReader, AbstractFormat, CachedDataPath
from pims.formats.utils.structures.metadata import ImageMetadata, ImageChannel
from pims.formats.utils.histogram import DefaultHistogramReader
from pims.utils.types import parse_int
from pims.processing.region import Region

# If you want to base the checker class on the file signature, you can use the 
# following checker class:
from pims.formats.utils.checker import SignatureChecker

# If the image format is a pyramid
from pims.formats.utils.structures.pyramid import Pyramid

from pims.utils import UNIT_REGISTRY
from PIL import Image

import binascii

MAGIC_NUMBER = binascii.hexlify('Cytomine test format'.encode('utf8'))

class ExampleChecker(SignatureChecker):
    """ 
    A simple way to implement the checker class is to inherit from the SignatureChecker
    class. Thanks to it, one can use the get_signature method already implemented to
    find the signature of the file.
    """
    @classmethod
    def match(cls, pathlike: CachedDataPath) -> bool:
        buf = cls.get_signature(pathlike)
        return binascii.hexlify(buf[0:20]) == MAGIC_NUMBER
     		
class ExampleParser(AbstractParser):
    """
    Example parser class. Used to parse the file data to use it correctly in 
    PIMS. 
    """
    def parse_main_metadata(self):
        """
        File data necessary for PIMS to work (e.g. image size, pixel type, etc.).
        The information is contained in an ImageMetadata object (see the implementation
        of this object to know the needed information for PIMS).
        
        Returns the ImageMetadata object.
        """
        
        # Get the information from the text file
        with open (str(self.format.path), "r") as hfile:
            sp = hfile.read()

        lines = sp.split("\n")
        properties = {}
        for line in range(1, len(lines)):
            parts = lines[line].split("=")
            properties[parts[0].lower()] = parts[1]
        imd = ImageMetadata()
        
        # Mandatory for the original and spatial representations
        imd.width = parse_int(properties["width"])
        imd.height = parse_int(properties["height"])
        imd.significant_bits = parse_int(properties["bits_per_pixel"])
        
        # Mandatory for the histogram representation
        imd.duration = 1
        imd.n_channels = 3
        imd.depth = 1
        
        # Mandatory information for PIMS
        imd.pixel_type = np.dtype('uint8') # just an example, adapt it as you want
        
        # Mandatory information for showing tiles
        imd.set_channel(ImageChannel(index=0, suggested_name='R'))
        imd.set_channel(ImageChannel(index=1, suggested_name='G'))
        imd.set_channel(ImageChannel(index=2, suggested_name='B'))
        
        """
        To add associated images relative to the format (thumb, macro, label),
        one can use the following lines (and replacing {associated} by the name
        of the image one has access to):
        
        imd.associated_{associated}.width = 
        imd.associated_{associated}.height = 
        imd.associated_{associated}.n_channels = 
        """
        
        return imd
    
    def parse_known_metadata(self):
        """
        File data used in Cytomine but not necessary for PIMS (e.g. physical_size,
        magnification, ...)
        
        Returns an ImageMetadata object.
        
        Note that for the physical_size_{dimension} property, it is needed to specify 
        the unit. Ex: imd.physical_size_x = 0.25*UNIT_REGISTRY("micrometers")
        """
        imd = super().parse_known_metadata()
        
        return imd
        
    def parse_raw_metadata(self):
        """
        Additional information that is not useful either for PIMS or Cytomine.
        Information used when the URL "http://localhost/image/{filepath}/metadata"
        is fetched.
        
        Returns a MetadataStore object.
        
        """
        store = super().parse_raw_metadata()
        
        """
        To fill this MetadataStore object with new image properties, use
        - key for the image property (e.g. model name, calibration time, etc.)
        - value for the value of the image property    
        -> store.set(key, value)
        """
        store.set("Model name", "This is the imaging device name")
        return store
    """
    Other parser methods can be used, e.g. 'PyramidChecker' to fill a Pyramid 
    object if the image file is a pyramid, to fill the acquisition date if needed, etc.
    """
    
class ExampleReader(AbstractReader):
    """
    Example Reader class. The three mandatory functions are listed below. Others
    can be implemented, e.g. to read the macro image or the label image.
    """
    def read_thumb(self, out_width, out_height, precomputed=None, c=None, z=None, t=None):
        main_info = self.format.main_imd
        region = Region(0, 0, main_info.width, main_info.height)
        return self.read_window(region, out_width, out_height, c,z,t)

    def read_window(self, region, out_width, out_height, c=None, z=None, t=None):
        """
        For the purpose of this format example, this function returns a white
        image representing the region of interest.
        """
        # Note: need to have integers for the region dimensions (for the annotation crop request)
        img_array = np.full((int(region.width), int(region.height), 3), 255, dtype=np.uint8) # white image
        #img_array = np.zeros((int(region.width), int(region.height), 3), dtype=np.uint8) # black image
        return Image.fromarray(img_array)

    def read_tile(self, tile, c=None, z=None, t=None):
        return self.read_window(tile, tile.width, tile.height, c, z, t)
        
        
class ExampleFormat(AbstractFormat):
    """
    Definition of the format itself and its classes.
    """
    checker_class = ExampleChecker
    parser_class = ExampleParser
    reader_class = ExampleReader
    histogram_reader_class = DefaultHistogramReader

    """
    The functions describing the format classes inherited from the parent class
    (in the context of this example, the AbstractFormat class) can be adapted.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._enabled = True

    @classmethod
    def get_name(cls):
        return "Example Format"

    @classmethod
    def get_remarks(cls):
        return "Example format used to explain how the integration of a format in PIMS works."
        
    @classmethod
    def is_spatial(cls):
        return True

    @cached_property
    def need_conversion(self):
        return False
