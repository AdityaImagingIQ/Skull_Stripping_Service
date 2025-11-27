import os
import subprocess
import logging
from datetime import datetime
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from tempfile import NamedTemporaryFile
from pathlib import Path
import uvicorn

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / f"skull_service_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


app = FastAPI(title="SynthStrip API")

PERMANENT_SAVE_DIR = "processed_nifti"
Path(PERMANENT_SAVE_DIR).mkdir(parents=True, exist_ok=True)
logger.info(f"Permanent save directory configured: {PERMANENT_SAVE_DIR}")


def run_synthstrip(input_path, output_path, use_gpu=False):
    logger.debug(f"Executing mri_synthstrip: input={input_path}, output={output_path}, gpu={use_gpu}")
    
    cmd = ["mri_synthstrip", "-i", input_path, "-o", output_path]
    if use_gpu:
        cmd.append("--gpu")
        logger.debug("GPU mode enabled")

    logger.info(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        logger.error(f"mri_synthstrip failed with return code {result.returncode}: {result.stderr}")
        raise RuntimeError(result.stderr)
    
    logger.info(f"Successfully completed skull-stripping: {os.path.basename(output_path)}")
    return output_path


@app.post("/skullstrip")
async def skullstrip(file: UploadFile = File(...), use_gpu: bool = False):
    logger.info(f"Received skull-stripping request for file: {file.filename}")
    logger.debug(f"GPU mode: {use_gpu}")

  
    filename = file.filename
    if filename.endswith(".nii.gz"):
        ext = ".nii.gz"
        base = filename.replace(".nii.gz", "")
    elif filename.endswith(".nii"):
        ext = ".nii"
        base = filename.replace(".nii", "")
    else:
        logger.warning(f"Invalid file format received: {filename}")
        return {"error": "Invalid file format. Only .nii and .nii.gz allowed."}

    logger.info(f"File format validated: {ext}")
    logger.debug(f"File base name: {base}")
  
    with NamedTemporaryFile(delete=False, suffix=ext) as tmp_in:
        file_content = await file.read()
        tmp_in.write(file_content)
        tmp_input_path = tmp_in.name
        logger.debug(f"Temporary file created: {tmp_input_path} (size: {len(file_content)} bytes)")

   
    permanent_output_path = os.path.join(
        PERMANENT_SAVE_DIR, f"{base}_stripped{ext}"
    )
    logger.info(f"Output path: {permanent_output_path}")

    try:
        run_synthstrip(tmp_input_path, permanent_output_path, use_gpu)
        logger.info(f"Returning processed file: {os.path.basename(permanent_output_path)}")

        return FileResponse(
            permanent_output_path,
            media_type="application/gzip" if ext.endswith("gz") else "application/octet-stream",
            filename=os.path.basename(permanent_output_path)
        )

    except Exception as e:
        logger.error(f"Error during skull-stripping: {str(e)}", exc_info=True)
        raise
        
    finally:
        if os.path.exists(tmp_input_path):
            os.remove(tmp_input_path)
            logger.debug(f"Temporary file deleted: {tmp_input_path}")


if __name__ == "__main__":
    logger.info("="*60)
    logger.info("Starting SynthStrip Skull Stripping API Service")
    logger.info("="*60)
    logger.info(f"Server configuration: host=0.0.0.0, port=8001")
    logger.info(f"Permanent save directory: {PERMANENT_SAVE_DIR}")
    logger.info("="*60)
    
    uvicorn.run("skull_service:app", host="0.0.0.0", port=8001, reload=True)
