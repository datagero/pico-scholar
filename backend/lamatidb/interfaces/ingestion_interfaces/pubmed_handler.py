import xml.etree.ElementTree as ET
import requests

class PubMedHandler:
    def fetch_pubmed_data_entrez(self, pmids):
        pmid_string = ",".join(pmids)
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid_string}&rettype=xml&retmode=text"
        
        response = requests.get(url)
        if response.status_code != 200:
            return f"Error: {response.status_code}"
        
        results = []
        root = ET.fromstring(response.content)
        for article in root.findall(".//PubmedArticle"):
            pmid = article.find(".//PMID").text
            title = article.find(".//ArticleTitle").text
            abstract = article.find(".//AbstractText").text if article.find(".//AbstractText") is not None else ""
            pub_year = article.find(".//PubDate/Year")
            pub_year = pub_year.text if pub_year is not None else "Unknown"
            
            authors = []
            for author in article.findall(".//Author"):
                fore_name = author.find("ForeName")
                last_name = author.find("LastName")
                if fore_name is not None and last_name is not None:
                    authors.append(f"{fore_name.text} {last_name.text}")
            
            results.append({
                "PMID": pmid,
                "Title": title,
                "Authors": ", ".join(authors),
                "Abstract": abstract,
                "Publication Year": pub_year
            })
        
        return results