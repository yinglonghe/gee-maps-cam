import ee


def addBand(landsat):
  def wrap(image):

    # choose bands
    nir = ee.String(ee.Algorithms.If(landsat=='L8','B5','B4'))
    red = ee.String(ee.Algorithms.If(landsat=='L8','B4','B3'))

    # compute NDVI
    return image.addBands(image.expression('(nir-red)/(nir+red)',{
      'nir':image.select(nir).multiply(0.0001),
      'red':image.select(red).multiply(0.0001)
    }).rename('NDVI'))

  return wrap