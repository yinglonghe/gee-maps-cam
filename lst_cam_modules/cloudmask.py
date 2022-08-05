import ee


# cloudmask for TOA data
def toa(use_cloudmask):

  def wrap(image):
    qa = image.select('BQA')
    mask = qa.bitwiseAnd(1 << 4).eq(0)
    return ee.Image(ee.Algorithms.If(use_cloudmask, image.updateMask(mask), image))
  
  return wrap

# cloudmask for SR data
def sr(use_cloudmask):

  def wrap(image):
    qa = image.select('pixel_qa')
    mask = qa.bitwiseAnd(1 << 3).eq(0) \
      .And(qa.bitwiseAnd(1 << 5).eq(0))
    return ee.Image(ee.Algorithms.If(use_cloudmask, image.updateMask(mask), image))
  
  return wrap
