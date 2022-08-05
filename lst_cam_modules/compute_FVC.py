

def addBand(landsat):
  def wrap(image):

    ndvi = image.select('NDVI')

    # Compute FVC
    fvc = image.expression('((ndvi-ndvi_bg)/(ndvi_vg - ndvi_bg))**2',
      {'ndvi':ndvi,'ndvi_bg':0.2,'ndvi_vg':0.86})
    fvc = fvc.where(fvc.lt(0.0),0.0)
    fvc = fvc.where(fvc.gt(1.0),1.0)

    return image.addBands(fvc.rename('FVC'))
  
  return wrap