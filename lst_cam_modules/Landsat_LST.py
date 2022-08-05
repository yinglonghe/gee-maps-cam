import ee


# MODULES DECLARATION -----------------------------------------------------------
import NCEP_TPW as NCEP_TPW
import cloudmask as cloudmask
import compute_NDVI as NDVI
import compute_FVC as FVC
import compute_emissivity as EM
import SMWalgorithm as LST
# --------------------------------------------------------------------------------

COLLECTION = ee.Dictionary({
  'L4': {
    'TOA': ee.ImageCollection('LANDSAT/LT04/C01/T1_TOA'),
    'SR': ee.ImageCollection('LANDSAT/LT04/C01/T1_SR'),
    'TIR': ['B6',]
  },
  'L5': {
    'TOA': ee.ImageCollection('LANDSAT/LT05/C01/T1_TOA'),
    'SR': ee.ImageCollection('LANDSAT/LT05/C01/T1_SR'),
    'TIR': ['B6',]
  },
  'L7': {
    'TOA': ee.ImageCollection('LANDSAT/LE07/C01/T1_TOA'),
    'SR': ee.ImageCollection('LANDSAT/LE07/C01/T1_SR'),
    'TIR': ['B6_VCID_1','B6_VCID_2'],
  },
  'L8': {
    'TOA': ee.ImageCollection('LANDSAT/LC08/C01/T1_TOA'),
    'SR': ee.ImageCollection('LANDSAT/LC08/C01/T1_SR'),
    'TIR': ['B10','B11']
  }
})

def collection(landsat, date_start, date_end, geometry, use_ndvi, use_cloudmask, cloudlimit):

  # load TOA Radiance/Reflectance
  collection_dict = ee.Dictionary(COLLECTION.get(landsat))

  landsatTOA = ee.ImageCollection(collection_dict.get('TOA')) \
                .filter(ee.Filter.date(date_start, date_end)) \
                .filterBounds(geometry) \
                .filterMetadata('CLOUD_COVER', 'less_than', cloudlimit) \
                .map(cloudmask.toa(use_cloudmask))

  # load Surface Reflectance collection for NDVI
  landsatSR = ee.ImageCollection(collection_dict.get('SR')) \
                .filter(ee.Filter.date(date_start, date_end)) \
                .filterBounds(geometry) \
                .filterMetadata('CLOUD_COVER', 'less_than', cloudlimit) \
                .map(cloudmask.sr(use_cloudmask)) \
                .map(NDVI.addBand(landsat)) \
                .map(FVC.addBand(landsat)) \
                .map(NCEP_TPW.addBand) \
                .map(EM.addBand(landsat,use_ndvi))

  # combine collections
  # all channels from surface reflectance collection
  # except tir channels: from TOA collection
  # select TIR bands
  tir = ee.List(collection_dict.get('TIR'))
  landsatALL = (landsatSR.combine(landsatTOA.select(tir), True))

  # compute the LST
  landsatLST = landsatALL.map(LST.addBand(landsat))

  return landsatLST
