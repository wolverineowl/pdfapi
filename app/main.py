from fastapi import FastAPI, Depends, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List
from tempfile import TemporaryDirectory
from pathlib import Path
from app_process import *
from app_spaces import *
import auth
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

class FileAttrib(BaseModel):
    rotateby: int
    # point: Optional[float] = None
    # is_accepted: Optional[bool] = False


@app.post("/merge", dependencies=[Depends(auth.get_api_key)])
async def merge_view(files: List[UploadFile] = File(...)):
    try:
        with TemporaryDirectory() as td:
            for f in files:
                save_upload_file_tmp(td, f)        

            get_raw_merge_files = list(Path(td).glob('*.*'))

            merged_file = mergePDFs_core(get_raw_merge_files, td)
            
            uploaded_filePath = spaces_upload_file(merged_file, 'merged', '.pdf')
            uploaded_url = spaces_presigned_url(uploaded_filePath)
            print(uploaded_url)

            return uploaded_url

    except Exception as e:
        print(e)
        return {"message": "There was an error uploading the file"}


@app.post("/rotate-pdf", dependencies=[Depends(auth.get_api_key)])
def rotate_pdf_view(rotate: FileAttrib = Depends(), file: UploadFile = File(...)):
    """
    Details needed for rotate-pdf:
    
    rotateby: Should have a value of 90, 180 or 270 only.
    file: a .pdf file.

    """

    formated_original_filename_stem = "".join([x if x.isalnum() else "_" for x in Path(file.filename).stem])
    try:
        with TemporaryDirectory() as td:
            tmp_path, tmp_stem, tmp_suffix = save_upload_file_tmp(td, file)        

            rotate_filePath = rotatePDF_core(tmp_path, td, tmp_suffix, rotate.rotateby)

            uploaded_filePath = spaces_upload_file(rotate_filePath, f'rotated-{formated_original_filename_stem}', tmp_suffix)
            uploaded_url = spaces_presigned_url(uploaded_filePath)

            return uploaded_url
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="There was an error uploading the file")
