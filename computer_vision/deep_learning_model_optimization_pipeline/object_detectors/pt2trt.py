import argparse
import json
import logging

import helpers
import modelinfo

logger = logging.getLogger("Convertor")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s][%(levelname)s] : %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


def pipeline(model_config):
    """
    Converts a yolo.pt model to TritonInferenceServer, TensorRT format.

    Follows this pipeline:
    ```
    arguments >>
        parse_config >>
            validate_config >>
                pt2onnx >>
                    prep_model_metadata >>
                        start_trt_container >>
                            build_engine >>
                                close_containers >>
                                    write_tis_config >>
                                        DONE.
    ```
    """
    try:
        model_config = helpers.parse_config(model_config)
        logger.info("🟢\t\t Parsing config ")
        model_config = helpers.validate_config(
            model_config, container_version=model_config["tritonserver_version"]
        )
        logger.info("🟢🟢\t\t Validating config")
    except Exception:
        logger.info("🔴\t\t Validating config ")
        exit(-1)

    try:
        onnx_path = helpers.pt2onnx(
            config=model_config, version=model_config["model_release"]
        )
        logger.info("🟢🟢🟢\t\t Pytorch to ONNX")
        onnx_model = modelinfo.test_onnx_model(onnx_path)
        logger.info("🟢🟢🟢🟢\t\t Checking ONNX")
    except Exception as e:
        logger.info("🔴\t\t Pytorch to ONNX")
        logger.error(f"🔴🔴 {e}")
        exit(-1)

    try:
        modelinfo.add_layer_info_to_config(onnx_model, model_config)
        logger.info("🟢🟢🟢🟢🟢\t\t Adding inputs/outputs metadata")
        model_metadata = modelinfo.build_model_metadata(model_config)
        logger.info("🟢🟢🟢🟢🟢🟢\t\t Building model config")
        trt_container = helpers.start_trt_container(
            container_version=config["tritonserver_version"]
        )
        logger.info(
            f"🟢🟢🟢🟢🟢🟢🟢\t\t Starting TensorRT{config['tritonserver_version']}"
        )
    except Exception as e:
        logger.info("🔴\t\t Parsing ONNX model metadata")
        logger.error(f"🔴🔴 {e}")

    try:
        model_folder = helpers.build_engine(
            onnx_path=onnx_path,
            container=trt_container,
            metadata=model_metadata,
            config=model_config,
        )
        logger.info("🟢🟢🟢🟢🟢🟢🟢🟢\t\t TensorRT plan generated")
        modelinfo.write_config_pbtxt(
            model_folder,
            config,
        )
        logger.info("🟢🟢🟢🟢🟢🟢🟢🟢🟢\t\t Saved config.pbtxt")
        trt_container.stop()
        trt_container.remove()
        logger.info("🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢\t\t Removed container")
    except Exception as e:
        logger.info("🔴\t\t Failed to build engine")
        logger.error(f"🔴🔴 {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=str,
        help="Path to the model config.json",
        default="/data/arazvant/conversion/tensorrt_conversion/blueprint.json",
    )
    args = parser.parse_args()
    config = json.load(open(args.config, "r"))
    pretty_json = json.dumps(config, indent=4)
    logger.info("==== Model Conversion Pipeline ====")
    logger.info("Model Configuration:")
    logger.info(pretty_json)
    logger.info("=" * 50)

    # Run Pipeline
    pipeline(config)
