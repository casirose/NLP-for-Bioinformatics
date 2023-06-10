



import requests
from collections import defaultdict
import streamlit as st
import pandas as pd
from Bio import Entrez
import numpy as np
import streamlit.components.v1 as components
import networkx as nx
from pyvis.network import Network


paper_id = []
title_list= []
abstract_list=[]
journal_list = []
language_list =[]
pubdate_year_list = []
pubdate_month_list = []
keywords = []

def search(query):

    Entrez.email = 'email@example.com'

    handle = Entrez.esearch(
        db='PubMed',    # The database to search (PubMed)
        sort='relevance',   # Sort the results by relevance (default)
        retmax='250000',    # The maximum number of results to return (default is 20)
        retmode='xml',  # The format of the results (XML)
        term=query  # The search term provided as input to the function
    )

    results = Entrez.read(handle)

    return results

st.title('PubMed Search')
    
# Get the search query from the user
query = st.text_input('Enter a search query', 'COVID-19')



# Create a text component on the left sidebar
with st.sidebar:

    # Display a pink triangle symbol using Unicode entities
    st.write("<span style='color: pink; font-size: 25px;'>&#9658;</span>", unsafe_allow_html=True)
    st.write("Pink Triangle is represents Gene Pathway")
    st.write("<div style='background-color: red; border-radius: 50%; width: 20px; height: 20px;'></div>", unsafe_allow_html=True)
    st.write("Red Circle  represents Diseases")
    # Display a yellow square using HTML and CSS
    st.write("<div style='background-color: yellow; width: 20px; height: 20px;'></div>", unsafe_allow_html=True)
    st.write("Yellow Square  represents Article")

    # Display a white star using HTML and CSS
    st.write("<span style='color: white; font-size: 20px;'>&#9733;</span>", unsafe_allow_html=True)
    st.write("White Star is represents Species")
    st.write("<div style='background-color: green; width: 20px; height: 20px; transform: rotate(45deg);'></div>", unsafe_allow_html=True)
    st.write("Green  Diamond is represents  Chemical")


# Use the Entrez API to search PubMed for the current term
studies = search(query)

# Get the IDs of the studies returned by the search
studiesIdList = studies['IdList']

# Define a function to fetch details for a list of IDs
def fetch_details(id_list):
    # Join the IDs into a comma-separated string
    ids = ','.join(id_list)

    # Use Entrez to fetch the details for the IDs
    Entrez.email = 'email@example.com'
    handle = Entrez.efetch(
        db='pubmed',    # The database to fetch from (PubMed)
        retmode='xml',  # The format of the results (XML)
        id=ids  # The list of IDs to fetch
    )
    results = Entrez.read(handle)
    return results

# Fetch details for the studies returned by the search
studies = fetch_details(studiesIdList)

# Define a chunk size for fetching details in batches
chunk_size = 10000

# Iterate over the IDs in chunks of the specified size
for chunk_i in range(0, len(studiesIdList), chunk_size):

    # Get the current chunk of IDs
    chunk = studiesIdList[chunk_i:chunk_i + chunk_size]

    # Fetch details for the current chunk of IDs
    papers = fetch_details(chunk)

    # Iterate over the papers in the current chunk
    for i, paper in enumerate(papers['PubmedArticle']):

        # Extract various fields from the paper details
        paper_id.append(paper['MedlineCitation']['PMID'])
        title_list.append(paper['MedlineCitation']['Article']['ArticleTitle'])
        st = ''
        ky = ''
        try:
            # Extract the abstract, if present
            Abstract_len = len(paper['MedlineCitation']['Article']['Abstract']['AbstractText'])
            for i in range(Abstract_len):
                st = st + ' ' +paper['MedlineCitation']['Article']['Abstract']['AbstractText'][i]
            abstract_list.append(st)
        except:
            abstract_list.append('No Abstract')
        journal_list.append(paper['MedlineCitation']['Article']['Journal']['Title'])
        language_list.append(paper['MedlineCitation']['Article']['Language'][0])

        try:
            # Extract the keywords, if present
            keyword_len = len(paper['MedlineCitation']['KeywordList'][0])
            for i in range(keyword_len):
                ky = ky + ' ' +paper['MedlineCitation']['KeywordList'][0][i] + ','
            keywords.append(ky)

        except:
            keywords.append(np.nan)

        # Extract the publication date, if present
        try:
            pubdate_year_list.append(paper['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate']['Year'])
        except:
            pubdate_year_list.append(np.nan)
        try:
            pubdate_month_list.append(paper['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate']['Month'])
        except:
            pubdate_month_list.append(np.nan)

df = pd.DataFrame(list(zip(
        paper_id,title_list, abstract_list, journal_list, language_list, pubdate_year_list, pubdate_month_list, keywords
        )), 
        columns=[
             'Paper_ID','Title', 'Abstract', 'Journal', 'Language', 'Year','Month', 'Keywords'
             ])





D_identifier=[]
D_ids=[]
D_typeof=[]
D_text=[]
D_offset=[]
D_length =[]
D_Pmid=[]
D_Pmid_name=[]
S_identifier=[]
S_ids=[]
S_typeof=[]
S_text=[]
S_offset=[]
S_length =[]
S_Pmid=[]
S_Pmid_name=[]
G_identifier=[]
G_ids=[]
G_typeof=[]
G_text=[]
G_offset=[]
G_length =[]
G_Pmid=[]
G_Pmid_name=[]
C_identifier=[]
C_ids=[]
C_typeof=[]
C_text=[]
C_offset=[]
C_length =[]
C_Pmid=[]
C_Pmid_name=[]
O_identifier=[]
O_ids=[]
O_typeof=[]
O_text=[]
O_offset=[]
O_length =[]
O_Pmid=[]
O_Pmid_name=[]
# Create an empty DataFrame with the desired columns
df_pathway = pd.DataFrame(columns=['Pathway_PMID','Pathway_Organism','Pathway_Gene'])



for i in range(0,len(df)):
	pmid = str(df['Paper_ID'][i])

	url ="https://www.ncbi.nlm.nih.gov/research/pubtator-api/publications/export/biocjson?pmids="+pmid
	resp = requests.get(url)

	jsonobj = resp.json()
	jsonobj = [jsonobj]
	pathway_Gene = []
	pathway_PMID = []
	pathway_organism = []
   

	pathway_PMID.append('PMID'+jsonobj[0]['id']) 
	#pathway_organism.append(jsonobj[0]['passages'][1]['annotations'][i]['text'])
	for i in range(0,len(jsonobj[0]['passages'][1]['annotations'])):
		try:
			if jsonobj[0]['passages'][1]['annotations'][i]['infons']['type'] == 'Species':
				try:
					S_Pmid.append('PMID'+jsonobj[0]['id']) 
					S_Pmid_name.append(jsonobj[0]['passages'][0]['text']) 
				except:
					S_Pmid.append(np.nan)
				try:
					S_ids.append(jsonobj[0]['passages'][1]['annotations'][i]['id']) 
				except:
					S_ids.append(np.nan)
				try:
					S_identifier.append(str(jsonobj[0]['passages'][1]['annotations'][i]['infons']['identifier'])) 
				except:
					S_identifier.append(np.nan)
				try:
					S_typeof.append(jsonobj[0]['passages'][1]['annotations'][i]['infons']['type']) 
				except:
					S_typeof.append(np.nan)
				try:
					S_text.append(jsonobj[0]['passages'][1]['annotations'][i]['text'])
					if jsonobj[0]['passages'][1]['annotations'][i]['text'] == "patient" or jsonobj[0]['passages'][1]['annotations'][i]['text'] == "patients" or jsonobj[0]['passages'][1]['annotations'][i]['text'] == "people" or jsonobj[0]['passages'][1]['annotations'][i]['text'] == "human" or jsonobj[0]['passages'][1]['annotations'][i]['text'] == "humans":
						pathway_organism.append("hsapiens")    
					elif jsonobj[0]['passages'][1]['annotations'][i]['text'] == "mouse" or jsonobj[0]['passages'][1]['annotations'][i]['text'] =="transgenic mice" or jsonobj[0]['passages'][1]['annotations'][i]['text'] =="mice" or jsonobj[0]['passages'][1]['annotations'][i]['text'] == "rats":
						pathway_organism.append("mmusculus")
					else:
						pathway_organism.append(jsonobj[0]['passages'][1]['annotations'][i]['text'])
				except:
					S_text.append(np.nan)
				try:
					S_offset.append(jsonobj[0]['passages'][1]['annotations'][i]['locations'][0]['offset']) 
				except:
					S_offset.append(np.nan)
				try:
					S_length.append(jsonobj[0]['passages'][1]['annotations'][i]['locations'][0]['length']) 
				except:
					S_length.append(np.nan)
			elif jsonobj[0]['passages'][1]['annotations'][i]['infons']['type'] == 'Gene':
				try:
					G_Pmid_name.append(jsonobj[0]['passages'][0]['text']) 
					G_Pmid.append('PMID'+jsonobj[0]['id'])
					                  
				except:
					G_Pmid.append(np.nan)
				try:
					G_ids.append(jsonobj[0]['passages'][1]['annotations'][i]['id']) 
				except:
					G_ids.append(np.nan)
				try:
					G_identifier.append(str(jsonobj[0]['passages'][1]['annotations'][i]['infons']['identifier']))
				except:
					G_identifier.append(np.nan)
				try:
					G_typeof.append(jsonobj[0]['passages'][1]['annotations'][i]['infons']['type']) 
				except:
					G_typeof.append(np.nan)
				try:
					G_text.append(jsonobj[0]['passages'][1]['annotations'][i]['text']) 
					                 
					pathway_Gene.append( jsonobj[0]["passages"][1]["annotations"][i]["text"]) 
				except:
					G_text.append(np.nan)
				try:
					G_offset.append(jsonobj[0]['passages'][1]['annotations'][i]['locations'][0]['offset']) 
				except:
					G_offset.append(np.nan)
				try:
					G_length.append(jsonobj[0]['passages'][1]['annotations'][i]['locations'][0]['length']) 
				except:
					G_length.append(np.nan)
			elif jsonobj[0]['passages'][1]['annotations'][i]['infons']['type'] == 'Disease':
				try:
					D_Pmid_name.append(jsonobj[0]['passages'][0]['text']) 
					D_Pmid.append('PMID'+jsonobj[0]['id']) 
				except:
					D_Pmid.append(np.nan)
				try:
					D_ids.append(jsonobj[0]['passages'][1]['annotations'][i]['id']) 
				except:
					D_ids.append(np.nan)
				try:
					D_identifier.append(str(jsonobj[0]['passages'][1]['annotations'][i]['infons']['identifier'])) 
				except:
					D_identifier.append(np.nan)
				try:
					D_typeof.append(jsonobj[0]['passages'][1]['annotations'][i]['infons']['type']) 
				except:
					D_typeof.append(np.nan)
				try:
					D_text.append(jsonobj[0]['passages'][1]['annotations'][i]['text']) 
				except:
					D_text.append(np.nan)
				try:
					D_offset.append(jsonobj[0]['passages'][1]['annotations'][i]['locations'][0]['offset']) 
				except:
					D_offset.append(np.nan)
				try:
					D_length.append(jsonobj[0]['passages'][1]['annotations'][i]['locations'][0]['length']) 
				except:
					D_length.append(np.nan)
			elif jsonobj[0]['passages'][1]['annotations'][i]['infons']['type'] == 'Chemical':
				try:
					C_Pmid_name.append(jsonobj[0]['passages'][0]['text']) 
					C_Pmid.append('PMID'+jsonobj[0]['id']) 
				except:
					C_Pmid.append(np.nan)
				try:
					C_ids.append(jsonobj[0]['passages'][1]['annotations'][i]['id']) 
				except:
					C_ids.append(np.nan)
				try:
					C_identifier.append(str(jsonobj[0]['passages'][1]['annotations'][i]['infons']['identifier'])) 
				except:
					C_identifier.append(np.nan)
				try:
					C_typeof.append(jsonobj[0]['passages'][1]['annotations'][i]['infons']['type']) 
				except:
					C_typeof.append(np.nan)
				try:
					C_text.append(jsonobj[0]['passages'][1]['annotations'][i]['text']) 
				except:
					C_text.append(np.nan)
				try:
					C_offset.append(jsonobj[0]['passages'][1]['annotations'][i]['locations'][0]['offset']) 
				except:
					C_offset.append(np.nan)
				try:
					C_length.append(jsonobj[0]['passages'][1]['annotations'][i]['locations'][0]['length']) 
				except:
					C_length.append(np.nan)
			else:
				try:
					O_Pmid_name.append(jsonobj[0]['passages'][0]['text']) 
					O_Pmid.append('PMID'+jsonobj[0]['id']) 
				except:
					O_Pmid.append(np.nan)
				try:
					O_ids.append(jsonobj[0]['passages'][1]['annotations'][i]['id']) 
				except:
					O_ids.append(np.nan)
				try:
					O_identifier.append(str(jsonobj[0]['passages'][1]['annotations'][i]['infons']['identifier'])) 
				except:
					O_identifier.append(np.nan)
				try:
					O_typeof.append(jsonobj[0]['passages'][1]['annotations'][i]['infons']['type']) 
				except:
					O_typeof.append(np.nan)
				try:
					O_text.append(jsonobj[0]['passages'][1]['annotations'][i]['text']) 
				except:
					O_text.append(np.nan)
				try:
					O_offset.append(jsonobj[0]['passages'][1]['annotations'][i]['locations'][0]['offset']) 
				except:
					O_offset.append(np.nan)
				try:
					O_length.append(jsonobj[0]['passages'][1]['annotations'][i]['locations'][0]['length']) 
				except:
					O_length.append(np.nan)
		except:
			pass
	
	    
	pathway_Gene = list(set(pathway_Gene))
	
	# add a new row to the DataFrame
	new_row = {'Pathway_PMID': pathway_PMID, 'Pathway_Organism': pathway_organism, 'Pathway_Gene': pathway_Gene}
	df_pathway = pd.concat([df_pathway, pd.DataFrame([new_row])], ignore_index=True)


# convert Pathway_PMID and Pathway_Gene columns to lists
df_pathway['Pathway_PMID'] = df_pathway['Pathway_PMID'].apply(lambda x: x[0]) 
# The 'Pathway_PMID' column is converted to a list by taking the first element of each value

df_pathway['Pathway_Gene'] = df_pathway['Pathway_Gene'].apply(lambda x: x) 


# explode Pathway_Organism column
df_pathway = df_pathway.explode('Pathway_Organism').reset_index(drop=True)
# The 'Pathway_Organism' column is exploded, meaning that each row is duplicated for each value in the column.


df_pathway = df_pathway.loc[df_pathway['Pathway_Gene'].apply(len) > 0]
# Rows are filtered based on the length of the values in the 'Pathway_Gene' column.

df_pathway = df_pathway.drop_duplicates(subset=['Pathway_PMID', 'Pathway_Organism'])
# Duplicate rows are removed based on the combination of 'Pathway_PMID' and 'Pathway_Organism'.
# Only the first occurrence of each unique combination is kept.

df_pathway = df_pathway[df_pathway['Pathway_Organism'] != 'adeno-associated virus']
# Rows containing 'adeno-associated virus' in the 'Pathway_Organism' column are removed.




import requests

PMID= []
description = []
effective_domain_size = []
goshv = []
intersection_size = []
intersections = []
name = []
native =[]
p_value=[]
parents = []
precision=[]
query=[]
query_size=[]
recall=[]
significant=[]
source = []
term_size = []
source_order=[]
group_id=[]


# Iterate over each row in the 'df_pathway' DataFrame
for index, row in df_pathway.iterrows():
    organism = row['Pathway_Organism']  # Get the value from 'Pathway_Organism' column
    query = row['Pathway_Gene']  # Get the value from 'Pathway_Gene' column
    pmid = row['Pathway_PMID']  # Get the value from 'Pathway_PMID' column
    
    # Send a POST request to the specified URL with JSON data
    r = requests.post(
        url='https://biit.cs.ut.ee/gprofiler/api/gost/profile/',
        json={
            'organism': organism,
            'query': query,
        }
    )
    
    # Extract and append data from the response to the respective lists
    for i in range(len(r.json()['result'])):
        try:
            description.append(r.json()['result'][i]['description'])
        except:
            description.append(np.nan)
        try:
            effective_domain_size.append(r.json()['result'][i]['effective_domain_size'])
        except:
            effective_domain_size.append(np.nan)
        try:
            goshv.append(r.json()['result'][i]['goshv'])
        except:
            goshv.append(np.nan)    
        try:
            intersection_size.append(r.json()['result'][i]['intersection_size'])
        except:
            intersection_size.append(np.nan)
        try:
            intersections.append(r.json()['result'][i]['intersections'])
        except:
            intersections.append(np.nan)
        try:
            name.append(r.json()['result'][i]['name'])
        except:
            name.append(np.nan)
        try:
            native.append(r.json()['result'][i]['native'])
        except:
            native.append(np.nan)
        try:
            p_value.append(r.json()['result'][i]['p_value'])
        except:
            p_value.append(np.nan)
        try:
            parents.append(r.json()['result'][i]['parents'])
        except:
            parents.append(np.nan)
        try:
            precision.append(r.json()['result'][i]['precision'])
        except:
            precision.append(np.nan)
        try:
            query_size.append(r.json()['result'][i]['query_size'])
        except:
            query_size.append(np.nan)
        try:
            recall.append(r.json()['result'][i]['recall'])
        except:
            recall.append(np.nan)
        try:
            significant.append(r.json()['result'][i]['significant'])
        except:
            significant.append(np.nan)
        try:
            source.append(r.json()['result'][i]['source'])
        except:
            source.append(np.nan)
        try:
            term_size.append(r.json()['result'][i]['term_size'])
        except:
            term_size.append(np.nan)
        try:
            source_order.append(r.json()['result'][i]['source_order'])
        except:
            source_order.append(np.nan)
        try:
            group_id.append(r.json()['result'][i]['group_id'])
        except:
            group_id.append(np.nan)
        
        PMID.append(row['Pathway_PMID'])  # Append the 'Pathway_PMID' value to the PMID list


# Create a DataFrame 'path_way' using the collected data
path_way = pd.DataFrame(
    list(zip(PMID, description, effective_domain_size, goshv, intersection_size, intersections, name, native,
             p_value, parents, precision, query_size, recall, significant, source, term_size, source_order, group_id)),
    columns=[
        'PMID', 'Description', 'Effective_domain_size', 'Goshv', 'Intersection_size', 'Intersections', 'Name',
        'Native', 'P_value', 'Parents', 'Precision', 'Query_size', 'Recall', 'Significant', 'Source', 'Term_size',
        'Source_order', 'Group_id'
    ]
)

# Create DataFrames for different entities: df_Other, df_Gen, df_Dis, df_Spe, df_Che
df_Other = pd.DataFrame(
    list(zip(O_Pmid, O_Pmid_name, O_ids, O_identifier, O_typeof, O_text, O_offset, O_length)),
    columns=['PMID', 'Paper', 'ID', 'Identifier', 'Type', 'Text', 'Offset', 'Length']
)

df_Gen = pd.DataFrame(
    list(zip(G_Pmid, G_Pmid_name, G_ids, G_identifier, G_typeof, G_text, G_offset, G_length)),
    columns=['PMID', 'Paper', 'ID', 'Identifier', 'Type', 'Text', 'Offset', 'Length']
)

df_Dis = pd.DataFrame(
    list(zip(D_Pmid, D_Pmid_name, D_ids, D_identifier, D_typeof, D_text, D_offset, D_length)),
    columns=['PMID', 'Paper', 'ID', 'Identifier', 'Type', 'Text', 'Offset', 'Length']
)

df_Spe = pd.DataFrame(
    list(zip(S_Pmid, S_Pmid_name, S_ids, S_identifier, S_typeof, S_text, S_offset, S_length)),
    columns=['PMID', 'Paper', 'ID', 'Identifier', 'Type', 'Text', 'Offset', 'Length']
)

df_Che = pd.DataFrame(
    list(zip(C_Pmid, C_Pmid_name, C_ids, C_identifier, C_typeof, C_text, C_offset, C_length)),
    columns=['PMID', 'Paper', 'ID', 'Identifier', 'Type', 'Text', 'Offset', 'Length']
)

# Capitalize the 'Text' column in df_Dis
df_Dis['Text'] = df_Dis['Text'].str.title()

# Iterate over each row in df_Dis
for i in range(len(df_Dis)):
    if df_Dis['Identifier'][i] == "None":
        # If the 'Identifier' column value is "None", replace it with the corresponding value from the 'Text' column
        df_Dis.loc[i, 'Identifier'] = df_Dis.loc[i, 'Text']


# Create a network visualization object with specified attributes
pub_net = Network(height='1200px', cdn_resources="remote", width='100%', bgcolor='#000000', font_color='black',
                  select_menu=True, filter_menu=True)

# Extract data for diseases from df_Dis DataFrame
disease_mesh = df_Dis['Identifier']
disease_pmid = df_Dis['PMID']
disease_type = df_Dis['Type']
disease_text = df_Dis['Text']
disease_paper = df_Dis['Paper']

# Zip the disease data together as edge_data
edge_data = zip(disease_mesh, disease_pmid, disease_type, disease_text, disease_paper)

# Iterate over each entry in edge_data
for e in edge_data:
    src = e[0]
    dst = e[1]
    w = e[2]
    txt = e[3]
    P_txt = e[4]

    # Add nodes and edges to the network visualization object for diseases
    pub_net.add_node(str(src), label=src, text=txt, type=w, color="red", size=125)
    pub_net.add_node(str(dst), label=dst, text=P_txt, title=dst, color='yellow', shape='square', size=125)
    pub_net.add_edge(str(src), str(dst), label='Disease', value=w, color='red', width=125)

# Get the adjacency list of the network
neighbor_map = pub_net.get_adj_list()

# Update the node attributes with titles and values based on neighbors
for node in pub_net.nodes:
    node_text = node['text']
    if 'title' in node:
        node['title'] += ' Title: ' + node_text + '\n' + ' Neighbors: ' + ','.join(neighbor_map[node['id']])
    else:
        node['title'] = 'Title: ' + node_text + '\n' + ' Neighbors: ' + ','.join(neighbor_map[node['id']])
    node['value'] = len(neighbor_map[node['id']])

# Extract data for species from df_Spe DataFrame
Species_mesh = df_Spe['Identifier']
Species_pmid = df_Spe['PMID']
Species_type = df_Spe['Type']
Species_text = df_Spe['Text']
Species_Paper = df_Spe['Paper']

# Zip the species data together as edge_data
edge_data = zip(Species_mesh, Species_pmid, Species_type, Species_text, Species_Paper)

# Iterate over each entry in edge_data
for e in edge_data:
    src = e[0]
    dst = e[1]
    w = e[2]
    txt = e[3]
    p_txt = e[4]

    # Add nodes and edges to the network visualization object for species
    pub_net.add_node(src, label=str(src), text=txt, type=w, size=125, color='white', shape='star')
    pub_net.add_node(dst, label=dst, text=p_txt, color='yellow', shape='square', size=125)
    pub_net.add_edge(src, dst, value=w, label="Species", color='white', width=125)


# Get the adjacency list of the network
neighbor_map = pub_net.get_adj_list()

# Update the node attributes with titles and values based on neighbors
for node in pub_net.nodes:
    node_text = node['text']
    if 'title' in node:
        node['title'] += ' Title: ' + node_text + '\n' + ' Neighbors: '
    else:
        node['title'] = 'Title: ' + node_text + '\n' + ' Neighbors: '
    node['value'] = len(neighbor_map[node['id']])

# Extract data for pathways from path_way DataFrame
pathway_native = path_way['Native']
pathway_pmid = path_way['PMID']
pathway_description = path_way['Description']
pathway_name = path_way['Name']
pathway_parents = path_way['Parents']

# Zip the pathway data together as edge_data
edge_data = zip(pathway_native, pathway_pmid, pathway_description, pathway_name, pathway_parents)

# Iterate over each entry in edge_data
for e in edge_data:
    src = e[0]
    dst = e[1]
    w = e[2]
    txt = e[3]
    p_txt = e[4]

    # Add nodes and edges to the network visualization object for pathways
    pub_net.add_node(src, label=str(src), text=txt, type=w, size=125, color="Pink", shape='triangle', physics=False)
    pub_net.add_node(dst, label=dst, text=p_txt, color='yellow', shape='square', size=125)
    pub_net.add_edge(src, dst, value=w, label="Pathway", color='Orange', width=125)

# Get the updated adjacency list of the network
neighbor_map = pub_net.get_adj_list()


# Update node attributes with titles and values based on neighbors
for node in pub_net.nodes:
    node_text = node['text']
    if 'title' in node:
        node['title'] += ' Title: ' + node_text + ' Neighbors: '
    else:
        node['title'] = 'Title: ' + node_text + ' Neighbors: '
    node['value'] = len(neighbor_map[node['id']])

# Extract data for chemicals from df_Che DataFrame
Che_mesh = df_Che['Identifier']
Che_pmid = df_Che['PMID']
Che_type = df_Che['Type']
Che_text = df_Che['Text']
Che_Paper = df_Che['Paper']

# Zip the chemical data together as edge_data
edge_data = zip(Che_mesh, Che_pmid, Che_type, Che_text, Che_Paper)

# Iterate over each entry in edge_data
for e in edge_data:
    src = e[0]
    dst = e[1]
    w = e[2]
    txt = e[3]
    p_txt = e[4]

    # Add nodes and edges to the network visualization object for chemicals
    pub_net.add_node(src, label=str(src), text=txt, type=w, size=125, color="Green", shape='diamond')
    pub_net.add_node(dst, label=dst, text=p_txt, color='yellow', shape='square', size=125)
    pub_net.add_edge(src, dst, value=w, label="Chemical", color='#FFFF00', width=125)

# Get the updated adjacency list of the network
neighbor_map = pub_net.get_adj_list()

# Update node attributes with titles and values based on neighbors again
for node in pub_net.nodes:
    node_text = node['text']
    if 'title' in node:
        node['title'] += ' Title: ' + node_text + '\n' + ' Neighbors: '
    else:
        node['title'] = 'Title: ' + node_text + '\n ' + ' Neighbors: '
    node['value'] = len(neighbor_map[node['id']])

# Perform the Barnes-Hut algorithm for layout
pub_net.barnes_hut(
    gravity=-2000,
    central_gravity=0,
    spring_length=2,
    spring_strength=0.001,
    damping=0.09,
    overlap=0
)

# Save the graph as an HTML file
pub_net.save_graph("Pubmedst.html")

# Open and display the HTML file in the notebook
HtmlFile = open('Pubmedst.html', 'r', encoding='utf-8')
components.html(HtmlFile.read(), height=1200, width=1000)

























