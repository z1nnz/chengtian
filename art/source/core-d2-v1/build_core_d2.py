"""core-d2-v1: pieces the D2 ancient tree block design lists as missing. Runs the village-houses-b build driver on this kit's assets.

  blender --background --factory-startup --python art/source/core-d2-v1/build_core_d2.py -- AL01_RootAltarTerrace --force
  ... -- AL01_RootAltarTerrace --preview <dir>     procedural look only, no bake or export
"""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'village-houses-b')); sys.path.insert(0, str(HERE))
import build_village_houses_b as B
import al_altar

B.KIT = 'core-d2-v1'
B.ASSETS.clear()
al_altar.register(B.ASSETS)

if __name__ == '__main__':
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    ids = [a for a in argv if a in B.ASSETS] or list(B.ASSETS)
    if '--preview' in argv:
        out = Path(argv[argv.index('--preview') + 1])
        for aid in ids: B.preview(aid, out)
    else:
        for aid in ids: B.run(aid, '--force' in argv)
