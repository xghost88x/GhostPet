"""Art regression checks: cat anatomy and decorated cottage collision footprints."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import unittest
from PySide6.QtGui import QImage, QPainter
from PySide6.QtWidgets import QApplication
from adopted_sprites import draw_adopted_pet
from cottage_art import built_in_occupied, pixel_cottage
from house import TILE, W, H, walls_for_layout


class SpriteAndArtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # QFont inside room labels requires a live QApplication.
        cls.app = QApplication.instance() or QApplication(["ghostpet-visual-tests"])

    def test_cat_has_full_silhouette_with_ears_tail_and_whisker_extents(self):
        img=QImage(124,116,QImage.Format.Format_ARGB32)
        img.fill(0)
        p=QPainter(img)
        try:
            draw_adopted_pet(p,124,116,{"species":"Cat","name":"Fuzz"},3,4,1)
        finally:
            p.end()
        opaque=[(x,y) for x in range(124) for y in range(116)
                if img.pixelColor(x,y).alpha()>0]
        self.assertGreater(len(opaque),2000,"Cat sprite should fill a readable silhouette")
        self.assertLess(min(y for x,y in opaque),24,"Two ears must rise above head")
        self.assertGreater(max(x for x,y in opaque),102,"Tail should extend away from body")
        self.assertLess(min(x for x,y in opaque),12,"Whiskers must extend to the sides")
        self.assertGreater(max(y for x,y in opaque),105,"Distinct paws at bottom")
        self.assertGreaterEqual(len({img.pixel(x,y) for x,y in opaque}),5)

    def test_cottage_scenes_render_differently_and_leave_paths(self):
        samples=[]
        for layout in ("cottage","open","garden"):
            im=QImage(W*TILE,H*TILE,QImage.Format.Format_ARGB32)
            im.fill(0)
            p=QPainter(im)
            try:
                pixel_cottage(p,layout,walls_for_layout(layout))
            finally:
                p.end()
            samples.append(im.pixel(510,292))
            self.assertGreater(len({im.pixel(x,y) for x in range(0,W*TILE,5)
                                    for y in range(0,H*TILE,5)}),60)
            reserved=built_in_occupied(layout)
            self.assertTrue(reserved)
            self.assertTrue(all(tile not in walls_for_layout(layout) for tile in reserved))
            self.assertNotIn((2,3),reserved)
            self.assertNotIn((3,6),reserved)
            self.assertNotIn((12,6),reserved)
        self.assertNotEqual(samples[0],samples[2],
                            "Garden layout should visibly replace nursery furnishings")

    def test_upgrades_have_substantial_visible_floor_changes(self):
        rendered = []
        for plan in ("cottage", "open", "garden"):
            canvas = QImage(W*TILE, H*TILE, QImage.Format.Format_ARGB32)
            canvas.fill(0)
            painter = QPainter(canvas)
            try:
                pixel_cottage(painter, plan, walls_for_layout(plan))
            finally:
                painter.end()
            rendered.append(canvas)

        def difference(first, second):
            changed = 0
            total = 0
            # Sample the real pixels, not only the layout key or labels.
            for y in range(20, H*TILE-20, 5):
                for x in range(20, W*TILE-20, 5):
                    total += 1
                    changed += first.pixel(x,y) != second.pixel(x,y)
            return changed / total

        # Intentional minimum coverage far above the old recolor-pass bars:
        # nearly half the canvas should change when buying a new floor plan.
        self.assertGreater(difference(rendered[0],rendered[1]), .43,
                           "Open Plan must show a dramatically different interior")
        self.assertGreater(difference(rendered[1],rendered[2]), .43,
                           "Garden must show a dramatically different conservatory")

    def test_desktop_cat_is_smaller_than_cottage_portal(self):
        img = QImage(124, 116, QImage.Format.Format_ARGB32)
        img.fill(0)
        painter = QPainter(img)
        try:
            draw_adopted_pet(painter, 124, 116,
                             {"species":"Cat","name":"Fuzz"}, 1, scale=2)
        finally:
            painter.end()
        pixels = [(x,y) for y in range(116) for x in range(124)
                  if img.pixelColor(x,y).alpha() > 0]
        self.assertTrue(pixels)
        self.assertLess(max(x for x,y in pixels)-min(x for x,y in pixels), 80)
        self.assertLess(max(y for x,y in pixels)-min(y for x,y in pixels), 95)



if __name__ == "__main__":
    unittest.main()
