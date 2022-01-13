
from PIL import Image
import os, io, json
import urllib.request
from fastapi import APIRouter
from pims.formats import FORMATS
from pims.importer.importer import FileImporter
from pims.files.file import (ORIGINAL_STEM, Path, SPATIAL_STEM, HISTOGRAM_STEM)
from pims.api.utils.models import HistogramType
from pims.processing.histograms.utils import build_histogram_file
from tests.utils.formats import info_test, thumb_test, resized_test, mask_test, crop_test, crop_null_annot_test, histogram_perimage_test
from pims.formats.utils.factories import FormatFactory

import pytest

def get_image(path, filename):
    # If image does not exist locally -> create it
    if not os.path.exists(path):
        os.mkdir("/data/pims/upload_test_example")
	    
    if not os.path.exists(os.path.join(path,filename)):
        try:
            with open(os.path.join(path, filename), 'w') as f:
                f.write('Cytomine test format\nWIDTH=200\nHEIGHT=80\nTILE_WIDTH=256\nTILE_HEIGHT=256\nBITS_PER_PIXEL=8')
        except Exception as e:
            print("Could not create example file.")
            print(e)
	
    if not os.path.exists(os.path.join(path, "processed")):
        try:
            fi = FileImporter(f"/data/pims/upload_test_example/{filename}")
            fi.upload_dir = "/data/pims/upload_test_example"
            fi.processed_dir = fi.upload_dir / Path("processed")
            fi.mkdir(fi.processed_dir)
        except Exception as e:
            print(path + "processed could not be created")
            print(e)
    if not os.path.exists(os.path.join(path, "processed/visualisation.example")):
        try:
            fi = FileImporter(f"/data/pims/upload_test_example/{filename}")
            fi.upload_dir = Path("/data/pims/upload_test_example")
            fi.processed_dir = fi.upload_dir / Path("processed")
            fi.upload_path = Path(os.path.join(path,filename))
            original_filename = Path(f"{ORIGINAL_STEM}.example")
            fi.original_path = fi.processed_dir / original_filename
            fi.mksymlink(fi.original_path, fi.upload_path)
            spatial_filename = Path(f"{SPATIAL_STEM}.example")
            fi.spatial_path = fi.processed_dir / spatial_filename
            fi.mksymlink(fi.spatial_path, fi.original_path)
        except Exception as e:
            print("Importation of images could not be done")
            print(e)
			
    if not os.path.exists(os.path.join(path, "processed/histogram")):
        if os.path.exists(os.path.join(path, "processed")):
            fi = FileImporter(f"/data/pims/upload_test_example/{filename}")
            fi.upload_dir = Path("/data/pims/upload_test_example")
            fi.processed_dir = fi.upload_dir / Path("processed")
            original_filename = Path(f"{ORIGINAL_STEM}.example")
            fi.original_path = fi.processed_dir / original_filename
        try:
            from pims.files.image import Image
            fi.histogram_path = fi.processed_dir/Path(HISTOGRAM_STEM) 
            format = FormatFactory().match(fi.original_path)
            fi.original = Image(fi.original_path, format=format)
            fi.histogram = build_histogram_file(fi.original, fi.histogram_path, HistogramType.FAST)
        except Exception as e:
            print("Creation of histogram representation could not be done")
            print(e)

def get_image_properties(path, filename):
    # Compare with the values extracted from the test file directly
    with open (os.path.join(path, filename)) as hfile:
        sp = hfile.read()

    lines = sp.split("\n")
    properties = {}
    for line in range(1, len(lines)):
        parts = lines[line].split("=")
        properties[parts[0].lower()] = parts[1]
    return properties
			
def test_example_exists(image_path_example):
	# Test if the file exists, either locally either with the OAC
	path, filename = image_path_example
	get_image(path, filename)
	assert os.path.exists(os.path.join(path,filename)) == True
	
def test_example_info(client, image_path_example):
    path, filename = image_path_example
    response = client.get(f'/image/upload_test_example/{filename}/info')
    properties = get_image_properties(path, filename)
    assert response.status_code == 200
    assert "example" in response.json()['image']['original_format'].lower()
    assert response.json()['image']['width'] == int(properties["width"])
    assert response.json()['image']['height'] == int(properties["height"])
    assert response.json()['image']['significant_bits'] == int(properties["bits_per_pixel"])

def test_example_norm_tile(client, image_path_example):
    path, filename = image_path_example
    response = client.get(f"/image/upload_test_example/{filename}/normalized-tile/level/0/ti/0", headers={"accept": "image/jpeg"})
    assert response.status_code == 200
    img_response = Image.open(io.BytesIO(response.content))
    width_resp, height_resp = img_response.size
    properties = get_image_properties(path, filename)
    # The size of a normalized tile must be 256 or the size of the image if the
    # dimension size is lower than 256.
    assert width_resp == 256 or width_resp == int(properties["width"])
    assert height_resp == 256 or height_resp == int(properties["height"])

def test_example_thumb(client, image_path_example):
    _, filename = image_path_example
    thumb_test(client, filename, "example")
		
def test_example_resized(client, image_path_example):
    _, filename = image_path_example
    resized_test(client, filename, "example")

def test_example_mask(client, image_path_example):
    _, filename = image_path_example
    mask_test(client, filename, "example")
		
def test_example_crop(client, image_path_example):
    _, filename = image_path_example
    crop_test(client, filename, "example")

@pytest.mark.skip(reason = "wrong response status code")
def test_example_crop_null_annot(client, image_path_example):
    _, filename = image_path_example
    crop_null_annot_test(client, filename, "example")
	
def test_example_histogram_perimage(client, image_path_example):
    _, filename = image_path_example
    histogram_perimage_test(client, filename, "example")
	
