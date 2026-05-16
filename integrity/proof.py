import json
from datetime import datetime, timezone
from typing import List, Dict

from .merkle_tree import MerkleTree
from .diacritics_splitter import split_diacritics

class IntegrityProof:
    """
    Generates and verifies Linguistic Integrity Proof files.
    """
    
    def __init__(self):
        self.blocks_info = []
        self.merkle_tree = MerkleTree()

    def add_block(self, text: str, block_type: str = "text"):
        """
        Add a document block to the proof.
        Computes the canonical and diacritics hashes, adds to Merkle Tree.
        """
        # We only hash textual content. For images, we could hash bytes, but Nassij is linguistic.
        if block_type == "image":
            return
            
        block_index = len(self.blocks_info)
        hashes = split_diacritics(text, block_index=block_index)
        
        self.blocks_info.append({
            "index": block_index,
            "type": block_type,
            "base_hash": hashes["base_hash"],
            "diacritics_hash": hashes["diacritics_hash"],
            "compound_hash": hashes["compound_hash"]
        })
        
        self.merkle_tree.add_leaf(hashes["compound_hash"])

    def generate_proof_file(self, source_filename: str, output_path: str):
        """
        Finalize the tree and write the .nassij-proof JSON file.
        """
        root_hash = self.merkle_tree.build()
        
        proof_data = {
            "version": "nassij-proof-v1",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source_file": source_filename,
            "merkle_root": root_hash,
            "blocks_count": len(self.blocks_info),
            "normalization_steps": ["NFKC", "remove_kashida", "remove_zwj", "NFC"],
            "processor": "nassij-v3.0",
            "blocks": self.blocks_info  # Storing leaf hashes for verification
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(proof_data, f, indent=2, ensure_ascii=False)
            
        return proof_data
