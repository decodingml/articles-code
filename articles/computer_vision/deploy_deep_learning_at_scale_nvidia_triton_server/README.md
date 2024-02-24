# Deploy Deep Learning Models at Scale using NVIDIA Triton Inference Server

NVIDIA Triton Inference Server is a powerful framework used at large in production environments to handle model serving.
In this article, we'll go over how to prepare,set,serve and use a Image Classification (MobileNetV2) model deployed within the Triton Inference Server.


![Architecture](./media/triton-inference-server-clean.png)

**Here's what we'll learn**

- what is NVIDIA Triton Inference Server
- how to download and prepare a model
- how to write the configuration file for the model
- how to start the Triton Inference Server via docker-compose
- how to use a Makefile to automate processes
- how to connect to the server and perform inference using the HTTP protocol
- how to pre-process/post-process the inputs/outputs from the server

## Table of Contents

- [Deploy Deep Learning Models at Scale using NVIDIA Triton Inference Server](#deploy-deep-learning-models-at-scale-using-nvidia-triton-inference-server)
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

```First, let's install the nvidia-docker runtime that will allow the interface between docker containers and the underlying HW of the PC. In this case, the NVIDIA GPU.```
As we use Make and Poetry to manage the project, to install the project, you have to run the following:
```shell
make install_nvidia_container_runtime
```

Next, install the project dependencies using:
```shell
make install
```

And setup the .env file to handle a few masked variables:
```shell
make fix_env
```


## Usage

Let's start the NVIDIA Triton Server, using the makefile command:
```shell
make start_tis
```

Next, let's run the client which will take an image of a pizza and send it to the Server to perform inference:
```shell
python src/client.py
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
