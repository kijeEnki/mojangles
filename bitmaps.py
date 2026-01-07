import pathlib
from PIL import Image

assets = pathlib.Path(__file__).resolve().parent.joinpath(pathlib.Path(r"assets/minecraft"))
textures = assets.joinpath(r"textures")

def getGlyph(file, x: int, y: int, h: int, w: int):
  file = textures.joinpath(file)
  # Returns a rectangle from (x,y) to (x+w, y+h)
  img = Image.open(file)
  cropped = img.crop((x, y, x+w, y+h))
  return cropped

def getWidth(file):
  file = textures.joinpath(file)
  img = Image.open(file)
  return img.width

def getGlyphAsText(img: Image.Image):
  w = img.width
  h = img.height
  text = ""
  for y in range(h):
    for x in range(w):
      color = img.getpixel((x,y))
      text += str(color)
    text += "\n"
  return text[:-1]