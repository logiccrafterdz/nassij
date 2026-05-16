import pytest
from integrity.proof import IntegrityProof
from integrity.diacritics_splitter import split_diacritics

def test_split_diacritics_with_index():
    text = "مَرْحَباً"
    
    # Same text, different index should yield different compound hash
    result1 = split_diacritics(text, block_index=0)
    result2 = split_diacritics(text, block_index=1)
    
    assert result1['base_hash'] == result2['base_hash']
    assert result1['diacritics_hash'] == result2['diacritics_hash']
    assert result1['compound_hash'] != result2['compound_hash']
    
def test_proof_contextual_binding():
    proof = IntegrityProof()
    proof.add_block("الفقرة الأولى", "text")
    proof.add_block("الفقرة الثانية", "text")
    
    assert len(proof.blocks_info) == 2
    assert proof.blocks_info[0]['index'] == 0
    assert proof.blocks_info[1]['index'] == 1
    
    hash_order_1 = proof.merkle_tree.build()
    
    # Create another proof with same blocks in reverse order
    proof2 = IntegrityProof()
    proof2.add_block("الفقرة الثانية", "text")
    proof2.add_block("الفقرة الأولى", "text")
    
    hash_order_2 = proof2.merkle_tree.build()
    
    # Because of block_index binding, even the leaves will be different!
    assert hash_order_1 != hash_order_2
