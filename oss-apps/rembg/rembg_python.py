import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Optional
from rembg import remove, new_session
import PIL.Image
import argparse

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ImageProcessor:
    """Background removal image processor class"""
    
    def __init__(self, input_dir: str, model_name: str = "u2net"):
        """
        Initialize the image processor
        
        Args:
            input_dir (str): Input directory path containing images
            model_name (str): Default model name to use
        """
        self.input_dir = Path(input_dir)
        self.default_model = model_name
        self.model_sessions = {}
        self.models_dir = Path(__file__).parent / "models"
        self.config = self._load_config()
        
        if not self.input_dir.exists():
            raise FileNotFoundError(f"Input directory '{input_dir}' does not exist")
        
        if not self.models_dir.exists():
            raise FileNotFoundError(f"Models directory '{self.models_dir}' does not exist")
            
        logger.info(f"Initialized ImageProcessor with input directory: {input_dir}")
        logger.info(f"Using models directory: {self.models_dir}")
        
    def _load_config(self) -> Dict:
        """Load configuration from JSON file if it exists"""
        config_path = self.input_dir / "config.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                logger.info("Loaded configuration file successfully")
                return config
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing config.json: {e}")
                return {}
        return {}
    
    def _get_model_session(self, model_name: str):
        """Get or create a model session"""
        if model_name not in self.model_sessions:
            model_path = self.models_dir / f"{model_name}.onnx"
            if not model_path.exists():
                raise FileNotFoundError(f"Model file not found: {model_path}")
                
            logger.info(f"Creating new session for model: {model_name} from {model_path}")
            self.model_sessions[model_name] = new_session(model_name, model_path=str(model_path))
        return self.model_sessions[model_name]
    
    def _get_model_for_image(self, image_path: Path) -> str:
        """Get the model name for a specific image from config or use default"""
        image_name = image_path.name
        if image_name in self.config:
            model_name = self.config[image_name].get('model', self.default_model)
            logger.info(f"Using model '{model_name}' for image: {image_name}")
            return model_name
        return self.default_model
    
    def process_image(self, input_path: Path) -> bool:
        """
        Process a single image
        
        Args:
            input_path (Path): Path to the input image
            
        Returns:
            bool: True if processing was successful, False otherwise
        """
        try:
            # Generate output path with prefix
            output_path = input_path.parent / f"output_{input_path.stem}.png"
            
            # Get model for this image
            model_name = self._get_model_for_image(input_path)
            session = self._get_model_session(model_name)
            
            # Load and process image
            input_image = PIL.Image.open(input_path)
            output_image = remove(input_image, session=session)
            
            # Save processed image
            output_image.save(output_path)
            logger.info(f"Successfully processed {input_path.name} -> {output_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing {input_path.name}: {str(e)}")
            return False
    
    def process_directory(self):
        """Process all images in the input directory"""
        image_extensions = {'.png', '.jpg', '.jpeg', '.webp'}
        processed_count = 0
        error_count = 0
        
        logger.info(f"Starting directory processing: {self.input_dir}")
        
        for file_path in self.input_dir.iterdir():
            if file_path.suffix.lower() in image_extensions:
                if self.process_image(file_path):
                    processed_count += 1
                else:
                    error_count += 1
                    
        logger.info(f"Directory processing complete. "
                   f"Processed: {processed_count}, Errors: {error_count}")

def main():
    parser = argparse.ArgumentParser(description='Remove background from images in a directory')
    parser.add_argument('input_dir', help='Input directory containing images')
    parser.add_argument('--model', default='u2net', 
                      help='Default model to use (default: u2net)')
    
    args = parser.parse_args()
    
    try:
        processor = ImageProcessor(args.input_dir, args.model)
        processor.process_directory()
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
