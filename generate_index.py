import json
import yaml
import os
import math
import rect_layout
from PIL import Image

dimension_axes = {
  'Size': 0,
  'Length': 0,
  'Width': 0,
  'Diameter': 0,
  'Height': 1,
}

def get_parts(path):
  part_values = {}
  keys = ['Universe','Faction']
  keys.reverse()

  remainder = path
  parts = []
  while remainder:
    (remainder, part) = os.path.split(remainder)
    parts.append(part)

  parts.pop() # Strip off "images"
  while len(parts) and len(keys):
    part_values[keys.pop()] = parts.pop()

  return part_values

def set_default(d, k, defaults):
  combined = {}
  combined.update(defaults)
  combined.update(d[k])
  d[k] = combined

def gather_yaml(path):
  ships = []
  extra_info = get_parts(path)
  for e in os.listdir(path):
    fullpath = os.path.join(path, e)
    if os.path.isfile(fullpath):
      if e.endswith('.yaml'):
        for ship in yaml.load_all(open(fullpath, 'r')):
          try:
            set_default(ship, 'info', extra_info)
            ship['path'] = path

            # Get image width/height
            im = Image.open(os.path.join(path, ship['filename']))
            ship['image_size'] = im.size

            # Add scale information
            m = px = None
            if 'm_per_px' in ship:
              m_per_px = ship['m_per_px']
              if isinstance(m_per_px, str):
                (m, px) = m_per_px.split('/')
            else:
              for (dim, axis) in dimension_axes.items():
                if dim in ship['info']:
                  m = ship['info'][dim]
                  px = im.size[axis]
                  break

            if m and px:
              ship['m_per_px'] = float(m)/float(px)
              ship['real_size'] = [
                d*ship['m_per_px']
                for d in ship['image_size']
              ]

            if 'm_per_px' not in ship:
              raise ArithmeticError("Couldn't determine m/px!")

            ships.append(ship)
          except ValueError as e:
            print("Failed to load ship from {}:\n{}\n{}".format(fullpath, str(e), str(ship)))
          except IOError as e:
            print("Failed to load image from {}:\n{}\n{}".format(fullpath, str(e), str(ship)))
          except ArithmeticError as e:
            print("Failed to load ship from {}:\n{}\n{}".format(fullpath, str(e), str(ship)))

    elif os.path.isdir(fullpath):
      ships += gather_yaml(fullpath)

  return ships

def sort_ship(ship):
  size_order = None
  if 'real_size' in ship:
    size_order = ship['real_size'][0]*ship['real_size'][1]
  else:
    size_order = 0

  return (size_order, ship['info'].get('Universe'), ship['info'].get('Faction'))

ships = gather_yaml('images')
ships.sort(key = sort_ship)

layout = rect_layout.Layout(24)
for s in ships:
  if 'm_per_px' not in s:
    print("Skipping {}, no size info!".format(s['info']['Name']))
  if 'image_size' not in s:
    print("Skipping {}, no image info!".format(s['info']['Name']))

  rect = layout.add_rect([
    px * s['m_per_px']
    for px in s['image_size']
  ])

  s['position'] = rect.center

json.dump(ships, open('ships.json', 'w'))
