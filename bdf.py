import json
import pathlib
import providers
import itertools
import metrics as m

current_path = pathlib.Path(__file__).resolve().parent

export = current_path.joinpath("mojangles.bdf")

assets = current_path.joinpath(pathlib.Path(r"assets/minecraft"))
defaultFont = assets.joinpath(r"font/default.json")

with defaultFont.open() as f:
  desc: dict = json.load(f)
ps: list[dict] = desc["providers"]
provs: list = list(map(lambda it: providers.Provider.new(it), ps))
provs = list(map(lambda it: it.resolve() if type(it) == providers.ReferenceProvider else it, provs))
provs = list(itertools.chain.from_iterable(provs))

preamble = f"""STARTFONT 2.1
FONT -Mojang-Mojangles-Regular-r-Normal--{m.ascender}-{m.ascender * 10}-72-72-p-60-iso10646-1
SIZE {m.em} 72 72
FONTBOUNDINGBOX 12 12 0 -2
STARTPROPERTIES 9
FONT_ASCENT 10
FONT_DESCENT 2
FACE_NAME "Mojangles Regular"
FAMILY_NAME "Mojangles"
FULL_NAME "Mojangles Regular"
SLANT "R"
WEIGHT_NAME "Regular"
CAP_HEIGHT 7
X_HEIGHT 5
ENDPROPERTIES
"""

glyphs = []
chars = []

for prov in provs:
  if type(prov) == providers.BitmapProvider:
    for char in "".join(prov.chars):
      unicode = hex(ord(char))[2:].zfill(4)
      encoding = ord(char)
      if encoding == 0: continue
      if encoding in chars: continue
      dwidth = prov.getActualWidth(char) + 1
      swidth = int((dwidth / m.em) * 1000)
      bitmap = prov.BDFGlyph(char)
      template = f"""STARTCHAR U+{unicode}
ENCODING {encoding}
SWIDTH {swidth} 0
DWIDTH {dwidth} 0
BBX {dwidth} {m.em} 0 {-m.descender}
BITMAP
{bitmap.upper()}
ENDCHAR"""
      glyphs.append(template)
      chars.append(encoding)
  elif type(prov) == providers.SpaceProvider:
    for char in prov.advances.keys():
      unicode = hex(ord(char))[2:].zfill(4)
      encoding = ord(char)
      if encoding == 0: continue
      if encoding in chars: continue
      dwidth = prov.getActualWidth(char) + 1
      swidth = int((dwidth / m.em) * 1000)
      bitmap = prov.BDFGlyph(char)
      template = f"""STARTCHAR U+{unicode}
ENCODING {encoding}
SWIDTH {swidth} 0
DWIDTH {dwidth} 0
BBX {dwidth} {m.em} 0 {-m.descender}
BITMAP
{bitmap.upper()}
ENDCHAR"""
      glyphs.append(template)
      chars.append(encoding)

font = preamble + f"CHARS {len(glyphs)}\n" + "\n".join(glyphs) + "\nENDFONT"

with export.open(mode="w") as f:
  f.write(font)

print(font)