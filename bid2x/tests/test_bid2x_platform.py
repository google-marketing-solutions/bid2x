"""Tests for the Platform abstract base class."""

from typing import Any

import pandas
import pytest

from bid2x_platform import Platform


class _ConcretePlatform(Platform):
  """Minimal concrete implementation for testing."""

  def __str__(self) -> str:
    return 'test-platform'

  def process_script(self, service: Any, *args: Any, **kwargs: Any) -> bool:
    return True

  def top_level_copy(self, source: Any) -> None:
    pass


def test_platform_cannot_be_instantiated() -> None:
  with pytest.raises(TypeError):
    Platform()  # type: ignore[abstract]


def test_print_dataframe_skips_output_when_debug_false(
    capsys: pytest.CaptureFixture[str],
) -> None:
  platform = _ConcretePlatform()
  platform.print_dataframe(False, pandas.DataFrame({'a': [1]}))
  assert capsys.readouterr().out == ''


def test_print_dataframe_writes_output_when_debug_true(
    capsys: pytest.CaptureFixture[str],
) -> None:
  platform = _ConcretePlatform()
  platform.print_dataframe(True, pandas.DataFrame({'a': [1], 'b': [2]}))
  output = capsys.readouterr().out
  assert 'a' in output
  assert '1' in output
