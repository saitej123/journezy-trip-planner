"""
Image handling utilities for the trip planner.
Handles image loading, fallbacks, and conversion for PDF generation.
"""

import os
import base64
import requests
from typing import Optional, Tuple
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

class ImageHandler:
    """Handles image processing and fallbacks for the trip planner"""
    
    def __init__(self, static_path: str = "static"):
        self.static_path = static_path
        self.fallback_dir = os.path.join(static_path, "images", "fallbacks")
        self.default_fallback = os.path.join(self.fallback_dir, "no-image.png")
        
    def get_image_data(self, image_url: str, fallback_type: str = "no-image") -> Tuple[str, bool]:
        """
        Get image data as base64 or return fallback.
        Returns (image_data, is_fallback)
        """
        if not image_url or image_url == "N/A":
            return self._get_fallback_image(fallback_type), True
            
        # Check if it's a local path
        if image_url.startswith('/static/') or image_url.startswith('static/'):
            return self._get_local_image(image_url), False
            
        # Check if it's an external URL
        if image_url.startswith('http'):
            return self._get_external_image(image_url, fallback_type)
            
        # Default to fallback
        return self._get_fallback_image(fallback_type), True
    
    def _get_local_image(self, image_path: str) -> str:
        """Get local image as base64"""
        try:
            # Normalize path
            if image_path.startswith('/static/'):
                image_path = image_path[8:]  # Remove '/static/' prefix
            elif image_path.startswith('static/'):
                image_path = image_path[7:]  # Remove 'static/' prefix
                
            full_path = os.path.join(self.static_path, image_path)
            
            if os.path.exists(full_path):
                with open(full_path, 'rb') as f:
                    image_data = f.read()
                return base64.b64encode(image_data).decode('utf-8')
            else:
                logger.warning(f"Local image not found: {full_path}")
                return self._get_fallback_image("no-image")
        except Exception as e:
            logger.error(f"Error reading local image {image_path}: {e}")
            return self._get_fallback_image("no-image")
    
    def _get_external_image(self, image_url: str, fallback_type: str) -> Tuple[str, bool]:
        """Get external image as base64 with fallback"""
        try:
            # Skip problematic URLs
            if self._is_problematic_url(image_url):
                logger.warning(f"Skipping problematic URL: {image_url}")
                return self._get_fallback_image(fallback_type), True
                
            # Try to fetch the image with timeout
            response = requests.get(image_url, timeout=10, stream=True)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if not content_type.startswith('image/'):
                logger.warning(f"URL does not return image content: {image_url}")
                return self._get_fallback_image(fallback_type), True
                
            # Convert to base64
            image_data = response.content
            return base64.b64encode(image_data).decode('utf-8'), False
            
        except Exception as e:
            logger.warning(f"Failed to fetch external image {image_url}: {e}")
            return self._get_fallback_image(fallback_type), True
    
    def _get_fallback_image(self, fallback_type: str) -> str:
        """Get fallback image as base64"""
        fallback_file = os.path.join(self.fallback_dir, f"{fallback_type}.png")
        
        if not os.path.exists(fallback_file):
            fallback_file = self.default_fallback
            
        try:
            with open(fallback_file, 'rb') as f:
                image_data = f.read()
            return base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            logger.error(f"Error reading fallback image {fallback_file}: {e}")
            # Return a minimal 1x1 pixel PNG as last resort
            return self._get_minimal_png()
    
    def _is_problematic_url(self, url: str) -> bool:
        """Check if URL is known to be problematic"""
        problematic_patterns = [
            'googleusercontent.com/gps-cs-s/',
            'lh3.googleusercontent.com/gps-cs-s/',
            'placeholder.com',
            'via.placeholder',
            'brw-',
            'ZAxdA-eob4MR40Zy'
        ]
        
        return any(pattern in url for pattern in problematic_patterns)
    
    def _get_minimal_png(self) -> str:
        """Return a minimal 1x1 transparent PNG as base64"""
        # Minimal 1x1 transparent PNG
        minimal_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
        return base64.b64encode(minimal_png).decode('utf-8')
    
    def get_image_html(self, image_url: str, alt_text: str = "Image", fallback_type: str = "no-image", 
                      max_width: str = "200px", max_height: str = "150px") -> str:
        """Get image as HTML with base64 data URI"""
        image_data, is_fallback = self.get_image_data(image_url, fallback_type)
        
        # Determine appropriate MIME type
        mime_type = "image/png"  # Default to PNG since our fallbacks are PNG
        
        data_uri = f"data:{mime_type};base64,{image_data}"
        
        return f'''
        <div class="image-container" style="text-align: center; margin: 10px 0;">
            <img src="{data_uri}" 
                 alt="{alt_text}" 
                 style="max-width: {max_width}; max-height: {max_height}; object-fit: cover; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);"
                 onerror="this.style.display='none';">
        </div>
        '''

# Global instance
image_handler = ImageHandler()
