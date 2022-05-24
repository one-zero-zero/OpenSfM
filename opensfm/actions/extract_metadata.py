from cmath import log
import copy
import logging
from functools import partial
from typing import Any, Dict
from opensfm import exif
from opensfm.dataset_base import DataSetBase


logger: logging.Logger = logging.getLogger(__name__)
logging.getLogger("exifread").setLevel(logging.WARNING)


def run_dataset(data: DataSetBase) -> None:
    """Extract metadata from images' EXIF tag."""

    exif_overrides = {}
    if data.exif_overrides_exists():
        exif_overrides = data.load_exif_overrides()

    camera_models = {}
    for image in data.images():
        if data.exif_exists(image):
            logging.info("Loading existing EXIF for {}".format(image))
            d = data.load_exif(image)
        else:
            logging.info("Extracting EXIF for {}".format(image))
            d = _extract_exif(image, data)

            if image in exif_overrides:
                d.update(exif_overrides[image])

            data.save_exif(image, d)

        if d["camera"] not in camera_models:
            camera = exif.camera_from_exif_metadata(d, data)
            camera_models[d["camera"]] = camera

    # Override any camera specified in the camera models overrides file.
    if data.camera_models_overrides_exists():
        overrides = data.load_camera_models_overrides()
        if "all" in overrides:
            for key in camera_models:
                camera_models[key] = copy.copy(overrides["all"])
                camera_models[key].id = key
        else:
            for key, value in overrides.items():
                camera_models[key] = value
    data.save_camera_models(camera_models)

    from opensfm.undistort import perspective_camera_from_brown
    from opensfm.undistort import undistort_image_from_camera
    from opensfm.io import imwrite
    for image in data.images():
        im_exif = data.load_exif(image)
        im_camera = camera_models[ im_exif["camera"] ]
        if im_camera.projection_type == "brown":
            logging.info(f"Undistorting image {image}")
            logging.info( f"{image} : projection_type: {im_camera.projection_type} : focal {im_camera.focal}" )
            img = data.load_image(image)
            u_cam = perspective_camera_from_brown(im_camera)
            logging.info( f"{image} : projection_type: {u_cam.projection_type}: focal {u_cam.focal}" )
            u_img = undistort_image_from_camera(im_camera, u_cam, img)
            fname = './reports/undistorted/' + image
            logging.info(f"Undistorting image {image} - saving")
            imwrite(fname, u_img)
            fname = './reports/undistorted/raw-' + image
            imwrite(fname, img)

def _extract_exif(image: str, data: DataSetBase) -> Dict[str, Any]:
    with data.open_image_file(image) as fp:
        d = exif.extract_exif_from_file(
            fp,
            partial(data.image_size, image),
            data.config["use_exif_size"],
            name=image,
        )

    if data.config["unknown_camera_models_are_different"] and (
        not d["model"] or d["model"] == "unknown"
    ):
        d["model"] = f"unknown_{image}"

    if data.config.get("default_projection_type"):
        d["projection_type"] = data.config.get("default_projection_type")

    d["camera"] = exif.camera_id(d)

    return d
