# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from fastapi import Request,FastAPI
# from pydantic import BaseModel
# import requests
# import os 
# from server.pipeline.end_to_end_pipeline import DFMEAEndToEndPipeline
# import shutil

# app = FastAPI()

# # Enable CORS (for later React UI)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# # Mount output folder
# app.mount("/files", StaticFiles(directory="server/output"), name="files")

# # Request model
# class DFMEARequest(BaseModel):
#     kb_url: str
#     fi_url: str
#     query: str = "Generate DFMEA entries for recent field failures"

# @app.post("/run_dfmea")
# def run_dfmea(req: DFMEARequest):
#     kb_path = "server/sample_files/kb_input.xlsx" if "xlsx" in req.kb_url else "server/sample_files/kb_input.csv"
#     fi_path = "server/sample_files/fi_input.xlsx" if "xlsx" in req.fi_url else "server/sample_files/fi_input.csv"

#     os.makedirs("server/sample_files", exist_ok=True)

    

#     def download(url, path):
#         if url.lower().startswith("http"):
#             # It is a real web URL
#             r = requests.get(url)
#             r.raise_for_status()
#             with open(path, "wb") as f:
#                 f.write(r.content)
#         else:
#             # It's a local file path → copy it
#             shutil.copy(url, path)

#     download(req.kb_url, kb_path)
#     download(req.fi_url, fi_path)

    

#     pipeline = DFMEAEndToEndPipeline(kb_path=kb_path, fi_path=fi_path, query=req.query)
#     output_path = pipeline.run()

#     filename = os.path.basename(output_path)
#     return {
#         "status": "success",
#         "output_file_url": f"http://localhost:8000/files/{filename}"
#     }

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os
import shutil
import time

from server.pipeline.end_to_end_pipeline import DFMEAEndToEndPipeline

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount output folder
OUTPUT_DIR = "output"
SAMPLE_DIR = "server/sample_files"
app.mount("/files", StaticFiles(directory=OUTPUT_DIR), name="files")

# Request model
class DFMEARequest(BaseModel):
    kb_url: str
    fi_url: str
    query: str = "Generate DFMEA entries for recent field failures"

@app.post("/run_dfmea")
def run_dfmea(req: DFMEARequest):
    os.makedirs(SAMPLE_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    kb_path = os.path.join(SAMPLE_DIR, "kb_input.xlsx" if "xlsx" in req.kb_url else "kb_input.csv")
    fi_path = os.path.join(SAMPLE_DIR, "fi_input.xlsx" if "xlsx" in req.fi_url else "fi_input.csv")

    def download(url, path):
        if url.lower().startswith("http"):
            r = requests.get(url)
            r.raise_for_status()
            with open(path, "wb") as f:
                f.write(r.content)
                f.flush()
                os.fsync(f.fileno())
        else:
            shutil.copy(url, path)

    download(req.kb_url, kb_path)
    download(req.fi_url, fi_path)

    pipeline = DFMEAEndToEndPipeline(kb_path=kb_path, fi_path=fi_path, query=req.query)
    output_path = pipeline.run()

    # Wait briefly to ensure file is fully written before accessing
    time.sleep(0.2)

    filename = os.path.basename(output_path)
    file_url = f"http://localhost:8000/files/{filename}"

    return {
        "status": "success",
        "message": "DFMEA file generated successfully.",
        "output_file_url": file_url
    }
