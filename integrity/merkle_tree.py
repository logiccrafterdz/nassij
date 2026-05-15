import hashlib
from typing import List, Optional

class MerkleTree:
    """
    Structural Merkle Tree for Document Integrity.
    Aggregates hashes of individual document blocks into a single root hash.
    """
    def __init__(self):
        self.leaves: List[str] = []
        self.root: Optional[str] = None

    def add_leaf(self, hash_value: str):
        """Add a leaf (hash of a block) to the tree."""
        self.leaves.append(hash_value)
        self.root = None # Invalidate root

    def _hash_pair(self, left: str, right: str) -> str:
        combined = left + right
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()

    def build(self) -> str:
        """Build the tree and return the root hash."""
        if not self.leaves:
            self.root = hashlib.sha256(b"").hexdigest()
            return self.root

        nodes = self.leaves.copy()
        while len(nodes) > 1:
            next_level = []
            for i in range(0, len(nodes), 2):
                left = nodes[i]
                # If odd number of nodes, duplicate the last one to pair with itself
                right = nodes[i + 1] if i + 1 < len(nodes) else left
                next_level.append(self._hash_pair(left, right))
            nodes = next_level
        
        self.root = nodes[0]
        return self.root
