import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
import os
import json
from io import BytesIO
import requests # To load image from URL

# --- Configuration ---
# Securely load your API key (recommended: use environment variables)
# For Google AI Studio:
GOOGLE_API_KEY = "AIzaSyCh-4jpvU7sNUNz3pi5t6Iq35G9IzQt3U4"
if not GOOGLE_API_KEY:
    raise ValueError("Please set the GOOGLE_API_KEY environment variable.")

genai.configure(api_key=GOOGLE_API_KEY)

# Choose a Gemini model with vision capabilities
# Options: 'gemini-pro-vision' (older), 'gemini-1.5-flash-latest', 'gemini-1.5-pro-latest'
MODEL_NAME = "gemini-1.5-flash-latest" # Flash is faster and cost-effective

# --- Helper Functions ---

def load_image_from_path(image_path: str) -> Image.Image:
    """Loads an image from a local file path."""
    try:
        img = Image.open(image_path)
        # Ensure image is in RGB format for consistency
        if img.mode != 'RGB':
            img = img.convert('RGB')
        return img
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        return None
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None

def load_image_from_url(image_url: str) -> Image.Image:
    """Loads an image from a URL."""
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status() # Raise an exception for bad status codes
        img = Image.open(BytesIO(response.content))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        return img
    except requests.exceptions.RequestException as e:
        print(f"Error fetching image from URL {image_url}: {e}")
        return None
    except Exception as e:
        print(f"Error processing image from URL {image_url}: {e}")
        return None

def get_bounding_boxes_from_gemini(image: Image.Image) -> list:
    """
    Sends an image to Gemini and requests bounding boxes for subjects.

    Args:
        image (PIL.Image.Image): The input image.

    Returns:
        list: A list of dictionaries, where each dictionary represents a detected
              object with 'label' and 'normalized_bbox' ( [xmin, ymin, xmax, ymax]
              between 0.0 and 1.0). Returns empty list on failure.
    """
    model = genai.GenerativeModel(MODEL_NAME)

    # --- This is the CRUCIAL PROMPT ---
    prompt_text = """
    Analyze the provided image carefully.
    Identify the primary subjects or distinct objects in the image.
    For each identified subject/object, provide:
    1. A concise 'label' (e.g., "cat", "car", "person", "tree").
    2. A 'normalized_bbox' representing the bounding box tightly enclosing the subject.
       The bounding box should be a list of four float numbers: [xmin, ymin, xmax, ymax].
       These coordinates must be normalized, meaning they should be between 0.0 and 1.0,
       relative to the image's width and height.
       - xmin: normalized horizontal coordinate of the top-left corner.
       - ymin: normalized vertical coordinate of the top-left corner.
       - xmax: normalized horizontal coordinate of the bottom-right corner.
       - ymax: normalized vertical coordinate of the bottom-right corner.
       Ensure xmin < xmax and ymin < ymax.

    Return the information as a JSON list of objects. Each object in the list
    should have a "label" key and a "normalized_bbox" key.
    Be precise with the bounding box coordinates to ensure they tightly fit the subjects.
    If no distinct subjects are clearly identifiable, return an empty list [].

    Example of desired JSON output format:
    [
      {
        "label": "dog",
        "normalized_bbox": [0.1, 0.2, 0.4, 0.5]
      },
      {
        "label": "person",
        "normalized_bbox": [0.5, 0.3, 0.8, 0.9]
      }
    ]
    """

    print("Sending request to Gemini API...")
    try:
        # The gemini-1.5-flash-latest model directly accepts PIL Images
        response = model.generate_content([prompt_text, image])

        # Clean the response: Gemini might wrap JSON in ```json ... ```
        cleaned_response_text = response.text.strip()
        if cleaned_response_text.startswith("```json"):
            cleaned_response_text = cleaned_response_text[7:]
        if cleaned_response_text.endswith("```"):
            cleaned_response_text = cleaned_response_text[:-3]
        cleaned_response_text = cleaned_response_text.strip()

        # print(f"Raw Gemini Response Text:\n{cleaned_response_text}") # For debugging

        bounding_boxes_data = json.loads(cleaned_response_text)
        if not isinstance(bounding_boxes_data, list):
            print("Warning: Gemini did not return a list as expected.")
            return []
        
        # Validate structure (basic validation)
        valid_boxes = []
        for item in bounding_boxes_data:
            if isinstance(item, dict) and "label" in item and "normalized_bbox" in item:
                bbox = item["normalized_bbox"]
                if isinstance(bbox, list) and len(bbox) == 4 and all(isinstance(n, (float, int)) for n in bbox):
                     # Further ensure coordinates are within [0,1] and xmin < xmax, ymin < ymax
                    xmin, ymin, xmax, ymax = bbox
                    if 0 <= xmin < xmax <= 1 and 0 <= ymin < ymax <= 1:
                        valid_boxes.append(item)
                    else:
                        print(f"Warning: Invalid bbox coordinates for label '{item.get('label')}': {bbox}")
                else:
                    print(f"Warning: Invalid bbox format for label '{item.get('label')}': {bbox}")
            else:
                print(f"Warning: Invalid item structure in Gemini response: {item}")
        return valid_boxes

    except json.JSONDecodeError as e:
        print(f"Error: Could not parse JSON response from Gemini: {e}")
        print(f"Gemini's (cleaned) response was: {cleaned_response_text}")
        return []
    except Exception as e:
        # Catching other potential errors from the API call or response processing
        print(f"An error occurred while interacting with Gemini API: {e}")
        if hasattr(response, 'prompt_feedback'):
            print(f"Prompt Feedback: {response.prompt_feedback}")
        return []


def draw_bounding_boxes(image: Image.Image, detections: list) -> Image.Image:
    """
    Draws bounding boxes and labels on the image.

    Args:
        image (PIL.Image.Image): The original image.
        detections (list): List of detection dicts from Gemini.
                           Each dict must have 'label' and 'normalized_bbox'.

    Returns:
        PIL.Image.Image: Image with bounding boxes drawn.
    """
    draw = ImageDraw.Draw(image)
    img_width, img_height = image.size
    
    try:
        # Attempt to load a common font, fall back to default if not found
        font = ImageFont.truetype("arial.ttf", 15)
    except IOError:
        font = ImageFont.load_default()

    for det in detections:
        label = det['label']
        norm_bbox = det['normalized_bbox'] # [xmin, ymin, xmax, ymax]

        # Convert normalized coordinates to absolute pixel coordinates
        xmin = int(norm_bbox[0] * img_width)
        ymin = int(norm_bbox[1] * img_height)
        xmax = int(norm_bbox[2] * img_width)
        ymax = int(norm_bbox[3] * img_height)

        # Draw rectangle
        draw.rectangle([(xmin, ymin), (xmax, ymax)], outline="lime", width=3)

        # Draw label background
        text_x = xmin
        text_y = ymin - 15 if ymin - 15 > 0 else ymin # Position label above box
        
        # Estimate text size to draw a background
        # For older Pillow versions, textbbox might not be available or accurate
        # For newer versions (Pillow >= 8.0.0):
        if hasattr(draw, 'textbbox'):
            bbox = draw.textbbox((text_x, text_y), label, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        else: # Fallback for older Pillow or simple estimation
            text_width = len(label) * 7 # Approximate
            text_height = 12         # Approximate

        draw.rectangle(
            [(text_x, text_y), (text_x + text_width + 4, text_y + text_height + 4)],
            fill="lime"
        )
        # Draw text
        draw.text((text_x + 2, text_y + 2), label, fill="black", font=font)
        
        print(f"Drew box for: {label} at [{xmin},{ymin},{xmax},{ymax}]")

    return image

# --- Main Execution ---
if __name__ == "__main__":
    # Choose one: image_path or image_url
    # image_path = "path/to/your/local/image.jpg" # e.g., "test_image.jpg"
    image_path = None 
    
    # Example using a URL (replace with your image URL)
    # Try this known image: https://storage.googleapis.com/generativeai-downloads/images/ ακόμα.jpg
    # Or a more complex one: https://images.pexels.com/photos/3760529/pexels-photo-3760529.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1
    # image_url = "https://images.pexels.com/photos/1108099/pexels-photo-1108099.jpeg" # Example: two dogs
    # image_url = "https://images.pexels.com/photos/3355732/pexels-photo-3355732.jpeg?auto=compress&cs=tinysrgb&w=1200"
    image_url = "https://images.pexels.com/photos/139303/pexels-photo-139303.jpeg?auto=compress&cs=tinysrgb&w=1200" # Example: city street

    input_image = None
    if image_path:
        input_image = load_image_from_path(image_path)
    elif image_url:
        input_image = load_image_from_url(image_url)
    else:
        print("No image source specified. Please set image_path or image_url.")
        exit()

    if input_image:
        print(f"Image loaded successfully. Dimensions: {input_image.size}")
        
        # Save a copy of the original for comparison if needed
        # input_image.save("original_temp.png") 
        
        detected_objects = get_bounding_boxes_from_gemini(input_image.copy()) # Send a copy

        if detected_objects:
            print(f"\nDetected {len(detected_objects)} objects:")
            for obj in detected_objects:
                print(f"  - Label: {obj['label']}, BBox (norm): {obj['normalized_bbox']}")

            output_image = draw_bounding_boxes(input_image, detected_objects)
            
            # Save or display the image
            output_image_path = "output_with_boxes.png"
            output_image.save(output_image_path)
            print(f"\nOutput image saved to: {output_image_path}")

            # To display the image (optional, might require a GUI environment)
            try:
                output_image.show()
            except Exception as e:
                print(f"Could not display image automatically (might be running in a non-GUI environment): {e}")
        else:
            print("No objects were detected by Gemini, or an error occurred.")