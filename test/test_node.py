# tests/test_node.py
from storage_virtual_node import StorageVirtualNode

def test_store_and_retrieve(tmp_path):
    node = StorageVirtualNode("testnode", data_dir=str(tmp_path))
    key = "song1"
    data = b"hello-music"
    assert node.store(key, data) is True
    got = node.retrieve(key)
    assert got == data
    assert node.delete(key) is True
    assert node.retrieve(key) is None
