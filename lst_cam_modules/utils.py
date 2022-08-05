import ee


def getGeometry(asset):

  coord = ee.FeatureCollection(asset) \
    .sort('id') \
    .geometry() \
    .coordinates()

  geometry = ee.Geometry.Polygon([coord])

  return geometry

  # Map.addLayer(geometry, {}, 'geometry', 1, 0.5)
  # Map.centerObject(geometry, 13)

def maskInside(image, geometry):
  mask = ee.Image.constant(1.0).clip(geometry).mask().Not()
  return image.addBands(mask.rename('geometry'))