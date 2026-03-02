from PIL import Image
import time

from .common import Decoder
from ...extractor.fakku import generate_shuffled_map


class FakkuDecoder(Decoder):

    def __init__(self, options, log):
        Decoder.__init__(self, options, log)

    def run(self, pathfmt):
        begin_time = time.time()

        try:
            self.decode(pathfmt)
        except Exception as exc:
            self.log.warning("Unable to decode image due to: %s", exc)
            return

        end_time = time.time() - begin_time
        self.log.debug("Decoded {:.2f} seconds".format(end_time))

    def decode(self, pathfmt):
        TILE_SIZE = 128

        kwdict = pathfmt.kwdict
        seed = kwdict["seed"]
        actual_width = kwdict["width"]
        actual_height = kwdict["height"]
        extension = kwdict["extension"]

        try:
            fmt = Image.registered_extensions()["." + extension]
        except KeyError:
            self.log.error(f"Unsupported extension {extension}")
            raise ValueError()

        img = Image.open(pathfmt.temppath, formats=None)

        # 1. Calculate the grid using the "scrambled" size
        scrambled_width, scrambled_height = img.size
        cols = scrambled_width // TILE_SIZE
        rows = scrambled_height // TILE_SIZE
        total_tiles = cols * rows

        piece_map = generate_shuffled_map(total_tiles, seed)

        # 2. Create a blank canvas of the "actual" size
        clean_canvas = Image.new("RGB", (actual_width, actual_height))

        # 3. Paste all scrambled tiles
        for dest_idx in range(total_tiles):
            source_idx = piece_map[dest_idx]

            # destination coordinates
            dx = (dest_idx % cols) * TILE_SIZE
            dy = (dest_idx // cols) * TILE_SIZE

            # Shift left/up if the tile exceeds the actual canvas
            if dx + TILE_SIZE > actual_width:
                dx = actual_width - TILE_SIZE
            if dy + TILE_SIZE > actual_height:
                dy = actual_height - TILE_SIZE

            # source coordinates
            sx = (source_idx % cols) * TILE_SIZE
            sy = (source_idx // cols) * TILE_SIZE

            # Crop to 128x128
            box = (sx, sy, sx + TILE_SIZE, sy + TILE_SIZE)
            tile = img.crop(box)

            clean_canvas.paste(tile, (dx, dy))

        clean_canvas.save(pathfmt.temppath, format=fmt)


__decoder__ = FakkuDecoder
