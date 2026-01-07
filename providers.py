import json
import pathlib
import bitmaps
import metrics
from math import ceil

class Provider:
  @staticmethod
  def new(desc: dict):
    kind = desc["type"]
    match kind:
      case "bitmap":
        return BitmapProvider(desc)
      case "space":
        return SpaceProvider(desc)
      case "reference":
        return ReferenceProvider(desc)

class BitmapProvider:
  def __init__(self, desc: dict):
    self.em = desc.get("height", 8)
    self.asc = desc["ascent"]
    self.chars = desc["chars"]
    self.file = desc["file"].removeprefix("minecraft:")

    self.rows = len(self.chars)
    self.cols = 16 # Sixteen in all actual minecraft assets.

    self.width = bitmaps.getWidth(self.file)
    self.charWidth = int(self.width / self.cols)
  
  def __repr__(self):
    return f"<BitmapProvider to {self.file}>"

  def hasChar(self, char: str):
    char = char[0]
    allChars = "".join(self.chars)
    return (char in allChars)

  def locateChar(self, char: str):
    char = char[0]
    if not self.hasChar(char): raise KeyError("Glyph not in this file.")
    for y in range(len(self.chars)):
      if char in self.chars[y]:
        for x in range(len(self.chars[y])):
          if char == self.chars[y][x]:
            return (x, y)
    raise KeyError("Could not find glyph.")

  def getImage(self, char: str):
    char = char[0]
    (x, y) = self.locateChar(char)
    y *= self.em
    x *= self.charWidth
    h = self.em
    w = self.charWidth
    return bitmaps.getGlyph(self.file, x, y, h, w)
  
  def getTextGlyph(self, char: str):
    char = char[0]
    img = self.getImage(char)
    return bitmaps.getGlyphAsText(img)

  def getActualWidth(self, char: str):
    char = char[0]
    textChar = self.getTextGlyph(char)
    lines = textChar.split()
    full = len(lines[0])
    minZ = full
    for line in lines:
      if line == "0" * full: continue
      stripped = line.rstrip("0")
      zeroes = full - len(stripped)
      minZ = min(minZ, zeroes)
    return full - minZ

  def fixWidth(self, char: str):
    textChar = self.getTextGlyph(char)
    actualWidth = self.getActualWidth(char)
    lines = textChar.split()
    new = ""
    for line in lines:
      new += line[:actualWidth+1]
      new += "\n"
    return new[:-1]
  
  def padTextGlyph(self, char: str):
    char = char[0]
    textChar = self.fixWidth(char)
    charWidth = self.getActualWidth(char) + 1
    onTop = metrics.ascender - self.asc
    onBottom = abs(metrics.descender - (self.em - self.asc))
    newStr = (("0" * charWidth + "\n") * onTop) + textChar + ("\n" + ("0" * charWidth) * onBottom)
    return newStr

  def BDFGlyph(self, char: str):
    char = char[0]
    textChar = self.padTextGlyph(char)
    charWidth = len(textChar.split()[0])
    pad = 8 * ceil(charWidth / 8) - charWidth
    hexChar = ""
    for line in textChar.split():
      hexChar += hex(int(line + "0"*pad, base=2))[2:].zfill(2 * ceil(charWidth / 8))
      hexChar += "\n"
    return hexChar[:-1]

class SpaceProvider:
  def __init__(self, desc: dict):
    self.advances = desc["advances"]
  
  def hasChar(self, char: str):
    char = char[0]
    return char in self.advances.keys()

  def getActualWidth(self, char: str):
    char = char[0]
    if not self.hasChar(char): raise KeyError("Glyph not in this file.")
    return self.advances[char]
  
  def BDFGlyph(self, char: str):
    char = char[0]
    charWidth = self.getActualWidth(char)
    return "0"*ceil(charWidth / 8)*2

class ReferenceProvider:
  def __init__(self, desc: dict):
    self.id = desc["id"].removeprefix("minecraft:")

  def __repr__(self):
    return f"<ReferenceProvider to {self.id}>"
  
  def resolve(self):
    path = (pathlib.Path(__file__)
            .resolve()
            .parent
            .joinpath(pathlib.Path(r"assets/minecraft/font")))
    obj = path.joinpath(self.id + ".json")
    d = json.load(obj.open())["providers"]
    return [Provider.new(p) for p in d]