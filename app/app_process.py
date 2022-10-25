from fastapi import FastAPI, Depends, File, UploadFile, Form, Request, HTTPException
import shutil, pdb
from pikepdf import Pdf
from tempfile import NamedTemporaryFile
from pathlib import Path


def rotatePDF_core(tmp_path, td, tmp_suffix, rotateby_Degree):

    tmp_save = NamedTemporaryFile(dir=td, delete=False, prefix='rotate-', suffix=tmp_suffix)

    try:
        with Pdf.open(tmp_path) as pdf:
            for page in pdf.pages:
                page.Rotate = rotateby_Degree
            pdf.save(tmp_save.name)
        return tmp_save.name

    except Exception as e:
        print(e)
        detail="error: rotating the file"
        return detail

def mergePDFs_core(rawfile_Path_List, td):

    tmp_save = NamedTemporaryFile(dir=td, delete=False, prefix='merged-', suffix='.pdf')

    try:
        pdf = Pdf.new()

        for file in rawfile_Path_List:
            src = Pdf.open(file)
            pdf.pages.extend(src.pages)
        pdf.save(tmp_save.name)
        pdf.close()
        
        return tmp_save.name

    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="error: merging the file")

def save_upload_file_tmp(td, upload_file: UploadFile) -> Path:
    try:
        p = Path(upload_file.filename)
        with NamedTemporaryFile(dir=td,delete=False, suffix=p.suffix) as tmp:
            shutil.copyfileobj(upload_file.file, tmp)
            tmp_path = Path(tmp.name)
            #print(f'1 - {tmp_path}')
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="error: saving tmp file")
    finally:
        upload_file.file.close()
    return tmp_path, p.stem, p.suffix
