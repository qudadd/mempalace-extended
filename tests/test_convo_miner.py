import os
import tempfile
import shutil
import time
import gc
import chromadb
from mempalace.convo_miner import mine_convos


def test_convo_mining():
    tmpdir = tempfile.mkdtemp()
    with open(os.path.join(tmpdir, "chat.txt"), "w") as f:
        f.write(
            "> What is memory?\nMemory is persistence.\n\n> Why does it matter?\nIt enables continuity.\n\n> How do we build it?\nWith structured storage.\n"
        )

    palace_path = os.path.join(tmpdir, "palace")
    mine_convos(tmpdir, palace_path, wing="test_convos")

    client = chromadb.PersistentClient(path=palace_path)
    col = client.get_collection("mempalace_drawers")
    assert col.count() >= 2

    # Verify search works
    results = col.query(query_texts=["memory persistence"], n_results=1)
    assert len(results["documents"][0]) > 0
    del col
    del client
    gc.collect()

    shutil.rmtree(tmpdir, ignore_errors=True)


def test_convo_mining_refreshes_changed_files_and_prunes_missing():
    tmpdir = tempfile.mkdtemp()
    try:
        with open(os.path.join(tmpdir, "chat.txt"), "w", encoding="utf-8") as f:
            f.write(
                "> First topic?\nInitial answer with enough detail to clear the minimum chunk size.\n\n"
                "> Why?\nBecause it helps preserve the first conversation during testing.\n"
            )
        with open(os.path.join(tmpdir, "notes.txt"), "w", encoding="utf-8") as f:
            f.write("> Secondary topic?\nKeep this longer conversation entry for now.\n")

        palace_path = os.path.join(tmpdir, "palace")
        mine_convos(tmpdir, palace_path, wing="test_convos")

        time.sleep(1.1)
        with open(os.path.join(tmpdir, "chat.txt"), "w", encoding="utf-8") as f:
            f.write(
                "> Updated topic?\nFresh answer with enough detail to be chunked and refiled.\n\n"
                "> Next?\nBecause it changed after the second sync and should replace the old drawer.\n"
            )
        os.remove(os.path.join(tmpdir, "notes.txt"))

        mine_convos(tmpdir, palace_path, wing="test_convos", prune_missing=True)

        client = chromadb.PersistentClient(path=palace_path)
        col = client.get_collection("mempalace_drawers")
        results = col.get(include=["documents", "metadatas"])

        docs = results["documents"]
        metas = results["metadatas"]
        source_names = {os.path.basename(meta["source_file"]) for meta in metas}

        assert "notes.txt" not in source_names
        assert any("Fresh answer with enough detail" in doc for doc in docs)
        assert not any("Initial answer with enough detail" in doc for doc in docs)
        del col
        del client
        gc.collect()
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
