import os
import subprocess
import sys
from enum import IntEnum
from pathlib import Path
from typing import Dict, Union

import docker


class Versions(IntEnum):
    YOLO5 = 5
    YOLO7 = 7
    YOLO8 = 8


# [(CONTAINER_VERSION, TENSORRT_VERSION, SUPPORTS_DYNAMIC_SHAPE?)]
TRT_CONTAINERS = {
    "21.09": {"trt": "8003", "dynamic_support": False},
    "22.12": {"trt": "842", "dynamic_support": True},
}
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cwd = os.getcwd()


def trt_supports_dynamic(container_version: str) -> bool:
    return TRT_CONTAINERS[container_version]["dynamic_support"]


def validate_config(config: Dict[str, Union[int, str]], container_version: str):
    """
    Validates the configuration dictionary for the object detector.

    Args:
        config (Dict[str, Union[int, str]]): The configuration dictionary.
        container_version (str): The version of the container.

    Returns:
        Dict[str, Union[int, str]]: The validated configuration dictionary.
    """
    if trt_supports_dynamic(container_version):
        config["half"] = False
        config["dynamic"] = True
    else:
        config["half"] = True
        config["dynamic"] = False
        config["min_bsz"] = 1
    return config


def parse_config(config):
    """
    Parses the given configuration dictionary and modifies it based on the specified model version.

    Args:
        config (dict): The configuration dictionary.

    Returns:
        dict: The modified configuration dictionary.
    """
    version = config["model_release"]
    assert isinstance(
        version, int
    ), "Version must be an int, specifying model version (5,7,8)"
    if Versions(version) == Versions.YOLO5:
        config["include"] = "onnx"
    elif Versions(version) == Versions.YOLO8:
        config["format"] = "onnx"
    else:
        config = config

    return config


def pt2onnx(config: Dict[str, Union[int, str]], version: int):
    """
    Converts a PyTorch model to ONNX format based on the specified configuration and version.

    Args:
        config (Dict[str, Union[int, str]]): The configuration parameters for the conversion.
        version (int): The version of the model to convert.

    Returns:
        The converted ONNX model.

    Raises:
        ValueError: If an unsupported version is provided.
    """
    if Versions(version) == Versions.YOLO5:
        return export_yolov5(config)
    elif Versions(version) == Versions.YOLO8:
        return export_yolov8(config)


def export_yolov5(config: Dict[str, Union[int, str]]) -> str:
    """
    Export YOLOv5 model.

    Args:
        config (Dict[str, Union[int, str]]): Configuration dictionary containing the following keys:
            - "weights" (str): Path to the model weights file.
            - "half" (int): Whether to use half-precision floating-point format (0 for full precision, 1 for half precision).
            - "device" (str): Device to use for model export (e.g., "cpu", "cuda").
            - "imgsz" (int): Input image size.
            - "nms" (float): Non-maximum suppression threshold.
            - "opset" (int): ONNX operator set version.
            - "simplify" (bool): Whether to simplify the exported ONNX model.

    Returns:
        str: Filename of the exported ONNX model.
    """
    sys.path.insert(0, os.path.join(base_dir, "object_detectors", "yolov5"))
    import export

    [filename] = export.run(
        weights=config["weights"],
        half=config["half"],
        include=["onnx"],
        device=config["device"],
        imgsz=config["imgsz"],
        nms=config["nms"],
        opset=config["opset"],
        simplify=config["simplify"],
        dynamic=config["dynamic"],
    )
    return filename


def export_yolov8(config: Dict[str, Union[int, str]]) -> str:
    """
    Export YOLOv8 model to ONNX format.

    Args:
        config (Dict[str, Union[int, str]]): Configuration dictionary containing the following keys:
            - "weights" (str): Path to the model weights file.
            - "half" (int): Whether to use half-precision floating-point format (0 for False, 1 for True).
            - "device" (str): Device to use for exporting the model (e.g., "cuda", "cpu").
            - "imgsz" (int): Input image size.
            - "nms" (float): Non-maximum suppression threshold.
            - "opset" (int): ONNX operator set version.
            - "simplify" (bool): Whether to simplify the exported ONNX model.

    Returns:
        str: Filename of the exported ONNX model.

    """
    sys.path.insert(0, os.path.join(base_dir, "object_detectors", "yolov8"))
    from ultralytics import YOLO

    model = YOLO(config["weights"])
    config.pop("weights")
    filename = model.export(
        half=config["half"],
        format="onnx",
        device=config["device"],
        imgsz=config["imgsz"],
        nms=config["nms"],
        opset=config["opset"],
        simplify=config["simplify"],
        dynamic=config["dynamic"],
    )
    return filename


def start_trt_container(container_version: str):
    """
    Starts a TensorRT container with the specified version.

    Args:
        container_version (str): The version of the TensorRT container to start.

    Returns:
        docker.models.containers.Container: The started container.
    """
    gpu_devices = ["0"]
    gpu_config = {
        "device_requests": [{"count": len(gpu_devices), "capabilities": [["gpu"]]}],
        "devices": [f"/dev/nvidia{n}" for n in gpu_devices],
    }

    client = docker.from_env()
    # Running the container
    container = client.containers.run(
        f"nvcr.io/nvidia/tensorrt:{container_version}-py3",
        command='sh -c "while true; do sleep 3600; done"',
        detach=True,
        stdout=True,
        stderr=True,
        **gpu_config,
    )

    return container


def build_engine(onnx_path: str, container, metadata, config):
    """
    Builds an engine for a deep learning model using TensorRT.

    Args:
        onnx_path (str): The path to the ONNX file of the model.
        container: The Docker container to use for building the engine.
        metadata (dict): Metadata containing information about the model.

    Returns:
        str: The path to the directory where the built engine is saved.
    """
    filename = Path(onnx_path).stem
    try:
        command = f"docker cp {onnx_path} {container.short_id}:/workspace/"
        subprocess.run(command, shell=True, check=True)
        print("File copied successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error copying file: {e}")

    try:
        if config["dynamic"]:
            # TODO: make batchsize dynamic, passed from config downstream
            input_name = config["inputs"][0]["name"]
            imgsz_str = "x".join(map(str, config["imgsz"]))
            min_bsz = config["min_bsz"]
            max_bsz = config["max_bsz"]

            min_shapes = f"{input_name}:{min_bsz}x3x{imgsz_str}"
            opt_shapes = f"{input_name}:{max_bsz // 2}x3x{imgsz_str}"
            max_shapes = f"{input_name}:{max_bsz }x3x{imgsz_str}"
            command = f"./tensorrt/bin/trtexec --onnx={filename}.onnx --saveEngine=model.plan --minShapes={min_shapes} --optShapes={opt_shapes} maxShapes={max_shapes} --{metadata['dtype'].lower()}"
        else:
            # Not Dynamic, keep 1 batch size
            command = f"./tensorrt/bin/trtexec --onnx={filename}.onnx --saveEngine=model.plan --{metadata['dtype'].lower()}"
        container.exec_run(command, stdout=True, stderr=True)

        model_template = """
            {PROJECT}_MODELS_{ML_TASK}_{MODEL_NAME}_{TRT_VERSION}_{GPU}_{DATA_TYPE}_{CC}_v{VERSION}
        """
        model_folder = model_template.format(
            PROJECT=metadata["project"],
            ML_TASK=metadata["task"],
            MODEL_NAME=metadata["model_name"],
            TRT_VERSION=metadata["trt_version"],
            GPU=metadata["gpu"],
            DATA_TYPE=metadata["dtype"],
            CC=metadata["cc"],
            VERSION="1.0",
        ).strip()

        model_dir_path = os.path.join(cwd, "model_repository", model_folder, "1")
        os.makedirs(model_dir_path, exist_ok=True)
        command = (
            f"docker cp {container.short_id}:/workspace/model.plan {model_dir_path}"
        )
        subprocess.run(command, shell=True, check=True)
        print("File copied successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error copying file: {e}")

    return model_dir_path
