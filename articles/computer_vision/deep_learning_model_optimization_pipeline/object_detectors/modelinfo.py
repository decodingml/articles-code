import os
import re
from pathlib import Path
from typing import Dict, Union

import onnx
import torch
from helpers import TRT_CONTAINERS


def gpu_name():
    """
    Returns the name of the GPU device.

    Returns:
        str: The name of the GPU device.
    """
    gpu_name = torch.cuda.get_device_name()
    match = re.search(r"(RTX|GTX|TITAN|Quadro|T)\s?(\d+\w*|\w+)", gpu_name)
    if match:
        short_name = "".join(match.groups())
    return short_name


def gpu_cc():
    """
    Get the CUDA compute capability of the GPU.

    Returns:
        str: The CUDA compute capability in the format "CC<major_version><minor_version>".
    """
    gpu_cc = torch.cuda.get_device_capability()
    return f"CC{gpu_cc[0]}{gpu_cc[1]}"


def build_model_metadata(model_config):
    """
    Builds the metadata for a deep learning model based on the given model configuration.

    Args:
        model_config (dict): The configuration of the model.

    Returns:
        dict: The metadata of the model, including information such as client, project, task, model name,
              Triton Server version, GPU name, GPU compute capability, and data type.
    """
    container_version = model_config["tritonserver_version"]

    model_meta = {
        "project": model_config["project"].upper(),
        "task": model_config["task"].upper(),
        "model_name": (
            model_config["model_family"].split("-")[0]
            + str(model_config["model_release"])
            + model_config["model_family"].split("-")[-1]
        ).upper(),
        "trt_version": TRT_CONTAINERS[container_version]["trt"],
        "gpu": gpu_name().upper(),
        "cc": gpu_cc().upper(),
        "dtype": model_config["dtype"].upper(),
    }
    return model_meta


def test_onnx_model(filepath: str):
    """
    Test the ONNX model located at the given filepath.

    Args:
        filepath (str): The path to the ONNX model file.

    Returns:
        Union[onnx.ModelProto, bool]: The loaded ONNX model if it is valid, False otherwise.
    """
    if not os.path.isfile(filepath):
        return False

    try:
        model = onnx.load(filepath)
        onnx.checker.check_model(model)
        return model
    except Exception:
        return False


def get_tensor_info(tensor):
    """
    Get information about a tensor.

    Args:
        tensor: The tensor object.

    Returns:
        A dictionary containing the name and shape of the tensor.
        If the shape is unknown, it will be set to "Unknown".
    """
    tensor_info = {}
    tensor_info["name"] = tensor.name
    try:
        tensor_info["shape"] = [
            dim.dim_value for dim in tensor.type.tensor_type.shape.dim
        ]
        tensor_info["shape"] = tensor_info["shape"][1:]
    except:
        tensor_info["shape"] = "Unknown"
    return tensor_info


def add_layer_info_to_config(model, config):
    """
    Adds layer information to the configuration dictionary.

    Args:
        model: The deep learning model.
        config: The configuration dictionary.

    Returns:
        The updated configuration dictionary.
    """
    inputs = [get_tensor_info(i) for i in model.graph.input]
    outputs = [get_tensor_info(o) for o in model.graph.output]
    config["inputs"] = inputs
    config["outputs"] = outputs
    return config


def write_config_pbtxt(model_path: str, model_metadata: Dict[str, Union[str, int]]):
    """
    Write the configuration file in pbtxt format for a given model.

    Args:
        model_path (str): The path to the model.
        model_metadata (Dict[str, Union[str, int]]): Metadata of the model including batch size, inputs, and outputs.

    Returns:
        None
    """
    model_name = Path(model_path).parts[-2]
    max_bsz = model_metadata["max_bsz"]

    input_template = """input [
        {{
            name: "{input_name}"
            data_type: TYPE_FP16
            format: FORMAT_NCHW
            dims: {input_shape}
        }}
    ]"""

    output_template = """output [
        {{
            name: "{output_name}"
            data_type: TYPE_FP16
            dims: {output_shape}
        }}
    ]"""

    format_shape = lambda shape: "[" + ", ".join(map(str, shape)) + "]"

    # Processing inputs
    input_sections = ""
    for input in model_metadata["inputs"]:
        formatted_input = input_template.format(
            input_name=input["name"], input_shape=format_shape(input["shape"])
        )
        input_sections += formatted_input + "\n"

    # Processing outputs
    output_sections = ""
    for output in model_metadata["outputs"]:
        formatted_output = output_template.format(
            output_name=output["name"], output_shape=format_shape(output["shape"])
        )
        output_sections += formatted_output + "\n"

    with open(os.path.join(model_path, "..", "config.pbtxt"), "w") as fout:
        fout.write(f'name: "{model_name}"\n')
        fout.write('platform: "tensorrt_plan"\n')
        fout.write(f"max_batch_size: {max_bsz}\n")
        fout.write(f"{input_sections}\n")
        fout.write(f"{output_sections}\n")
        fout.write('default_model_filename: "model.plan"')
