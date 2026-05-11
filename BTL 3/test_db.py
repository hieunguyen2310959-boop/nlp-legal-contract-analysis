import chromadb

client = chromadb.PersistentClient(path='./chroma_db')
coll = client.get_collection('legal_clauses')
print('Total documents:', coll.count())

results = coll.query(
    query_texts=['Bên B phải thanh toán trong bao lâu?'], 
    n_results=3
)

print('\nTop 3 kết quả cho query "Bên B phải thanh toán trong bao lâu?"')
for i, (doc, meta, dist) in enumerate(zip(results['documents'][0], results['metadatas'][0], results['distances'][0]), 1):
    print(f'{i}. (line {meta["line"]}, intent={meta["intent"]}, dist={dist:.3f})')
    print(f'   {doc[:80]}...')
