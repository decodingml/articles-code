import gradio as gr
from dotenv import load_dotenv

from inference import DiffusionInference
from config import TrainingConfig


# Define the function to generate an image
def generate_image():
    return inference_model.generate_unconditioned_image()

# Create the Gradio interface
def create_gradio_interface():
    output_image = gr.Image(label="Generated Image")  # Use gr.Image for output component

    interface = gr.Interface(
        fn=generate_image,
        inputs=[],  # No inputs needed
        outputs=output_image,
        title="Unconditioned Diffusion Model Image Generator",
        description="Generate images using an unconditioned diffusion model."
    )

    # Launch the interface
    interface.launch(share=True)

# Load Env Variables from .env file
load_dotenv()

# Load Training Config from config.yaml file
config = TrainingConfig.load_from_yaml("config.yaml")

# Load Inference Pipeline from Huggingface
inference_model = DiffusionInference(config.huggingface_repo_name)

# Launch Gradio interface
create_gradio_interface()

