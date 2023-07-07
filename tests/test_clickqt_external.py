from clickqt.core.__main__ import get_command_from_entrypoint, get_command_from_path
from click import Command
import pytest

def test_clickqt_external():
  # test with endpoint
  with pytest.raises(ImportError):
    get_command_from_entrypoint("example")
  with pytest.raises(TypeError):
    get_command_from_entrypoint("example_cli")
  assert isinstance(get_command_from_entrypoint("example_cli"), Command)

  # test with file
  with pytest.raises(ImportError):
    get_command_from_path("example/example/afwizard.py", "ma")
  with pytest.raises(FileNotFoundError):
    get_command_from_path("example/example/--_--_-_.py", "main")
  with pytest.raises(TypeError):
    get_command_from_path("example/example/afwizard.py", "validate_spatial_reference")
  assert isinstance(get_command_from_path("example/example/afwizard.py", "main"), Command)
