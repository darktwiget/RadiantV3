import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# Add the root directory to Python path
root_dir = str(Path(__file__).parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from heurist_image.ImageGen import ImageGen
from heurist_image.SmartGen import SmartGen

# Load environment variables from .env file
load_dotenv(find_dotenv())

async def test_basic_image_generation():
    """Test basic image generation."""
    print("\n1. Testing Basic Image Generation")
    print("-" * 50)
    api_key = os.getenv("HEURIST_API_KEY")
    if not api_key:
        raise EnvironmentError("Missing HEURIST_API_KEY in environment variables.")
    async with ImageGen(api_key=api_key) as generator:
        try:
            response = await generator.generate({
                "model": "FLUX.1-dev",
                "prompt": "A serene Japanese garden with cherry blossoms",
                "width": 1024,
                "height": 768,
                "num_iterations": 20,
                "guidance_scale": 7.5,
                "seed": None
            })
            print("✓ Image Generated Successfully"),
            print(f"URL: {response['url']}")
            print(f"Full response: {response}\n")
            return True
            return True
        except Exception as e:
            print(f"✗ Image Generation Failed: {e}\n")
            return False

async def test_smartgen():
    """Test SmartGen image generation."""
    """Test SmartGen image generation using specific parameters."""
    print("-" * 50)
    api_key = os.getenv("HEURIST_API_KEY")
    if not api_key:
        raise EnvironmentError("Missing HEURIST_API_KEY in environment variables.")
    async with SmartGen(api_key=api_key) as generator:
        try:
            response = await generator.generate_image(
                description="A futuristic cyberpunk cityscape",
                image_model="FLUX.1-dev",
                stylization_level=4,
                detail_level=5,
                color_level=5,
                lighting_level=4,
                must_include="neon lights, flying cars",
                quality="high"
            )
            print("✓ SmartGen Image Generated Successfully:")
            print(f"URL: {response['url']}")
            print(f"Parameters used: {response['parameters']}\n")
            return True
        except Exception as e:
            print(f"✗ SmartGen Failed: {e}\n")
            return False

async def main():
    """Run all tests."""
    print("Starting Image Generation Tests...\n")
    
    test_results = await asyncio.gather(
        test_basic_image_generation(),
        test_smartgen()
    )
    basic_test_result, smartgen_test_result = test_results
    smartgen_test_result = await test_smartgen()
    
    # Print summary
    print("\nTest Summary:")
    print("-" * 50)
    print(f"Basic Image Generation: {'✓ Passed' if basic_test_result else '✗ Failed'}")
    print(f"SmartGen: {'✓ Passed' if smartgen_test_result else '✗ Failed'}")
    
    # Return overall success
    return basic_test_result and smartgen_test_result

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        success = False
    exit(0 if success else 1) 