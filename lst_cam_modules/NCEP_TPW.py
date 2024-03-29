import ee


def addBand(image):

  # first select the day of interest
  date = ee.Date(image.get('system:time_start'))
  year = ee.Number.parse(date.format('yyyy'))
  month = ee.Number.parse(date.format('MM'))
  day = ee.Number.parse(date.format('dd'))
  date1 = ee.Date.fromYMD(year,month,day)
  date2 = date1.advance(1,'days')

  # function compute the time difference from landsat image
  def datedist(image):
    return image.set('DateDist',
      ee.Number(image.get('system:time_start')) \
      .subtract(date.millis()).abs())

  # load atmospheric data collection
  TPWcollection = ee.ImageCollection('NCEP_RE/surface_wv') \
                  .filter(ee.Filter.date(date1.format('yyyy-MM-dd'), date2.format('yyyy-MM-dd'))) \
                  .map(datedist)

  # select the two closest model times
  closest = (TPWcollection.sort('DateDist')).toList(2)

  # check if there is atmospheric data in the wanted day
  # if not creates a TPW image with non-realistic values
  # these are then masked in the SMWalgorithm function (prevents errors)
  tpw1 = ee.Image(ee.Algorithms.If(closest.size().eq(0), ee.Image.constant(-999.0),
                      ee.Image(closest.get(0)).select('pr_wtr') ))
  tpw2 = ee.Image(ee.Algorithms.If(closest.size().eq(0), ee.Image.constant(-999.0),
                        ee.Algorithms.If(closest.size().eq(1), tpw1,
                        ee.Image(closest.get(1)).select('pr_wtr') )))

  time1 = ee.Number(ee.Algorithms.If(closest.size().eq(0), 1.0,
                        ee.Number(tpw1.get('DateDist')).divide(ee.Number(21600000)) ))
  time2 = ee.Number(ee.Algorithms.If(closest.size().lt(2), 0.0,
                        ee.Number(tpw2.get('DateDist')).divide(ee.Number(21600000)) ))

  tpw = tpw1.expression('tpw1*time2+tpw2*time1',
                            {'tpw1':tpw1,
                            'time1':time1,
                            'tpw2':tpw2,
                            'time2':time2
                            }).clip(image.geometry())

  # SMW coefficients are binned by TPW values
  # find the bin of each TPW value
  pos = tpw.expression(
    "value = (TPW>0 && TPW<=6) ? 0" + \
    ": (TPW>6 && TPW<=12) ? 1" + \
    ": (TPW>12 && TPW<=18) ? 2" + \
    ": (TPW>18 && TPW<=24) ? 3" + \
    ": (TPW>24 && TPW<=30) ? 4" + \
    ": (TPW>30 && TPW<=36) ? 5" + \
    ": (TPW>36 && TPW<=42) ? 6" + \
    ": (TPW>42 && TPW<=48) ? 7" + \
    ": (TPW>48 && TPW<=54) ? 8" + \
    ": (TPW>54) ? 9" + \
    ": 0",{'TPW': tpw}) \
    .clip(image.geometry())

  # add tpw to image as a band
  withTPW = (image.addBands(tpw.rename('TPW'),['TPW'])).addBands(pos.rename('TPWpos'),['TPWpos'])

  return withTPW