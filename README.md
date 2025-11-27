# SynthStrip Skull-Stripping Service

This service provides a simple FastAPI wrapper around `mri_synthstrip` for on-demand skull-stripping of NIfTI images.

**Location:** `Skull_Stripping_Service/skull_service.py`

## Overview
- Upload a `.nii` or `.nii.gz` file to the `/skullstrip` endpoint.
- The service runs `mri_synthstrip` on the uploaded file and returns a skull-stripped NIfTI file.
- Processed outputs are saved under `processed_nifti/` and logs are written to the `logs/` directory.

## Requirements
- Python 3.8+ (adjust as needed)
- Python packages:
  - `fastapi`
  - `uvicorn`

Install Python dependencies (recommended in a virtualenv):

```bash
python3 -m pip install fastapi uvicorn
```

- System dependency: `mri_synthstrip` (part of SynthStrip / FreeSurfer toolchain). Make sure it is installed and available on the PATH.
  # FreeSurfer (SynthStrip) Installation Guide for WSL
  
  
  ## **1. Download FreeSurfer Tarball**
  
  Download FreeSurfer using `wget` inside WSL:
  
  ```bash
  wget https://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/7.3.2/freesurfer-linux-ubuntu20_amd64-7.3.2.tar.gz
  ```
  
  If downloaded via a Windows browser, it will be stored at:
  
  ```
  /mnt/c/Users/AdityaGandhi/Downloads/pet_scan/Data_Validation_Pipeline/
  ```
  
  ---
  
  ## **2. Extract FreeSurfer in WSL**
  
  ### **Create installation directory:**
  
  ```bash
  sudo mkdir -p /opt/freesurfer
  ```
  
  ### **Extract the tarball to /opt:**
  
  ```bash
  sudo tar -xzvf /mnt/c/Users/AdityaGandhi/Downloads/pet_scan/Data_Validation_Pipeline/freesurfer-linux-ubuntu20_amd64-7.3.2.tar.gz -C /opt
  ```
  
  After extraction, FreeSurfer will be located at:
  
  ```
  /opt/freesurfer/
  ```
  
  ---
  ## **3. Configure FreeSurfer Environment**
  
  Add environment variables to your `~/.bashrc`:
  
  ```bash
  echo "export FREESURFER_HOME=/opt/freesurfer" >> ~/.bashrc
  echo "source \$FREESURFER_HOME/SetUpFreeSurfer.sh" >> ~/.bashrc
  ```
  
  Reload your shell:
  
  ```bash
  source ~/.bashrc
  ```
  
  ---
  
  ## **4. Verify Installation**
  
  Check location of SynthStrip:
  
  ```bash
  which mri_synthstrip
  ```
  
  This should output a path under `/opt/freesurfer/bin`.
  
  Check SynthStrip help:
  
  ```bash
  mri_synthstrip --help
  ```
  
  If the help message appears, SynthStrip is correctly installed.
  
  ---
  
  ## **✔ Completed**
  
  FreeSurfer and SynthStrip are now properly installed and ready for use .

## Running the Service
You can either run the script directly or use `uvicorn`:

Run directly (the script will call uvicorn):

```bash
python3 Skull_Stripping_Service/skull_service.py
```

Or with uvicorn manually:

```bash
cd Skull_Stripping_Service
uvicorn skull_service:app --host 0.0.0.0 --port 8001 --reload
```

The service listens on `0.0.0.0:8001` by default.

## API Endpoint
POST `/skullstrip`
- Form field `file`: the NIfTI file to process (`.nii` or `.nii.gz`).
- Query/form field `use_gpu` (boolean): optional; if true the service will pass `--gpu` to `mri_synthstrip` (if available).

Response: Returns the skull-stripped NIfTI file as a download and also saves it to `processed_nifti/` using the original base name with `_stripped` appended.

## Example curl Upload (save output locally)

Use this exact command to test (this example sends a T2-FLAIR file and writes the output to `stripped_output.nii.gz`):

```bash
curl -X POST "http://localhost:8001/skullstrip" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/mnt/c/Users/AdityaGandhi/Downloads/pet_scan/nifti_t2_extracted/1.2.156.112605.66988331203870.250730145813.2.8084.17547/T2-FLAIR/T2-FLAIR.nii.gz" \
  --output stripped_output.nii.gz
```

Note: Add `-F "use_gpu=true"` to the form if you want the service to attempt GPU mode (requires `mri_synthstrip` compiled with GPU support):

```bash
curl -X POST "http://localhost:8001/skullstrip" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/file.nii.gz" \
  -F "use_gpu=true" \
  --output stripped_output.nii.gz
```

## Output & Logs
- Processed output files are saved to `processed_nifti/` relative to the repository root.
- Runtime logs are written to `logs/skull_service_YYYYMMDD_HHMMSS.log`. Watch logs with:

```bash
tail -f logs/skull_service_*.log
```

## Troubleshooting
- If you see `mri_synthstrip failed` in the logs, check that `mri_synthstrip` is installed and in `PATH` and that the input file is a valid NIfTI.
- If the service exits on startup, check Python package installation and any tracebacks in the `logs/` directory.
- Ensure the uploaded file extension is `.nii` or `.nii.gz`.

## Notes
- Temporary uploaded files are created in the system temp directory and removed after processing.
- Output file naming: `<original_basename>_stripped.nii(.gz)` (saved in `processed_nifti/`).

---
