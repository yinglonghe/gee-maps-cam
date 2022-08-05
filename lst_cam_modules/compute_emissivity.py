import ee


import ASTER_bare_emiss as ASTERGED
# ASTERGED = require('users/yhephd/yhe_home:modules/ASTER_bare_emiss.js')

# this function computes the emissivity of the
# Landsat TIR band using ASTER and FVC
def addBand(landsat, use_ndvi):
  def wrap(image):

    c13 = ee.Number(ee.Algorithms.If(landsat=='L4',0.3222,
                            ee.Algorithms.If(landsat=='L5',-0.0723,
                            ee.Algorithms.If(landsat=='L7',0.2147,
                            ee.Algorithms.If(landsat=='L8',0.6820)))))
    c14 = ee.Number(ee.Algorithms.If(landsat=='L4',0.6498,
                            ee.Algorithms.If(landsat=='L5',1.0521,
                            ee.Algorithms.If(landsat=='L7',0.7789,
                            ee.Algorithms.If(landsat=='L8',0.2578)))))
    c = ee.Number(ee.Algorithms.If(landsat=='L4',0.0272,
                            ee.Algorithms.If(landsat=='L5',0.0195,
                            ee.Algorithms.If(landsat=='L7',0.0059,
                            ee.Algorithms.If(landsat=='L8',0.0584)))))

    # get ASTER emissivity
    # convolve to Landsat band
    emiss_bare = image.expression('c13*EM13 + c14*EM14 + c',{
      'EM13':ASTERGED.emiss_bare_band('emissivity_band13', image),
      'EM14':ASTERGED.emiss_bare_band('emissivity_band14', image),
      'c13':ee.Image(c13),
      'c14':ee.Image(c14),
      'c':ee.Image(c)
      })

    # compute the dynamic emissivity for Landsat
    EMd = image.expression('fvc*0.99+(1-fvc)*em_bare',
      {'fvc':image.select('FVC'),'em_bare':emiss_bare})

    # compute emissivity directly from ASTER
    # without vegetation correction
    # get ASTER emissivity
    aster = ee.Image("NASA/ASTER_GED/AG100_003") \
      .clip(image.geometry())
    EM0 = image.expression('c13*EM13 + c14*EM14 + c',{
      'EM13':aster.select('emissivity_band13').multiply(0.001),
      'EM14':aster.select('emissivity_band14').multiply(0.001),
      'c13':ee.Image(c13),
      'c14':ee.Image(c14),
      'c':ee.Image(c)
      })

    # select which emissivity to output based on user selection
    EM = ee.Image(ee.Algorithms.If(use_ndvi,EMd,EM0))

    return image.addBands(EM.rename('EM'))

  return wrap