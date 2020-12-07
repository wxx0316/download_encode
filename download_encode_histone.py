import requests, json
import pandas as pd
import os
from urllib.parse import urlparse

def getUrl(sample,assay_title,status="released",perturbed="false",biosample_ontology_classification="cell%20line"):
    #url_histone = "https://www.encodeproject.org/search/?type=Experiment&status=released&perturbed=false&biosample_ontology.term_name=GM12878&assay_title=Histone+ChIP-seq&biosample_ontology.classification=cell%20line"
    url = "https://www.encodeproject.org/metadata/?type=Experiment&status=" + status + \
        "&perturbed=" + perturbed + \
        "&biosample_ontology.term_name=" + sample + \
        "&assay_title=" + assay_title + \
        "&biosample_ontology.classification=" + biosample_ontology_classification
    
    return url

def file_filter(input_file, fileType=None,fileFormatTpye=None,outoutType=None,
               assembly=None, assay=None, sample=None, organism=None,
               treatment=None, target=None, BioRep=None, TechRep=None):
    table = pd.read_csv(input_file, sep='\t')
    
    print("Before fileter.")
    print(table.pivot_table(index=["Biological replicate(s)", "Technical replicate(s)"], aggfunc='size'))
    
    #filter
    if fileType!=None:
        table = table[table['File type'].isin(fileType)]
    if fileFormatTpye!=None:
        table = table[table['File format type'].isin(fileFormatTpye)]
    if outoutType!=None:
        table = table[table['Output type'].isin(outoutType)]
    if assembly!=None:
        table = table[table['File assembly'].isin(assembly)]
    if assay!=None:
        table = table[table['Assay'].isin(assay)]
    if sample!=None:
        table = table[table['Biosample term name'].isin(sample)]
    if organism!=None:
        table = table[table['Biosample organism'].isin(organism)]
    if treatment!=None:
        table = table[table['Biosample treatments'].isin(treatment)]
    if target!=None:
        table = table[table['Experiment target'].isin(target)]
    if BioRep!=None:
        table = table[table['Biological replicate(s)'].isin(BioRep)]
    if TechRep!=None:
        table = table[table['Technical replicate(s)'].isin(TechRep)]
    
    print("After fileter.")
    print(table.pivot_table(index=["Biological replicate(s)", "Technical replicate(s)"], aggfunc='size'))
    
    return table

def main(sample, output_dir):
    print("Begin download for cell line: " + sample + " .")
    
    data_url = getUrl(sample, "Histone+ChIP-seq")
    #output_dir = "/usr0/home/yuchuanw/1_Project/0_data/2_ENCODE/histone_human/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open(output_dir+"files.txt", "w") as text_file:
        text_file.write("\"" + data_url + "\"")
    
    # use system commands
    output_metadata = output_dir + "metadata.tsv"
    os.system("xargs -L 1 curl -o " + output_metadata + " -J -L < " + output_dir + "files.txt")
    
    # filter 
    fileTypeList = ['bigBed', 'bigWig']
    assemblyList = ['GRCh38']
    outoutTypeList = ['signal p-value', 'fold change over control', 'replicated peaks']
    BioRepList = ["1, 2"]

    table_filter = file_filter(output_metadata, fileType = fileTypeList, 
        outoutType = outoutTypeList, assembly = assemblyList,
        BioRep = BioRepList
    )
    
    print("Begin download files.")
    for url in table_filter['File download URL']:
        url_parse = urlparse(url)
        file_name = os.path.basename(url_parse.path)
        print(url)
        print(file_name)
        os.system("wget -O " + output_dir + file_name + " " + url)
    
    print("Finished.")
    