import numpy as np
import pytest
from numpy.testing import assert_almost_equal, assert_equal

from taser.cameras import PinholeCamera, AtanCamera

IMAGE_ROWS = 1080
IMAGE_COLS = 1920
CAMERA_READOUT = 0.026

ATAN_K = np.array([[853.12703455, 0., 988.06311256],
                   [0., 873.54956631, 525.71056312],
                   [0., 0., 1.]])
ATAN_WC = np.array([0.0029110778971412417, 0.0004189670467132041])#.reshape(2,1)
ATAN_GAMMA = 0.8894355177968156                   

@pytest.fixture
def pinhole_camera():
    K = np.eye(3)
    return PinholeCamera(IMAGE_ROWS, IMAGE_COLS, CAMERA_READOUT, K)


@pytest.fixture
def atan_camera():
    return AtanCamera(IMAGE_ROWS, IMAGE_COLS, CAMERA_READOUT,
                      ATAN_K, ATAN_WC, ATAN_GAMMA)


camera_classes = {
    PinholeCamera: pinhole_camera,
    AtanCamera: atan_camera,
}


@pytest.fixture(params=camera_classes)
def camera(request):
    cls = request.param
    try:
        return camera_classes[cls]()
    except KeyError:
        raise NotImplementedError(f"Fixture for {cls} not implemented")


def test_basic(camera):
    assert camera.readout == CAMERA_READOUT
    assert camera.rows == IMAGE_ROWS
    assert camera.cols == IMAGE_COLS

    # Change and test again
    camera.readout = 0.02
    assert camera.readout == 0.02

    camera.rows = 720
    assert camera.rows == 720

    camera.cols = 1280
    assert camera.cols == 1280


def test_project_unproject(camera):
    u = np.random.uniform(0, IMAGE_COLS-1)
    v = np.random.uniform(0, IMAGE_ROWS-1)
    y = np.array([u, v])
    X = camera.unproject(y) * np.random.uniform(0.01, 10)
    yhat = camera.project(X)

    assert_almost_equal(yhat, y)


def test_pinhole(pinhole_camera):
    camera = pinhole_camera
    K = np.random.uniform(0, 20, size=(3,3))
    camera.camera_matrix = K
    assert np.allclose(camera.camera_matrix, K)


def test_atan(atan_camera):
    camera = atan_camera

    K = np.random.uniform(0, 20, size=(3,3))
    camera.camera_matrix = K
    assert np.allclose(camera.camera_matrix, K)

    wc = np.random.uniform(-1, 1, size=2)
    camera.wc = wc
    assert np.allclose(camera.wc, wc)

    gamma = np.random.uniform(0, 1)
    camera.gamma = gamma
    assert camera.gamma == gamma
    
# Creating the camera should not depend on which constructor is used!
def test_atan_create_unproject():
    # Using full constructor
    cam1 = AtanCamera(IMAGE_ROWS, IMAGE_COLS, CAMERA_READOUT,
                      ATAN_K, ATAN_WC, ATAN_GAMMA)

    test_project_unproject(cam1)

    # Using common constructor and setting attributes manually
    cam2 = AtanCamera(IMAGE_ROWS, IMAGE_COLS, CAMERA_READOUT)
    cam2.camera_matrix = ATAN_K
    cam2.wc = ATAN_WC
    cam2.gamma = ATAN_GAMMA
    assert_equal(cam2.camera_matrix, cam1.camera_matrix)
    assert_equal(cam2.wc, cam1.wc)
    assert cam2.gamma == cam1.gamma
    test_project_unproject(cam2)