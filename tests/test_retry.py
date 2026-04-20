import pytest
from unittest.mock import MagicMock, patch
from math_mind.utils.retry import with_retry
from math_mind.engines.exceptions import RateLimitExceededError

@with_retry(max_retries=5, base_delay=0.01)
def fail_twice_then_return_sum():
    global call_count
    call_count += 1
    if call_count < 3:
        raise RateLimitExceededError("Temporary failure")
    return call_count

def test_retry_logic_simple():
    # Arrange
    global call_count
    call_count = 0 # Reset state
    # Act
    result = fail_twice_then_return_sum()
    # Assert
    assert result == 3
    assert call_count == 3

@with_retry(max_retries=3, base_delay=0.01)
def always_fail():
    global call_count
    call_count += 1
    raise RateLimitExceededError("Temporary failure")

def test_retry_logic_exceeds_max_retries():
    # Arrange
    global call_count
    call_count = 0 # Reset state
    # Act
    with pytest.raises(RateLimitExceededError):
        always_fail()
    # Assert
    assert call_count == 4
