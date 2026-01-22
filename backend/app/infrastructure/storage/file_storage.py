"""
File Storage Implementation.
Handles file operations for document generation.
"""

from pathlib import Path
from typing import Optional
import shutil
import uuid
from PIL import Image
import cairosvg
import logging

logger = logging.getLogger(__name__)


class FileStorage:
    """
    File storage service for handling document-related files.
    """

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize file storage.

        Args:
            base_path: Base directory for file storage
        """
        self.base_path = base_path or Path("generated")
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save_file(self, source_path: Path, destination_dir: str) -> Path:
        """
        Save a file to the storage directory.

        Args:
            source_path: Path to the source file
            destination_dir: Subdirectory within base_path

        Returns:
            Path to the saved file
        """
        # Create destination directory
        dest_dir = self.base_path / destination_dir
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename
        unique_name = f"{uuid.uuid4().hex[:8]}_{source_path.name}"
        dest_path = dest_dir / unique_name

        # Copy file
        shutil.copy2(source_path, dest_path)

        return dest_path

    async def process_logo(self, logo_path: Path, output_path: Path) -> Path:
        """
        Process and optimize a logo image.

        Args:
            logo_path: Path to the original logo
            output_path: Path for the processed logo

        Returns:
            Path to the processed logo
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if logo_path.suffix.lower() == ".svg":
                # Convert SVG to PNG
                cairosvg.svg2png(
                    url=str(logo_path),
                    write_to=str(output_path),
                    output_width=200,
                    output_height=200
                )
                logger.info(f"Converted SVG logo to PNG: {output_path}")
            else:
                # Process raster image
                with Image.open(logo_path) as img:
                    # Resize if too large
                    max_size = (200, 200)
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)

                    # Convert to RGB if necessary
                    if img.mode in ('RGBA', 'LA', 'P'):
                        # Create a white background
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if 'A' in img.mode else None)
                        img = background

                    # Save optimized image
                    img.save(output_path, optimize=True, quality=95)
                    logger.info(f"Optimized logo image: {output_path}")

            return output_path

        except Exception as e:
            logger.error(f"Failed to process logo: {e}")
            # Fallback to simple copy
            shutil.copy2(logo_path, output_path)
            return output_path

    async def delete_file(self, file_path: Path) -> bool:
        """
        Delete a file from storage.

        Args:
            file_path: Path to the file to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return False

    def get_file_path(self, subdirectory: str, filename: str) -> Path:
        """
        Get the full path for a file in storage.

        Args:
            subdirectory: Subdirectory within base_path
            filename: Name of the file

        Returns:
            Full path to the file
        """
        return self.base_path / subdirectory / filename

    def ensure_directory(self, subdirectory: str) -> Path:
        """
        Ensure a subdirectory exists.

        Args:
            subdirectory: Subdirectory to create

        Returns:
            Path to the directory
        """
        dir_path = self.base_path / subdirectory
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path