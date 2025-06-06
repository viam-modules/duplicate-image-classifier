# duplicate-image-classifier

This module implements a vision service that detects duplicate images from the previous frame. It uses a mean numpy array comparison between the current frame and the previous frame to determine if they are under a certain threshold of similarity.

## API and Namespace Triplet

- API: `rdk:service:vision`
- Organization Namespace: `viam`
- Model: `viam:duplicate-classifier:duplicate-classifier`


## Attributes

The following attributes are available for this model:

| Name          | Type   | Inclusion | Description                |
|---------------|--------|-----------|----------------------------|
| `camera_name` | string  | Required  | The name of the camera configured on your robot. |
| `average_pixel_difference_threshold` | float | Optional  | The threshold _above_ which an image would be considered different. The **default** value is 5.0. |


## Configuration

Start by [configuring a camera](https://docs.viam.com/components/camera/webcam/) on your robot. Remember the name you give to the camera, it will be important later.

> [!NOTE]
> Before configuring your camera or vision service, you must [create a robot](https://docs.viam.com/manage/fleet/robots/#add-a-new-robot).

> [!NOTE]
> If you run this on a non-Debian-based flavor of Linux, you need to ensure that libGL.so.1 is installed on your system! It's probably already installed, unless you're using a headless setup. Ubuntu is Debian-based, so this note doesn't apply on Ubuntu.


Navigate to the **Config** tab of your robot’s page in [the Viam app](https://app.viam.com/). Click on the **Services** subtab and click **Create service**. Select the `vision` type, then select the `duplicate-image-classifier` model. Enter a name for your service and click **Create**.

On the new component panel, copy and paste the following attribute template into your base’s **Attributes** box.
```json
{
    "camera_name": "myCam",
    "average_pixel_difference_threshold": 5.0
}
```

## Example Configuration

```json
{
  "modules": [
    {
      "type": "registry",
      "name": "viam-duplicate-image-classifier",
      "module_id": "viam:duplicate-image-classifier",
      "version": "0.0.1"
    }
  ],
  "services": [
    {
      "name": "myDuplicateImageClassifier",
      "type": "vision",
      "namespace": "rdk",
      "model": "viam:duplicate-image-classifier:duplicate-image-classifier",
      "attributes": {
        "camera_name": "myCam",
        "average_pixel_difference_threshold": 5.0
      }
    }
  ]
}
```

# Usage

The following methods are implemented from the [Vision Service API](https://docs.viam.com/dev/reference/apis/services/vision/):

- [`CaptureAllResult()`](https://docs.viam.com/dev/reference/apis/services/vision/#captureallresult)
- [`GetClassificationsFromCamera()`](https://docs.viam.com/dev/reference/apis/services/vision/#getclassificationsfromcamera)
- [`GetClassifications()`](https://docs.viam.com/dev/reference/apis/services/vision/#getclassifications)
- [`GetProperties()`](https://docs.viam.com/dev/reference/apis/services/vision/#getproperties)

When the module returns classifications, the `class_name` will always be `"different"` and the confidence will always be 1.0 if the images are different. Nothing will be returned if the images are similar.
