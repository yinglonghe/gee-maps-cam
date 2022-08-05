import ee


def emiss_bare_band(band, image):
  # get ASTER emissivity
  aster = ee.Image("NASA/ASTER_GED/AG100_003")

  #get ASTER FVC from NDVI
  aster_ndvi = aster.select('ndvi').multiply(0.01)

  aster_fvc = aster_ndvi.expression('((ndvi-ndvi_bg)/(ndvi_vg - ndvi_bg))**2',
    {'ndvi':aster_ndvi,'ndvi_bg':0.2,'ndvi_vg':0.86})
  aster_fvc = aster_fvc.where(aster_fvc.lt(0.0),0.0)
  aster_fvc = aster_fvc.where(aster_fvc.gt(1.0),1.0)

  # bare ground emissivity functions for each band
  emiss_bare_band = image.expression('(EM - 0.99*fvc)/(1.0-fvc)',{
    'EM':aster.select(band).multiply(0.001),
    'fvc':aster_fvc}) \
    .clip(image.geometry())

  return emiss_bare_band
