import chromadb

client = chromadb.PersistentClient()
collection = client.get_or_create_collection('test')

def addMaterial(material):
    if material['material_type'] == 'image' or material['material_type'] == 'pdf_file':
        sts = [s['words'] for s in material['material_info']]
        ids = [f'VEC_{material["file_id"]}_{material["material_id"]}_{idx}' for idx, s in enumerate(sts)]
        meta = [{
            'source': f'{material["file_id"]}_{material["material_id"]}'
        } for _ in ids]
    collection.add(
        documents=sts,
        ids=ids,
        metadatas=meta
    )
    print(sts, ids)

def query_by_metadata(text, metadata_key, metadata_value, top_n=5):
    # 查询集合
    print(metadata_value)
    results = collection.query(
        query_texts=[text],
        where={metadata_key: {
            "$in": metadata_value
        }},
        n_results=top_n,
    )
    print(results)
    # 返回查询结果

    return results
