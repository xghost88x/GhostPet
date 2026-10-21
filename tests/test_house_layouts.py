"""Pure layout/pathfinding tests; no display server or Qt dependency required."""
import ast
from collections import deque
from pathlib import Path
import unittest

SRC = Path(__file__).resolve().parents[1] / "house.py"


def load_layout_logic():
    source = ast.parse(SRC.read_text(encoding="utf-8"), filename=str(SRC))
    nodes = []
    for node in source.body:
        if isinstance(node, ast.FunctionDef) and node.name in {"walls", "walls_for_layout", "path_between"}:
            nodes.append(node)
        elif isinstance(node, ast.Assign):
            assigned = {v.id for target in node.targets for v in ast.walk(target) if isinstance(v, ast.Name)}
            if assigned & {"W", "H", "WALLS", "LAYOUTS"}:
                nodes.append(node)
    namespace = {"deque": deque}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SRC), "exec"), namespace)
    return namespace


class CottageLayoutsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.logic = load_layout_logic()

    def test_three_distinct_upgradable_plans(self):
        ns = self.logic
        self.assertEqual(list(ns["LAYOUTS"]), ["cottage", "open", "garden"])
        starter = ns["walls_for_layout"]("cottage")
        middle = ns["walls_for_layout"]("open")
        deluxe = ns["walls_for_layout"]("garden")
        # These are genuine room renovations, not subsets of the same
        # four-room map; new privacy nooks and greenhouse posts are relocated.
        self.assertGreater(len(starter), len(middle) + 5)
        self.assertGreater(len(middle), len(deluxe))
        self.assertGreater(len(starter.symmetric_difference(middle)), 12)
        self.assertGreater(len(middle.symmetric_difference(deluxe)), 9)
        self.assertIn((8,2), starter)
        self.assertNotIn((8,2), middle)
        self.assertIn((6,2), middle)  # compact sleeping-nook partition
        self.assertNotIn((6,2), deluxe)
        self.assertIn((12,2), deluxe) # glasshouse column
        self.assertNotIn((12,2), middle)

    def test_all_rooms_remain_reachable_in_every_plan(self):
        ns = self.logic
        for plan in ns["LAYOUTS"]:
            wall_tiles = ns["walls_for_layout"](plan)
            start = (2, 3)
            self.assertNotIn(start, wall_tiles)
            for y in range(1, ns["H"]-1):
                for x in range(1, ns["W"]-1):
                    destination = (x, y)
                    if destination in wall_tiles:
                        continue
                    with self.subTest(plan=plan, tile=destination):
                        if destination != start:
                            route = ns["path_between"](start, destination, wall_tiles=wall_tiles)
                            self.assertTrue(route, f"No path to {destination} in {plan}")
                            self.assertEqual(route[-1], destination)
                            self.assertTrue(all(step not in wall_tiles for step in route))

    def test_path_avoids_user_placed_furniture(self):
        ns = self.logic
        for plan in ns["LAYOUTS"]:
            blocked = {(3,3), (4,3), (5,3)}
            target = (6,3)
            route = ns["path_between"]((2,3), target, blocked, ns["walls_for_layout"](plan))
            self.assertTrue(route)
            self.assertTrue(all(cell not in blocked for cell in route))


if __name__ == "__main__":
    unittest.main()
