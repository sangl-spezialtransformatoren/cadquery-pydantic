import pytest
from pydantic import TypeAdapter


@pytest.fixture
def check_serialization():
    def _check_serialization(obj, obj_type, equality_check):
        """
        Test both Python and JSON serialization/deserialization.

        Args:
            obj: The object to test
            obj_type: The type of the object (for TypeAdapter)
            equality_check: Function(obj1, obj2) -> bool that checks if two objects are equal
        """
        adapter = TypeAdapter(obj_type)

        # Test Python serialization
        serialized_py = adapter.dump_python(obj)
        deserialized_py = adapter.validate_python(serialized_py)
        assert equality_check(obj, deserialized_py)

        # Test JSON serialization
        serialized_json = adapter.dump_json(obj)
        deserialized_json = adapter.validate_json(serialized_json)
        assert equality_check(obj, deserialized_json)

    return _check_serialization
