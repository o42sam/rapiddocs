import os
import aiofiles
from datetime import datetime
from typing import Optional
from PIL import Image
import io
import cairosvg
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger('storage_service')


class StorageService:
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.pdf_dir = settings.PDF_OUTPUT_DIR

    async def save_upload(self, file_data: bytes, filename: str, subdir: str = "logos") -> str:
        """Save uploaded file and return path. Converts SVG to PNG for compatibility."""
        # Create subdirectory
        target_dir = os.path.join(self.upload_dir, subdir)
        os.makedirs(target_dir, exist_ok=True)

        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name, ext = os.path.splitext(filename)

        # If SVG, convert to PNG using cairosvg
        if ext.lower() == '.svg':
            try:
                logger.info(f"Converting SVG to PNG: {filename}")
                # Convert SVG to PNG
                png_data = cairosvg.svg2png(bytestring=file_data, output_width=800, output_height=800)

                # Save as PNG
                unique_filename = f"{name}_{timestamp}.png"
                file_path = os.path.join(target_dir, unique_filename)

                async with aiofiles.open(file_path, 'wb') as f:
                    await f.write(png_data)

                logger.info(f"SVG converted and saved to: {file_path}")
                return file_path
            except Exception as e:
                logger.error(f"Failed to convert SVG: {str(e)}", exc_info=True)
                # If conversion fails, try saving as-is (won't work with PDF but better than None)
                unique_filename = f"{name}_{timestamp}{ext}"
                file_path = os.path.join(target_dir, unique_filename)
                async with aiofiles.open(file_path, 'wb') as f:
                    await f.write(file_data)
                return file_path

        unique_filename = f"{name}_{timestamp}{ext}"
        file_path = os.path.join(target_dir, unique_filename)

        # For image files, try to convert to PNG for consistency
        if ext.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            try:
                logger.info(f"Processing image file: {filename}")
                # Open image with PIL
                img = Image.open(io.BytesIO(file_data))
                # Convert to RGB if necessary (for PNG transparency)
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                # Save as PNG
                unique_filename = f"{name}_{timestamp}.png"
                file_path = os.path.join(target_dir, unique_filename)

                # Save synchronously (PIL doesn't support async)
                img.save(file_path, 'PNG')
                logger.info(f"Image saved successfully to: {file_path}")
                return file_path
            except Exception as e:
                logger.error(f"Image conversion failed: {str(e)}, saving as-is", exc_info=True)
                # Fall back to saving original
                pass

        # Save file as-is
        logger.info(f"Saving file as-is: {unique_filename}")
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_data)

        logger.info(f"File saved successfully to: {file_path}")
        return file_path

    async def save_generated_image(self, image_data: bytes, doc_id: str, image_num: int) -> str:
        """Save generated image"""
        subdir = os.path.join("images", doc_id)
        target_dir = os.path.join(self.upload_dir, subdir)
        os.makedirs(target_dir, exist_ok=True)

        filename = f"image_{image_num}.png"
        file_path = os.path.join(target_dir, filename)

        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(image_data)

        return file_path

    async def save_visualization(self, viz_data: bytes, doc_id: str, stat_name: str) -> str:
        """Save visualization chart"""
        subdir = os.path.join("visualizations", doc_id)
        target_dir = os.path.join(self.upload_dir, subdir)
        os.makedirs(target_dir, exist_ok=True)

        # Clean stat name for filename
        clean_name = "".join(c if c.isalnum() else "_" for c in stat_name)
        filename = f"{clean_name}_chart.png"
        file_path = os.path.join(target_dir, filename)

        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(viz_data)

        return file_path

    def get_pdf_path(self, doc_id: str, title: str) -> str:
        """Get path for PDF output"""
        os.makedirs(self.pdf_dir, exist_ok=True)

        # Clean title for filename
        clean_title = "".join(c if c.isalnum() or c == ' ' else "_" for c in title)
        clean_title = clean_title.replace(' ', '_')[:50]

        filename = f"{doc_id}_{clean_title}.pdf"
        return os.path.join(self.pdf_dir, filename)

    def get_public_url(self, file_path: str) -> str:
        """Get public URL for file"""
        # For local development, return relative path
        # In production, this would return S3 URL or CDN URL
        if file_path.startswith(self.pdf_dir):
            filename = os.path.basename(file_path)
            return f"/pdfs/{filename}"

        return file_path

    def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        return os.path.exists(file_path)

    async def delete_file(self, file_path: str):
        """Delete a file"""
        if os.path.exists(file_path):
            os.remove(file_path)


storage_service = StorageService()
