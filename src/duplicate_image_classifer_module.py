from typing import ClassVar, List, Mapping, Optional, Sequence, Union

import numpy as np
from PIL import Image

from viam.components.camera import Camera
from viam.media.video import CameraMimeType, ViamImage
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import PointCloudObject, ResourceName
from viam.proto.service.vision import Classification, Detection
from viam.resource.base import ResourceBase
from viam.resource.easy_resource import EasyResource
from viam.resource.types import Model, ModelFamily
from viam.services.vision import Vision, CaptureAllResult
from viam.utils import ValueTypes
from viam.logging import getLogger

from src.utils import decode_image, create_empty_rgb_image


LOGGER = getLogger("DuplicateImageClassifierLogger")

class DuplicateImageClassifier(Vision, EasyResource):
    """
    DuplicateImageClassifer implements a vision service that only supports classification.
    
    It detects whether the camera's view has changed significantly since the last frame. 
    This helps to avoid uploading too many nearly identical photos. 
    This is done by doing a pixel-wise diff of two images, by checking how different, 
    on average, two numpy array representations of the images are.

    It inherits from the built-in resource subtype Vision and conforms to the
    ``Reconfigurable`` protocol, which signifies that this component can be
    reconfigured. Additionally, it specifies a constructor function
    ``BlurryClassifier.new`` which confirms to the
    ``resource.types.ResourceCreator`` type required for all models.
    """

    MODEL: ClassVar[Model] = Model(
        ModelFamily("viam", "duplicate-image-classifier"), "duplicate-image-classifier"
    )

    def __init__(self, name: str):
        super().__init__(name=name)
        self.camera = None
        self.camera_name = None
        self.current_image = create_empty_rgb_image(480, 640)
        self.average_pixel_difference_threshold = 20.0

    @classmethod
    def new(
        cls,
        config: ComponentConfig,
        dependencies: Mapping[ResourceName, ResourceBase]
    ):
        """
        This method creates a new instance of this Vision service.  The default
        implementation sets the name from the `config` parameter and then calls
        `reconfigure`.

        Args:
            config (ComponentConfig): The configuration for this resource
            dependencies (Mapping[ResourceName, ResourceBase]): The
                dependencies (both implicit and explicit)

        Returns:
            Self: The resource
        """
        service = cls(config.name)
        service.reconfigure(config, dependencies)
        return service

    @classmethod
    def validate_config(cls, config: ComponentConfig) -> Sequence[str]:
        """
        This method allows you to validate the configuration object received
        from the machine, as well as to return any implicit dependencies based
        on that `config`.

        Args:
            config (ComponentConfig): The configuration for this resource

        Returns:
            Sequence[str]: A list of implicit dependencies
        """
        camera_name = config.attributes.fields["camera_name"].string_value
        if camera_name == "":
            raise ValueError(
                "A camera name is required for face_identification vision service module."
            )
        return [camera_name]

    def reconfigure(
        self,
        config: ComponentConfig,
        dependencies: Mapping[ResourceName, ResourceBase],
    ) -> None:
        """
        This method allows you to dynamically update your service when it
        receives a new `config` object.

        Args:
            config (ComponentConfig): The new configuration
            dependencies (Mapping[ResourceName, ResourceBase]): Any
                dependencies (both implicit and explicit)
        """
        self.camera_name = config.attributes.fields["camera_name"].string_value
        self.camera = dependencies[Camera.get_resource_name(self.camera_name)]
        if "average_pixel_difference_threshold" in config.attributes.fields:
            self.average_pixel_difference_threshold = config.attributes.fields[
                "average_pixel_difference_threshold"].number_value

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    async def capture_all_from_camera(
        self,
        camera_name: str,
        return_image: bool = False,
        return_classifications: bool = False,
        return_detections: bool = False,
        return_object_point_clouds: bool = False,
        *,
        extra: Optional[Mapping[str, ValueTypes]] = None,
        timeout: Optional[float] = None,
    ) -> CaptureAllResult:
        """
        This function captures an image from the camera and optionally returns classifications.

        Args:
            camera_name (str): The name of the camera to capture from.
            return_image (bool): Whether to return the captured image.
            return_classifications (bool): Whether to return classifications of the image.
            return_detections (bool): Whether to return detections from the image.
            return_object_point_clouds (bool): Whether to return object point clouds from the image.
            extra (Optional[Mapping[str, ValueTypes]]): Additional parameters for the function.
            timeout (Optional[float]): Timeout for the function call.
        Returns:
            CaptureAllResult: A result object containing the captured image and classifications.
        """
        if camera_name not in (self.camera_name, ""):
            raise ValueError(
                f"Camera name {camera_name} does not match the camera name " +
                f"{self.camera_name} in the config."
            )
        # Added check for camera dependency, otherwise gets error on calling get_image function
        if self.camera is None or not isinstance(self.camera, Camera):
            raise RuntimeError("Camera dependency is not properly configured or is missing.")
        image = await self.camera.get_image(mime_type=CameraMimeType.JPEG)
        classifications = None
        if return_classifications:
            classifications = await self.get_classifications(
                image, 1, extra=extra, timeout=timeout
            )

        return CaptureAllResult(image=image, classifications=classifications)

    def set_current_image(self, image: Union[Image.Image, ViamImage, np.ndarray]):
        """
        This function sets the current image to the provided parameter image after decoding it.
        (Mainly used for testing purposes)
        Args:
            image (Union[Image.Image, ViamImage, np.ndarray]): The current image to set.
        Returns:
            None
        """
        self.current_image = decode_image(image)

    # I assume the following three functions are here to conform to the Vision superclass?
    ########################################################
    async def get_detections_from_camera(
        self,
        camera_name: str,
        *,
        extra: Optional[Mapping[str, ValueTypes]] = None,
        timeout: Optional[float] = None,
    ) -> List[Detection]:
        raise NotImplementedError()

    async def get_detections(
        self,
        image: ViamImage,
        *,
        extra: Optional[Mapping[str, ValueTypes]] = None,
        timeout: Optional[float] = None,
    ) -> List[Detection]:
        raise NotImplementedError()

    async def get_object_point_clouds(
        self,
        camera_name: str,
        *,
        extra: Optional[Mapping[str, ValueTypes]] = None,
        timeout: Optional[float] = None,
    ) -> List[PointCloudObject]:
        raise NotImplementedError()
    ########################################################

    async def get_classifications_from_camera(
        self,
        camera_name: str,
        count: int,
        *,
        extra: Optional[Mapping[str, ValueTypes]] = None,
        timeout: Optional[float] = None,
    ) -> List[Classification]:
        """
        This function captures an image from the camera and returns classifications.

        Args:
            camera_name (str): The name of the camera to capture from.
            count (int): The number of classifications to return.
            extra (Optional[Mapping[str, ValueTypes]]): Additional parameters for the function.
            timeout (Optional[float]): Timeout for the function call.
        Returns:
            List[Classification]: A list of classifications for the captured image.
        """
        if camera_name not in (self.camera_name, ""):
            raise ValueError(
                f"Camera name {camera_name} does not match the camera name " +
                f"{self.camera_name} in the config."
            )
        if self.camera is None or not isinstance(self.camera, Camera):
            raise RuntimeError("Camera dependency is not properly configured or is missing.")
        im = await self.camera.get_image(mime_type=CameraMimeType.JPEG)
        return await self.get_classifications(im, 1, extra=extra, timeout=timeout)

    # True difference from blurry-classifier lies in this function
    async def get_classifications(
        self,
        image: ViamImage,
        count: int,
        *,
        extra: Optional[Mapping[str, ValueTypes]] = None,
        timeout: Optional[float] = None,
    ) -> List[Classification]:
        """
        This function compares the current image with the new image 
        and returns a classification based on the pixel difference.

        Args:
            image (ViamImage): The new image to compare with the current image.
            count (int): The number of images to classify (should be 1 for this module use case).
            extra (Optional[Mapping[str, ValueTypes]]): Additional parameters for the function.
            timeout (Optional[float]): Timeout for the function call.
        Returns:
            List[Classification]: Contains a single classification indicating
            if the image is "different" or not.
        """
        img = decode_image(image)
        pixel_by_pixel_diff = np.abs(img.astype(np.int16) - self.current_image.astype(np.int16))
        average_pixel_difference = np.mean(pixel_by_pixel_diff)
        LOGGER.info("Average pixel difference is: %f. Threshold is %f.",
                    average_pixel_difference, self.average_pixel_difference_threshold)
        if self.average_pixel_difference_threshold < average_pixel_difference:
            self.current_image = img
            return [Classification(class_name="different", confidence=1.0)]

        return []

    async def get_properties(
        self,
        *,
        extra: Optional[Mapping[str, ValueTypes]] = None,
        timeout: Optional[float] = None,
    ) -> Vision.Properties:
        """
        This function returns the properties of the vision service.
        """
        return Vision.Properties(
            classifications_supported=True,
            detections_supported=False,
            object_point_clouds_supported=False,
        )
