import ee
import ASTER_bare_emiss as ASTERGED


def addBand(dynamic):

  def em_band(band, image):

    aster = ee.Image('NASA/ASTER_GED/AG100_003') \
      .clip(image.geometry())

    orig = aster.select(band).multiply(0.001)
    dynam = image.expression('fvc*0.99+(1-fvc)*em_bare',{
      'fvc':image.select('FVC'),
      'em_bare':ASTERGED.emiss_bare_band(band, image)})
    em = ee.Image(ee.Algorithms.If(dynamic,dynam,orig))

    return em

  def wrap(image):

    # get ASTER emissivity
    em10 = em_band('emissivity_band10', image)
    em11 = em_band('emissivity_band11', image)
    em12 = em_band('emissivity_band12', image)
    em13 = em_band('emissivity_band13', image)
    em14 = em_band('emissivity_band14', image)

    bbe = image.expression('0.128 + 0.014*em10 + 0.145*em11 + 0.241*em12 + 0.467*em13 + 0.004*em14',
      {'em10':em10,'em11':em11,'em12':em12,'em13':em13,'em14':em14})

    return image.addBands(bbe.rename('BBE'))
  
  return wrap