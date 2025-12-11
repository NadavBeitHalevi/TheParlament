# import time
# from google import genai  # type: ignore
# from dotenv import load_dotenv
# import os

# load_dotenv()

# client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))  # type: ignore

# prompt = """Drone shot following a classic red convertible driven by a man along a winding coastal road at sunset, waves crashing against the rocks below.
# The convertible accelerates fast and the engine roars loudly."""

# operation = client.models.generate_videos(  # type: ignore
#     model="veo-3.1-generate-preview",
#     prompt=prompt,
# )

# # Poll the operation status until the video is ready.
# while not operation.done:
#     print("Waiting for video generation to complete...")
#     time.sleep(10)
#     operation = client.operations.get(operation)  # type: ignore

# # Download the generated video.
# generated_video = operation.response.generated_videos[0]  # type: ignore
# client.files.download(file=generated_video.video)  # type: ignore
# generated_video.video.save("realism_example.mp4")  # type: ignore
# print("Generated video saved to realism_example.mp4")

# ============================================================================
# google_api_key = os.getenv("GOOGLE_API_KEY")

# client = genai.Client(api_key=google_api_key)

# prompt = (
#     "Create a picture of a nano banana dish in a fancy restaurant with a Gemini theme"
# )

# response = client.models.generate_content(
#     model="gemini-2.5-flash-image",
#     contents=[prompt],
# )

# for part in response.parts:
#     if part.text is not None:
#         print(part.text)
#     elif part.inline_data is not None:
#         image = part.as_image()
#         image.save("generated_image.png")