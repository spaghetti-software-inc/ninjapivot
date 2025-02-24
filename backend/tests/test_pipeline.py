import pandas as pd

import ninjapivot as ninja



def test_pdf_gen():
    df = pd.read_csv('data/iris.csv')
    job_id = 'test'
    pdf_path = ninja.gen_latex_document(job_id, df)
    
    assert pdf_path.exists()
    assert pdf_path.suffix == '.pdf'
    assert pdf_path.parent.name == job_id
    assert pdf_path.parent.exists()
    assert pdf_path.parent.is_dir()
    assert pdf_path.name == 'main.pdf'
    assert pdf_path.is_file()
    assert pdf_path.stat().st_size > 0