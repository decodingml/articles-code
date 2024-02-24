import os
import sys

import numpy as np
import tools
import tritonclient.http as httpclient
from scipy.special import softmax

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

if __name__ == "__main__":
    # == Set up model parameters ==
    MODEL_INPUT_NAME = "input"
    MODEL_OUTPUT_NAME = "output"
    MODEL_NAME_ON_SERVER = "mobilenetv2_imc"
    MODEL_VERSION_ON_SERVER = "1"

    # == Prepare image for inference ==
    image = tools.load_image("./media/pizzaa.png")
    image = tools.resize_image(image, 256)
    image = tools.crop_center(image, 224, 224)
    image = tools.normalize_image(image)

    # == Prepare class labels ==
    categories = tools.load_classes("./imagenet_classes.txt")

    # Prepare server connection
    triton_client = httpclient.InferenceServerClient(url="localhost:8000", verbose=True)

    # Define the input tensor placeholder
    input_data = httpclient.InferInput(MODEL_INPUT_NAME, image.shape, "FP32")

    # Populate the tensor with data
    input_data.set_data_from_numpy(image)

    # Send inference request
    request = triton_client.infer(
        MODEL_NAME_ON_SERVER, model_version=MODEL_VERSION_ON_SERVER, inputs=[input_data]
    )

    # Unpack the output layer as numpy
    output = request.as_numpy(MODEL_OUTPUT_NAME)

    # Flatten the values
    output = np.squeeze(output)

    # Since it's image classification, apply softmax
    probabilities = softmax(output)

    # Get Top5 prediction labels
    top5_class_ids = np.argsort(probabilities)[-5:][::-1]

    # Pretty print the results
    print("\nInference outputs (TOP5):")
    print("=========================")
    padding_str_width = 10
    for class_id in top5_class_ids:
        score = probabilities[class_id]
        print(
            f"CLASS: [{categories[class_id]:<{padding_str_width}}]\t: SCORE [{score*100:.2f}%]"
        )
