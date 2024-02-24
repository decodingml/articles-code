# YOLO Model Optimization (PyTorch 2 TensorRT) Pipeline

In real-time deep learning systems, models have to be optimized for performance.
With this implementation, we're automating the process of optimizing a PyTorch model to TensorRT GPU-specific format, such that this pipeline could be
integrated as a CI/CD step or within any process-orchestration tool like Airflow, Prefect or Metaflow.
In this article, we'll set a single `.json` configuration file with the desired model parameters and then run the pipeline - the output of which being a model 100% configurated
to be used within the NVIDIA Triton Inference Server framework for serving.

The contents of the outputs are defaulted in `./model_repository` folder.
Here, each sub-folder is an optimized model in itself:
```
__model_repository
|
|-- [model_one]
|   |-- 1/
|   |   |-- model.plan
|   |
|   |-- config.pbtxt

```


![Architecture](./media/model-conversion-pipeline.png)

**Here's what we'll learn**

- adding YOLO5/YOLO8 as submodules
- converting pt2onnx generically
- handling model integrity checks
- auto-formatting .engine for model serving with Triton Server
- auto-parsing model configurations
- auto create folder structure
- auto define model naming from configuration .json
- handling docker containers from within python
- selecting FP16 or Dynamic Batching automatically

## Table of Contents

- [YOLO Model Optimization (PyTorch 2 TensorRT) Pipeline](#yolo-model-optimization-pytorch-2-tensorrt-pipeline)
  - [Table of Contents](#table-of-contents)
  - [Articles](#articles)
  - [Dependencies](#dependencies)
  - [Install](#install)
  - [Usage](#usage)
  - [License](#license)
  - [Contributors](#contributors)

------

## Articles

To fully grasp the code, check out our articles ↓

1. [Full Article](https://decodingml.substack.com/p/dml-how-to-deploy-deep-learning-models)

## Dependencies

- [Python (version 3.9)](https://www.python.org/downloads/)
- [Poetry (version 1.6.1)](https://python-poetry.org/)
- [GNU Make (version 3.81)](https://www.gnu.org/software/make/)
- [Docker (version 24.0.7)](https://www.docker.com/)


## Install



## Usage

1. Start by installing the dependencies
```shell
poetry install
```

2. Configure the `blueprint.json`:
```shell
{   
    "tritonserver_version": "22.12",    # Version of Triton to Deploy to
    "model_family": "yolo-s",           # Used within the model naming metadata
    "model_release": 5,                 # Used within the model naming metadata
    "weights": "yolov5s.pt",            # Path to the .pt model
    "imgsz": [640, 640],                # Input image size
    "device": "0",                      # Device ID to use when building TensorRT model
    "dtype": "fp16",                    # Target datatype, FP16 defaulted
    "min_bsz": 1,                       # In case of dynamic batch, min_batch = 1
    "max_bsz": 8,                       # In case of dynamic batch, max_batch = 8
    "dynamic": true,                    # Dynamic tells ONNX model to build with dynamic axes
    "nms": true,                        # Include NMS as part of yolo models
    "simplify": true,                   # Simplifies the ONNX model (layer merges, layer cuts and other optimizations. Reduces model size.)
    "opset": 14,                        # Desired ONNX Operator Set Version (14 is ok)
    "project": "sample",      # Used within the model naming metadata
    "task": "objectdetection",          # Used within the model naming metadata
    "version": "1.0"                    # Used within the model naming metadata
}

This is how the generated model will look like:
SAMPLE_OBJECTDETECTION_YOLO5S_851_RTX3080_FP16_CC78_1.0/
```

3. Run pipeline:
```shell
python object_detectors/pt2trt.py --config blueprint.json
```


## License

This article is an open-source project released under the MIT license. Thus, as long you distribute our LICENSE and acknowledge our work, you can safely clone or fork this project and use it as a source of inspiration for whatever you want (e.g., work, university projects, college degree projects, etc.).

## Contributors

<table>
  <tr>
    <td><img src="https://github.com/Joywalker.png" width="100" style="border-radius:50%;"/></td>
    <td>
      <strong>Alex Razvant</strong><br />
      <i>Senior Machine Learning Engineer</i>
    </td>
  </tr>
</table>