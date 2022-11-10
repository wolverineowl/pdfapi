from fastapi import Request,FastAPI, Depends, File, UploadFile, HTTPException, Body
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

# @app.post("/dummypath")
# async def get_body(request: Request):
#     pdb.set_trace()
#     return request.json()

@app.post('/test')
async def update_item(payload: dict = Body(...)):
    pdb.set_trace()
    return payload

#@app.post("/merge-pdf", dependencies=[Depends(auth.get_api_key)])
@app.post("/merge-pdf")
async def merge_pdf_view(files: List[UploadFile] = File(...)):
    try:
        with TemporaryDirectory() as td:
            for f in files:
                save_upload_file_tmp(td, f)        

            get_raw_merge_files = list(Path(td).glob('*.*'))

            merged_file = mergePDFs_process(get_raw_merge_files, td)
            
            uploaded_filePath = spaces_upload_file(merged_file, 'merged', '.pdf')
            uploaded_url = spaces_presigned_url(uploaded_filePath)
            print(uploaded_url)

            return uploaded_url

    except Exception as e:
        print(e)
        return {"message": "There was an error merging pdf files"}


#@app.post("/rotate-pdf", dependencies=[Depends(auth.get_api_key)]) # Injects a dependency to check auth
#async def rotate_pdf_view(rotate: int, file: UploadFile = File(...)): # rotate: int, creates a query parameter.
@app.post("/rotate-pdf")
async def rotate_pdf_view(rotateby = Body(...), file: UploadFile = File(...)): # Takes a Body parameter of rotate.
    """
    Details needed for rotate-pdf:
    
    rotateby: Should have a value of 90, 180 or 270 only.
    file: a .pdf file.

    """
    formated_original_filename_stem = "".join([x if x.isalnum() else "_" for x in Path(file.filename).stem])
    try:
        with TemporaryDirectory() as td:
            tmp_path, tmp_stem, tmp_suffix = save_upload_file_tmp(td, file)        

            rotate_filePath = rotatePDF_process(tmp_path, td, tmp_suffix, int(rotateby))

            uploaded_filePath = spaces_upload_file(rotate_filePath, f'rotated-{formated_original_filename_stem}', tmp_suffix)
            uploaded_url = spaces_presigned_url(uploaded_filePath)

            return uploaded_url
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="There was an error rotating the pdf file")

@app.post("/protect-pdf")
async def protect_pdf_view(protectpassword = Body(), file: UploadFile = File(...)):
    """
    Details needed for protect-pdf:
    
    protectpassword: password
    file: a .pdf file.

    """
    formated_original_filename_stem = "".join([x if x.isalnum() else "_" for x in Path(file.filename).stem])
    try:
        with TemporaryDirectory() as td:
            tmp_path, tmp_stem, tmp_suffix = save_upload_file_tmp(td, file)        

            protected_filePath = protectPDF_process(tmp_path, td, tmp_suffix, protectpassword)

            uploaded_filePath = spaces_upload_file(protected_filePath, f'protected-{formated_original_filename_stem}', tmp_suffix)
            uploaded_url = spaces_presigned_url(uploaded_filePath)

            return uploaded_url
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="There was an error protecting the pdf file")


@app.post("/unlock-pdf")
async def unlock_pdf_view(unlockpassword = Body(), file: UploadFile = File(...)):
    """
    Details needed for unlock-pdf:
    
    unlockpassword: password
    file: a .pdf file.

    """
    formated_original_filename_stem = "".join([x if x.isalnum() else "_" for x in Path(file.filename).stem])
    try:
        with TemporaryDirectory() as td:
            tmp_path, tmp_stem, tmp_suffix = save_upload_file_tmp(td, file)        

            protected_filePath = unlockPDF_process(tmp_path, td, tmp_suffix, unlockpassword)

            uploaded_filePath = spaces_upload_file(protected_filePath, f'unlocked-{formated_original_filename_stem}', tmp_suffix)
            uploaded_url = spaces_presigned_url(uploaded_filePath)

            return uploaded_url
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="There was an error unlocking the pdf file")


@app.post("/reverse-pdf")
async def reverse_pdf_view(file: UploadFile = File(...)):
    """
    Details needed for reverse-pdf:

    file: a .pdf file.

    """
    formated_original_filename_stem = "".join([x if x.isalnum() else "_" for x in Path(file.filename).stem])
    try:
        with TemporaryDirectory() as td:
            tmp_path, tmp_stem, tmp_suffix = save_upload_file_tmp(td, file)        

            protected_filePath = reversePDF_process(tmp_path, td, tmp_suffix)
            #pdb.set_trace()
            uploaded_filePath = spaces_upload_file(protected_filePath, f'reverse-{formated_original_filename_stem}', tmp_suffix)
            uploaded_url = spaces_presigned_url(uploaded_filePath)

            return uploaded_url
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="There was an error reversing the pdf file")

"""Windows only features"""

@app.post("/word-pdf")
async def word_pdf_view(file: UploadFile = File(...)): # Only docx
    """
    Details needed for word-pdf:

    file: a .doc or .docx file.

    """
    #pdb.set_trace()
    formated_original_filename_stem = "".join([x if x.isalnum() else "_" for x in Path(file.filename).stem])
    try:
        with TemporaryDirectory() as td:
            tmp_path, tmp_stem, tmp_suffix = save_upload_file_tmp(td, file)        

            converted_filePath = wordToPDF_process(tmp_path, td)
            #pdb.set_trace()
            uploaded_filePath = spaces_upload_file(str(converted_filePath), f'{formated_original_filename_stem}', '.pdf')
            uploaded_url = spaces_presigned_url(uploaded_filePath)

            return uploaded_url
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="There was an error converting word to pdf")


@app.post("/delete-pdf")
async def delete_pdf_view(pages = Body(), file: UploadFile = File(...)):
    """
    Details needed for delete-pdf:
    
    pages:
        1) Single input
        2) "Should" be a comma seperated multiple page numbers. ex: 3,5,8,12, 14, 23
        3) And multiple ranges. 3-9, 12-19. '-' dash is a must.
        example input: '1, 3-7,11, 22, 14, 9, 73-99, 65, 42-47' - this is a valid combo.
    file: a .pdf file.

    """
    formated_original_filename_stem = "".join([x if x.isalnum() else "_" for x in Path(file.filename).stem])
    try:
        with TemporaryDirectory() as td:
            tmp_path, tmp_stem, tmp_suffix = save_upload_file_tmp(td, file)        

            deleted_filePath = deletePDF_process(tmp_path, pages)

            uploaded_filePath = spaces_upload_file(str(deleted_filePath), f'deleted-{formated_original_filename_stem}', '.pdf')
            uploaded_url = spaces_presigned_url(uploaded_filePath)

            return uploaded_url
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="There was an error deleting pages from the file")


@app.post("/extract-pdf")
async def extract_pdf_view(pages = Body(), file: UploadFile = File(...)):
    """
    Details needed for delete-pdf:
    
    pages:
        1) Single input
        2) "Should" be a comma seperated multiple page numbers. ex: 3,5,8,12, 14, 23
        3) And multiple ranges. 3-9, 12-19. '-' dash is a must.
        example input: '1, 3-7,11, 22, 14, 9, 73-99, 65, 42-47' - this is a valid combo.
    file: a .pdf file.

    """
    formated_original_filename_stem = "".join([x if x.isalnum() else "_" for x in Path(file.filename).stem])
    try:
        with TemporaryDirectory() as td:
            tmp_path, tmp_stem, tmp_suffix = save_upload_file_tmp(td, file)        

            deleted_filePath = extractPDF_process(tmp_path, pages)

            uploaded_filePath = spaces_upload_file(str(deleted_filePath), f'extract-{formated_original_filename_stem}', '.pdf')
            uploaded_url = spaces_presigned_url(uploaded_filePath)

            return uploaded_url
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="There was an error extracting the pages from pdf file")

@app.post("/jpg-pdf")
async def jpgtopdf_view(files: List[UploadFile] = File(...)):
    try:
        with TemporaryDirectory() as td:
            for f in files:
                save_upload_file_tmp(td, f)        

            #get_raw_merge_files = list(Path(td).glob('*.*'))

            converted_jpgtopdf = mergePDFs_process(td)
            
            uploaded_filePath = spaces_upload_file(converted_jpgtopdf, 'jpgtopdf', '.pdf')
            uploaded_url = spaces_presigned_url(uploaded_filePath)
            print(uploaded_url)

            return uploaded_url

    except Exception as e:
        print(e)
        return {"message": "There was an error merging pdf files"}