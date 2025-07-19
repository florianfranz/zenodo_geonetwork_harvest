import requests
import xml.etree.ElementTree as ET
from xml.dom import minidom
import html
import re


def clean_html_content(text):
    if not text:
        return ""

    text = html.unescape(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    return text


zenodo_id = "15396265" #Example with the Palaeogeographic Maps PANALESIS recor
zenodo_url = f"https://zenodo.org/api/records/{zenodo_id}"

response = requests.get(zenodo_url)
metadata = response.json()

title = metadata["metadata"].get("title", "")
creators = metadata["metadata"].get("creators", [])
description = metadata["metadata"].get("description", "")
doi = metadata["metadata"].get("doi", "")
pub_date = metadata["metadata"].get("publication_date", "")

clean_description = clean_html_content(description)

gmd = "http://www.isotc211.org/2005/gmd"
gco = "http://www.isotc211.org/2005/gco"
ET.register_namespace("gmd", gmd)
ET.register_namespace("gco", gco)

root = ET.Element(f"{{{gmd}}}MD_Metadata")

fid = ET.SubElement(root, f"{{{gmd}}}fileIdentifier")
ET.SubElement(fid, f"{{{gco}}}CharacterString").text = doi or f"https://zenodo.org/record/{zenodo_id}"

ident_info = ET.SubElement(root, f"{{{gmd}}}identificationInfo")
data_id = ET.SubElement(ident_info, f"{{{gmd}}}MD_DataIdentification")

citation = ET.SubElement(data_id, f"{{{gmd}}}citation")
ci_citation = ET.SubElement(citation, f"{{{gmd}}}CI_Citation")
title_el = ET.SubElement(ci_citation, f"{{{gmd}}}title")
ET.SubElement(title_el, f"{{{gco}}}CharacterString").text = title

date_el = ET.SubElement(ci_citation, f"{{{gmd}}}date")
ci_date = ET.SubElement(date_el, f"{{{gmd}}}CI_Date")
ET.SubElement(ET.SubElement(ci_date, f"{{{gmd}}}date"), f"{{{gco}}}Date").text = pub_date
ET.SubElement(ET.SubElement(ci_date, f"{{{gmd}}}dateType"), f"{{{gmd}}}CI_DateTypeCode", {
    "codeList": "http://www.isotc211.org/2005/resources/codeList.xml#CI_DateTypeCode",
    "codeListValue": "publication"
}).text = "publication"

abstract = ET.SubElement(data_id, f"{{{gmd}}}abstract")
ET.SubElement(abstract, f"{{{gco}}}CharacterString").text = clean_description

for creator in creators:
    poc = ET.SubElement(data_id, f"{{{gmd}}}pointOfContact")
    rp = ET.SubElement(poc, f"{{{gmd}}}CI_ResponsibleParty")
    ET.SubElement(ET.SubElement(rp, f"{{{gmd}}}individualName"), f"{{{gco}}}CharacterString").text = creator.get("name",
                                                                                                                 "")
    ET.SubElement(ET.SubElement(rp, f"{{{gmd}}}role"), f"{{{gmd}}}CI_RoleCode", {
        "codeList": "http://www.isotc211.org/2005/resources/codeList.xml#CI_RoleCode",
        "codeListValue": "author"
    }).text = "author"

ref_sys = ET.SubElement(root, f"{{{gmd}}}referenceSystemInfo")
md_ref_sys = ET.SubElement(ref_sys, f"{{{gmd}}}MD_ReferenceSystem")
ref_id = ET.SubElement(md_ref_sys, f"{{{gmd}}}referenceSystemIdentifier")
rs_id = ET.SubElement(ref_id, f"{{{gmd}}}RS_Identifier")
ET.SubElement(ET.SubElement(rs_id, f"{{{gmd}}}code"), f"{{{gco}}}CharacterString").text = "ESRI:54034"
ET.SubElement(ET.SubElement(rs_id, f"{{{gmd}}}codeSpace"), f"{{{gco}}}CharacterString").text = "ESRI"

extent = ET.SubElement(data_id, f"{{{gmd}}}extent")
ex_extent = ET.SubElement(extent, f"{{{gmd}}}EX_Extent")
geo_el = ET.SubElement(ex_extent, f"{{{gmd}}}geographicElement")
bbox = ET.SubElement(geo_el, f"{{{gmd}}}EX_GeographicBoundingBox")
ET.SubElement(ET.SubElement(bbox, f"{{{gmd}}}westBoundLongitude"), f"{{{gco}}}Decimal").text = "-20037508.34"
ET.SubElement(ET.SubElement(bbox, f"{{{gmd}}}eastBoundLongitude"), f"{{{gco}}}Decimal").text = "20037508.34"
ET.SubElement(ET.SubElement(bbox, f"{{{gmd}}}southBoundLatitude"), f"{{{gco}}}Decimal").text = "-6363885.33"
ET.SubElement(ET.SubElement(bbox, f"{{{gmd}}}northBoundLatitude"), f"{{{gco}}}Decimal").text = "6363885.33"

xml_str = ET.tostring(root, encoding="utf-8")
pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")
with open(f"zenodo_metadata_{zenodo_id}.xml", "w", encoding="utf-8") as f:
    f.write(pretty_xml)

print(f"Metadata saved to zenodo_metadata_{zenodo_id}.xml")
print(f"Cleaned abstract preview: {clean_description[:200]}...")