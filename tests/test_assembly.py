from cadquery import Assembly, Workplane, Location, Color
from cadquery_pydantic import patch_cadquery

patch_cadquery()


def test_basic_assembly(check_serialization):
    # Create a simple assembly with two cubes
    root = Workplane().box(10, 10, 10)
    child = Workplane().box(5, 5, 5)

    # Create assembly
    assembly = Assembly()
    assembly.add(root, name="root", color=Color(1, 0, 0))
    assembly.add(child, name="child", color=Color(0, 1, 0))

    # Add constraints to fix both parts
    assembly.constrain("root", "Fixed", None)
    assembly.constrain("child", "Fixed", None)

    def check_equality(a1: Assembly, a2: Assembly) -> bool:
        # Check that the named objects are present
        assert "root" in a2.objects
        assert "child" in a2.objects

        # Check that the colors are preserved
        assert a2.objects["root"].color.toTuple() == (1, 0, 0, 1)
        assert a2.objects["child"].color.toTuple() == (0, 1, 0, 1)

        # Check constraints
        assert len(a2.constraints) == 2
        return True

    check_serialization(assembly, Assembly, check_equality)


def test_color_serialization(check_serialization):
    # Create assembly with colored parts
    assembly = Assembly()
    box = Workplane().box(1, 1, 1)

    # Test various color combinations
    colors = [
        Color(1, 0, 0),  # Red
        Color(0, 1, 0),  # Green
        Color(0, 0, 1),  # Blue
        Color(1, 1, 1),  # White
        Color(0, 0, 0, 0.5),  # Transparent black
    ]

    for i, color in enumerate(colors):
        assembly.add(box, name=f"part_{i}", color=color)

    def check_equality(a1: Assembly, a2: Assembly) -> bool:
        # Check each part has the correct color
        for i, color in enumerate(colors):
            part_name = f"part_{i}"
            assert part_name in a2.objects
            assert a2.objects[part_name].color is not None
            assert a2.objects[part_name].color.toTuple() == color.toTuple()
        return True

    check_serialization(assembly, Assembly, check_equality)


def test_assembly_relationships(check_serialization):
    # Create a more complex assembly with nested relationships
    root_assy = Assembly()

    # Create parts
    root = Workplane().box(10, 10, 10)
    child1 = Workplane().box(5, 5, 5)
    child2 = Workplane().box(3, 3, 3)

    # Add with relationships
    root_assy.add(root, name="root")

    # Create a subassembly for child1
    child1_assy = Assembly()
    child1_assy.add(child1, name="child1")
    child1_assy.add(child2, name="child2", loc=Location((2, 0, 0)))

    # Add the subassembly to the root
    root_assy.add(child1_assy, name="child1_assy", loc=Location((5, 0, 0)))

    def check_equality(a1: Assembly, a2: Assembly) -> bool:
        # Check root assembly structure
        assert "root" in a2.objects
        assert "child1_assy" in a2.objects
        assert a2.parent is None

        # Check subassembly structure
        child1_assy_obj = a2.objects["child1_assy"]
        assert child1_assy_obj.parent == a2
        assert "child1" in child1_assy_obj.objects
        assert "child2" in child1_assy_obj.objects

        # Check locations
        assert child1_assy_obj.loc.toTuple()[0][0] == 5  # x = 5
        child2_obj = child1_assy_obj.objects["child2"]
        assert child2_obj.loc.toTuple()[0][0] == 2  # x = 2
        return True

    check_serialization(root_assy, Assembly, check_equality)


def test_constraints(check_serialization):
    assembly = Assembly()

    # Create parts
    box1 = Workplane().box(2, 2, 2)
    box2 = Workplane().box(1, 1, 1)

    # Add parts
    assembly.add(box1, name="box1")
    assembly.add(box2, name="box2", loc=Location((3, 0, 0)))

    # Add different types of constraints
    assembly.constrain("box1", "Fixed", None)
    assembly.constrain(
        "box1@faces@>Z",  # Specify the face to constrain
        "box2@faces@>Z",  # Specify the face to constrain
        "Axis",  # The constraint type
    )

    def check_equality(a1: Assembly, a2: Assembly) -> bool:
        # Check parts exist
        assert "box1" in a2.objects
        assert "box2" in a2.objects

        # Check constraints
        assert len(a2.constraints) == 2
        assert a2.constraints[0].kind == "Fixed"
        assert a2.constraints[1].kind == "Axis"
        assert a2.constraints[0].objects == ("box1",)
        assert len(a2.constraints[1].objects) == 2
        return True

    check_serialization(assembly, Assembly, check_equality)


def test_json_serialization(check_serialization):
    # Test that we can serialize to and from JSON
    assembly = Assembly()
    box = Workplane().box(1, 1, 1)
    assembly.add(box, name="box", color=Color(1, 0, 0))
    assembly.constrain("box", "Fixed", None)

    def check_equality(a1: Assembly, a2: Assembly) -> bool:
        # Check part exists with correct color
        assert "box" in a2.objects
        assert a2.objects["box"].color.toTuple() == (1, 0, 0, 1)

        # Check constraint
        assert len(a2.constraints) == 1
        assert a2.constraints[0].kind == "Fixed"
        return True

    check_serialization(assembly, Assembly, check_equality)
