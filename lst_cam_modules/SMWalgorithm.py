import ee

import SMW_coefficients as SMWcoef
# coefficients for the Statistical Mono-Window Algorithm
# SMWcoef = require('users/yhephd/yhe_home:modules/SMW_coefficients.js')

# Function to create a lookup between two columns in a
# feature collection
def get_lookup_table(fc, prop_1, prop_2):
  reducer = ee.Reducer.toList().repeat(2)
  lookup = fc.reduceColumns(reducer, [prop_1, prop_2])
  return ee.List(lookup.get('list'))


def addBand(landsat):

  def wrap(image):

    # Select algorithm coefficients
    coeff_SMW = ee.FeatureCollection(ee.Algorithms.If(landsat=='L4',SMWcoef.coeff_SMW_L4,
                                        ee.Algorithms.If(landsat=='L5',SMWcoef.coeff_SMW_L5,
                                        ee.Algorithms.If(landsat=='L7',SMWcoef.coeff_SMW_L7,
                                        SMWcoef.coeff_SMW_L8))))

    # Create lookups for the algorithm coefficients
    A_lookup = get_lookup_table(coeff_SMW, 'TPWpos', 'A')
    B_lookup = get_lookup_table(coeff_SMW, 'TPWpos', 'B')
    C_lookup = get_lookup_table(coeff_SMW, 'TPWpos', 'C')

    # Map coefficients to the image using the TPW bin position
    A_img = image.remap(A_lookup.get(0), A_lookup.get(1),0.0,'TPWpos').resample('bilinear')
    B_img = image.remap(B_lookup.get(0), B_lookup.get(1),0.0,'TPWpos').resample('bilinear')
    C_img = image.remap(C_lookup.get(0), C_lookup.get(1),0.0,'TPWpos').resample('bilinear')

    # select TIR band
    tir = ee.String(ee.Algorithms.If(landsat=='L8','B10',
                        ee.Algorithms.If(landsat=='L7','B6_VCID_1',
                        'B6')))
    # compute the LST
    lst = image.expression(
      'A*Tb1/em1 + B/em1 + C - 273.15',
         {'A': A_img,
          'B': B_img,
          'C': C_img,
          'em1': image.select('EM'),
          'Tb1': image.select(tir)
         }).updateMask(image.select('TPW').lt(0).Not())

    return image.addBands(lst.rename('LST'))
  
  return wrap