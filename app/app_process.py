from fastapi import FastAPI, Depends, File, UploadFile, Form, Request, HTTPException
import shutil, pdb
from pikepdf import Pdf, Encryption
import pikepdf
from tempfile import NamedTemporaryFile
from pathlib import Path
from docx2pdf import convert
import fitz

def rotatePDF_process(tmp_path, td, tmp_suffix, rotateby_Degree):
    tmp_save = NamedTemporaryFile(dir=td, delete=False, prefix='rotate-', suffix=tmp_suffix)
    try:
        with Pdf.open(tmp_path) as pdffile:
            for page in pdffile.pages:
                page.Rotate = rotateby_Degree
            pdffile.save(tmp_save.name)
        return tmp_save.name
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="There was an error rotating the file")

def protectPDF_process(tmp_path, td, tmp_suffix, protectpassword):

    tmp_save = NamedTemporaryFile(dir=td, delete=False, prefix='protected-', suffix=tmp_suffix) 
    try:
        with Pdf.open(tmp_path) as pdffile:
            #pdb.set_trace()
            pdffile.save(tmp_save.name, encryption=pikepdf.Encryption(owner=protectpassword, user=protectpassword, R=4))
        return tmp_save.name
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="There was an error protecting the file")

def unlockPDF_process(tmp_path, td, tmp_suffix, unlockpassword):

    tmp_save = NamedTemporaryFile(dir=td, delete=False, prefix='unlocked-', suffix=tmp_suffix) 
    try:
        with Pdf.open(tmp_path, password=unlockpassword) as pdffile:
            pdffile.save(tmp_save.name)
        return tmp_save.name
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="There was an error protecting the file")

def reversePDF_process(tmp_path, td, tmp_suffix):

    tmp_save = NamedTemporaryFile(dir=td, delete=False, prefix='reversed-', suffix=tmp_suffix) 
    try:
        with Pdf.open(tmp_path) as pdffile:
            pdffile.pages.reverse()
            pdffile.save(tmp_save.name)
        return tmp_save.name
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="There was an error protecting the file")

def wordToPDF_process(tmp_path, td):
    t_path=Path(tmp_path)
    #tmp_save = NamedTemporaryFile(dir=td, delete=False, prefix='reversed-', suffix='.pdf') 
    try:
        convert(t_path.parent)
        pdb.set_trace()
        converted_filepath = list(Path(t_path.parent).glob('*.pdf'))

        return converted_filepath[0]
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="There was an error protecting the file")

def deletePDF_process(tmp_path, pages):

    t_path=Path(tmp_path)
    save_path = Path.joinpath(t_path.parent, "deleted.pdf")
    try:
        page_list = formated_pages_list(pages)

        with fitz.open(tmp_path) as file_handle:
            file_handle.delete_pages(page_list)
            file_handle.save(save_path, garbage=3, deflate=True)

        return save_path
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="There was an error protecting the file")

def extractPDF_process(tmp_path, pages):

    t_path=Path(tmp_path)
    save_path = Path.joinpath(t_path.parent, "extracted.pdf")
    try:
        page_list = formated_pages_list(pages)

        with fitz.open(tmp_path) as file_handle:
            file_handle.select(page_list)
            file_handle.save(save_path, garbage=3, deflate=True)

        return save_path
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="There was an error protecting the file")

def mergePDFs_process(rawfile_Path_List, td):

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
        raise HTTPException(status_code=404, detail="There was an error merging the file")

def save_upload_file_tmp(td, upload_file: UploadFile) -> Path:

    try:
        p = Path(upload_file.filename)
        with NamedTemporaryFile(dir=td,delete=False, suffix=p.suffix) as tmp:
            shutil.copyfileobj(upload_file.file, tmp)
            tmp_path = Path(tmp.name)
        return tmp_path, p.stem, p.suffix
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="There was an error saving the file")
    finally:
        upload_file.file.close()   

def formated_pages_list(pages):
    """Used for Delete and Extract PDF features.
        Taskes user provided pages, and returns a list of generated numbers.
    """
    formatted_page_numbers = pages.replace(" ", "").split(',')
    num_list = []

    for x in formatted_page_numbers:
        if '-' in x:
            while True:
                try:
                    num1 = int(x.split("-")[0])
                    num2 = int(x.split("-")[1])

                    for i in range(num1+1, num2): # iterate over the range between first number and second number. Add 1 to num1 so that num1 is not included in list
                        num_list.append(i) 
                    break
                except:
                    print("Input must be a number. Try again.")
        if not '-' in x:
            num_list.append(int(x)-1)
    num_list.sort()
    return num_list