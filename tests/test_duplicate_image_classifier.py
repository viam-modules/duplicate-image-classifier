from typing import List, Dict
from unittest.mock import patch
from src.duplicate_image_classifer_module import DuplicateImageClassifier
from tests.fake_camera import FakeCamera, read_image
from PIL import Image

from viam.proto.app.robot import ComponentConfig, ServiceConfig
from viam.utils import dict_to_struct

import pytest
import os

CAMERA_NAME = "fake_camera"

config = ComponentConfig(
    attributes=dict_to_struct(
        {
            "camera_name": CAMERA_NAME,
        }
    ))

def get_vision_service(similar: bool = True) -> DuplicateImageClassifier:
    service = DuplicateImageClassifier("test")
    cam = FakeCamera(CAMERA_NAME, similar)
    camera_name = cam.get_resource_name(CAMERA_NAME)
    service.validate_config(config)
    service.reconfigure(config, dependencies={camera_name: cam}) # type: ignore
    service.set_current_image(read_image("img"))  # Set a default image for testing
    return service
 
class TestDuplicateClassifier:
    def test_empty(self):
        duplicate_classifier = DuplicateImageClassifier("test_duplicate_classifier")
        with pytest.raises(ValueError, match="A camera name is required for face_identification vision service module."):
            duplicate_classifier.validate_config(ComponentConfig(attributes=dict_to_struct({})))

    @pytest.mark.asyncio
    @patch('viam.components.camera.Camera.get_resource_name', return_value=CAMERA_NAME)
    async def test_reconfigure(self, fake_cam):
        duplicate_classifier = get_vision_service()

        assert duplicate_classifier.camera_name == CAMERA_NAME
        assert duplicate_classifier.camera is not None

    @pytest.mark.asyncio
    @patch('viam.components.camera.Camera.get_resource_name', return_value=CAMERA_NAME)
    async def test_get_classifications(self, fake_cam):
        # Test with a different image
        duplicate_classifier = get_vision_service(True)
        result = await duplicate_classifier.get_classifications(
            image = await duplicate_classifier.camera.get_image(), # type: ignore
            count=1,
        )
        assert result[0].class_name == "different"
        assert result[0].confidence == 1.0

        # Test with a similar image
        duplicate_classifier = get_vision_service(False)
        result = await duplicate_classifier.get_classifications(
            image = await duplicate_classifier.camera.get_image(), # type: ignore
            count=1,
        )
        assert result == []

    @pytest.mark.asyncio
    @patch('viam.components.camera.Camera.get_resource_name', return_value=CAMERA_NAME)
    async def test_capture_all_from_camera(self, fake_cam):
        # Test with a different image
        duplicate_classifier = get_vision_service(True)
        result = await duplicate_classifier.capture_all_from_camera(
            camera_name=CAMERA_NAME,
            return_image=True,
            return_classifications=True,
        )

        assert result.image is not None
        assert result.classifications[0].class_name == "different" # type: ignore
        assert result.classifications[0].confidence == 1.0 # type: ignore

    @pytest.mark.asyncio
    @patch('viam.components.camera.Camera.get_resource_name', return_value=CAMERA_NAME)
    async def test_with_default_camera(self, fake_cam):
        duplicate_classifier = get_vision_service(True)

        # Test funtions with empty camera name
        result = await duplicate_classifier.capture_all_from_camera(
            camera_name="",
            return_image=True,
            return_classifications=True,
        )

        assert result.image is not None
        assert result.classifications[0].class_name == "different" # type: ignore
        assert result.classifications[0].confidence == 1.0 # type: ignore

        duplicate_classifier = get_vision_service(True)
        result = await duplicate_classifier.get_classifications_from_camera(
            camera_name="",
            count=1,
        )

        assert result[0].class_name == "different"
        assert result[0].confidence == 1.0

        # Test with wrong camera name
        with pytest.raises(ValueError, match="Camera name wrong_camera does not match the camera name fake_camera in the config."):
            await duplicate_classifier.capture_all_from_camera(
                camera_name="wrong_camera",
                return_image=True,
                return_classifications=True,
            )

        with pytest.raises(ValueError, match="Camera name wrong_camera does not match the camera name fake_camera in the config."):
            await duplicate_classifier.get_classifications_from_camera(
                camera_name="wrong_camera",
                count=1,
            )