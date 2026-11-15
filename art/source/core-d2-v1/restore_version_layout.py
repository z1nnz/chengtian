"""Keep established core D2 export paths stable after building a new version.

The shared driver archives prior outputs into a version directory and writes the
new version at the root. This moves the new version to its own directory and
puts the prior version back where existing consumers expect it.
"""
from pathlib import Path
import shutil

ART = Path(__file__).resolve().parents[2]
CASES = [
    ('AL01_RootAltarTerrace', 'v001', 'v002'),
    ('SR01_SurfaceRoot_A', 'v002', 'v003'),
    ('SR01_SurfaceRoot_B', 'v002', 'v003'),
    ('SR01_SurfaceRoot_C', 'v002', 'v003'),
]
for family in ('exports', 'previews'):
    for asset, old, new in CASES:
        root = (ART / family / 'core-d2-v1' / asset).resolve()
        assert root.is_relative_to(ART.resolve())
        old_dir, new_dir = root / old, root / new
        assert old_dir.is_dir(), old_dir
        assert not new_dir.exists(), new_dir
        new_dir.mkdir()
        fresh = [p for p in root.iterdir() if p not in (old_dir, new_dir)]
        assert fresh, root
        for item in fresh:
            shutil.move(str(item), str(new_dir / item.name))
        for item in list(old_dir.iterdir()):
            assert not (root / item.name).exists()
            shutil.move(str(item), str(root / item.name))
        old_dir.rmdir()
        print(f'RESTORED {family} {asset}: {old} at root; {new} in {new_dir}')
