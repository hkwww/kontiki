import pytest
import numpy as np
from numpy.testing import assert_equal

from taser.sfm import Landmark, Observation, View

def test_new_view():
    n = 34
    t0 = 4.67
    v = View(n, t0)
    assert v.frame_nr == n
    assert v.t0 == t0
    assert len(v) == 0
    assert len(v.observations) == 0

def test_view_add_observations():
    lm1 = Landmark()
    lm2 = Landmark()
    v = View(0, 0.0)

    p1 = np.array([100, 200])
    v.create_observation(lm1, *p1)
    assert len(v) == 1
    assert len(lm1.observations) == 1
    assert lm1.observations[0].view is v
    assert_equal(lm1.observations[0].uv, p1)
    assert len(lm2.observations) == 0

    p2 = np.array([300, 499])
    v.create_observation(lm2, *p2)
    assert len(v) == 2
    assert len(lm2.observations) == 1

def test_remove_observations():
    lm = Landmark()
    v1 = View(0, 0.0)
    v2 = View(1, 1.0)

    obs1 = v1.create_observation(lm, 1, 2)
    _ = v2.create_observation(lm, 3, 4)
    assert len(v1) == 1
    assert len(v2) == 1
    assert len(lm.observations) == 2

    v1.remove_observation(obs1)
    assert len(v1) == 0
    assert len(v2) == 1
    assert len(lm.observations) == 1

def test_remove_nonowned():
    lm = Landmark()
    v = View(0, 0.0)
    v_other = View(1, 1.0)
    _ = v.create_observation(lm, 1, 2)
    obs_other = v_other.create_observation(lm, 3, 4)
    with pytest.raises(RuntimeError):
        v.remove_observation(obs_other)

def test_deleted_view_cleanup():
    v = View(0, 0.0)
    N = 100
    landmarks = [Landmark() for _ in range(N)]
    for lm in landmarks:
        v.create_observation(lm, 1, 1)
        assert len(lm.observations) == 1

    del v
    for lm in landmarks:
        assert len(lm.observations) == 0


def test_new_landmark():
    lm = Landmark()
    assert len(lm.observations) == 0
    with pytest.raises(RuntimeError):
        ref = lm.reference # No reference set


def test_landmark_ids_unique():
    N = 1000
    bunch_of_landmarks = [Landmark() for _ in range(N)]
    lm_ids = set(lm.id for lm in bunch_of_landmarks)
    assert len(lm_ids) == N


def test_landmark_reference_not_owned():
    v = View(0, 0.0)
    lm = Landmark()
    obs_owned = v.create_observation(lm, 1, 2)
    obs_not_owned = v.create_observation(Landmark(), 6, 7)

    lm.reference = obs_owned # OK

    assert lm.reference is obs_owned

    with pytest.raises(RuntimeError):
        lm.reference = obs_not_owned # Error