"""
Quality metrics for Nassij conversion.
Implements CER, WER, diacritics preservation, and ligature validation.
"""
from typing import Dict, Optional, Tuple
import unicodedata

from utils.unicode_helpers import count_diacritics, normalize_nfc


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate Levenshtein distance between two strings.
    
    Args:
        s1: First string
        s2: Second string
        
    Returns:
        Edit distance (number of operations needed)
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def calculate_cer(reference: str, hypothesis: str) -> float:
    """
    Calculate Character Error Rate (CER).
    Target: < 0.08 (8%)
    
    Args:
        reference: Ground truth text
        hypothesis: OCR/converted text
        
    Returns:
        CER value between 0.0 and 1.0
    """
    if not reference:
        return 1.0 if hypothesis else 0.0
    
    # Normalize both strings
    ref_norm = normalize_nfc(reference)
    hyp_norm = normalize_nfc(hypothesis)
    
    # Calculate edit distance
    distance = levenshtein_distance(ref_norm, hyp_norm)
    
    # CER = edit_distance / reference_length
    cer = distance / len(ref_norm)
    
    return min(cer, 1.0)  # Cap at 1.0


def calculate_wer(reference: str, hypothesis: str) -> float:
    """
    Calculate Word Error Rate (WER).
    Target: < 0.20 (20%)
    
    Args:
        reference: Ground truth text
        hypothesis: OCR/converted text
        
    Returns:
        WER value between 0.0 and 1.0
    """
    if not reference:
        return 1.0 if hypothesis else 0.0
    
    # Split into words (handle Arabic and Latin)
    ref_words = reference.split()
    hyp_words = hypothesis.split()
    
    if not ref_words:
        return 1.0 if hyp_words else 0.0
    
    # Calculate word-level edit distance
    distance = levenshtein_distance(' '.join(ref_words), ' '.join(hyp_words))
    
    # WER = edit_distance / reference_word_count
    wer = distance / len(ref_words)
    
    return min(wer, 1.0)  # Cap at 1.0


def calculate_diacritics_preservation(reference: str, hypothesis: str) -> float:
    """
    Calculate diacritics preservation rate.
    Target: ≥ 90%
    
    Args:
        reference: Original text with diacritics
        hypothesis: Processed text
        
    Returns:
        Preservation rate between 0.0 and 1.0
    """
    ref_diacritics = count_diacritics(reference)
    hyp_diacritics = count_diacritics(hypothesis)
    
    if ref_diacritics == 0:
        # No diacritics in reference - perfect if none in hypothesis
        return 1.0 if hyp_diacritics == 0 else 0.0
    
    # Calculate preservation rate
    preservation_rate = hyp_diacritics / ref_diacritics
    
    return min(preservation_rate, 1.0)


def validate_ligatures(text: str) -> Dict[str, bool]:
    """
    Validate that known Arabic ligatures are present and correct.
    Target: 100% accuracy
    
    Args:
        text: Text to validate
        
    Returns:
        Dictionary mapping ligature to validation result
    """
    known_ligatures = {
        'لا': 'Lam + Alif',
        'إلا': 'Alif + Lam + Alif',
        'الله': 'Alif + Lam + Lam + Heh',
        'لله': 'Lam + Lam + Heh',
    }
    
    results = {}
    for ligature, description in known_ligatures.items():
        # Check if ligature exists in text
        found = ligature in text
        
        # Verify it's correctly formed (normalized)
        normalized_text = normalize_nfc(text)
        correctly_formed = ligature in normalized_text
        
        results[ligature] = {
            'found': found,
            'correctly_formed': correctly_formed,
            'description': description
        }
    
    return results


def calculate_table_accuracy(reference_table: Dict, hypothesis_table: Dict) -> float:
    """
    Calculate table cell accuracy.
    Target: ≥ 90%
    
    Args:
        reference_table: Reference table with 'cells' key
        hypothesis_table: Converted table with 'cells' key
        
    Returns:
        Accuracy value between 0.0 and 1.0
    """
    ref_cells = reference_table.get('cells', [])
    hyp_cells = hypothesis_table.get('cells', [])
    
    if not ref_cells:
        return 1.0 if not hyp_cells else 0.0
    
    # Calculate cell count accuracy
    ref_cell_count = sum(len(row) for row in ref_cells)
    hyp_cell_count = sum(len(row) for row in hyp_cells)
    
    if ref_cell_count == 0:
        return 1.0 if hyp_cell_count == 0 else 0.0
    
    # Count accuracy
    count_accuracy = 1.0 - abs(ref_cell_count - hyp_cell_count) / ref_cell_count
    
    # Calculate content accuracy (character-level)
    total_cer = 0.0
    matched_cells = 0
    
    min_rows = min(len(ref_cells), len(hyp_cells))
    for i in range(min_rows):
        ref_row = ref_cells[i]
        hyp_row = hyp_cells[i] if i < len(hyp_cells) else []
        
        min_cols = min(len(ref_row), len(hyp_row))
        for j in range(min_cols):
            ref_cell = ref_row[j] if j < len(ref_row) else ''
            hyp_cell = hyp_row[j] if j < len(hyp_row) else ''
            
            if ref_cell or hyp_cell:
                cell_cer = calculate_cer(ref_cell, hyp_cell)
                total_cer += cell_cer
                matched_cells += 1
    
    if matched_cells == 0:
        content_accuracy = 0.0
    else:
        avg_cer = total_cer / matched_cells
        content_accuracy = 1.0 - avg_cer
    
    # Combined accuracy (weighted: 30% count, 70% content)
    accuracy = 0.3 * count_accuracy + 0.7 * content_accuracy
    
    return max(0.0, min(1.0, accuracy))


def calculate_all_metrics(reference: str, 
                         hypothesis: str,
                         reference_table: Optional[Dict] = None,
                         hypothesis_table: Optional[Dict] = None) -> Dict:
    """
    Calculate all quality metrics.
    
    Args:
        reference: Reference text
        hypothesis: Converted text
        reference_table: Optional reference table
        hypothesis_table: Optional converted table
        
    Returns:
        Dictionary with all metrics
    """
    metrics = {
        'cer': calculate_cer(reference, hypothesis),
        'wer': calculate_wer(reference, hypothesis),
        'diacritics_preservation': calculate_diacritics_preservation(reference, hypothesis),
        'ligatures': validate_ligatures(hypothesis),
    }
    
    # Add table metrics if provided
    if reference_table and hypothesis_table:
        metrics['table_accuracy'] = calculate_table_accuracy(reference_table, hypothesis_table)
    
    # Overall quality score (weighted average)
    quality_score = (
        0.3 * (1.0 - metrics['cer']) +  # CER contribution
        0.2 * (1.0 - metrics['wer']) +  # WER contribution
        0.3 * metrics['diacritics_preservation'] +  # Diacritics contribution
        0.2 * (1.0 if all(v.get('correctly_formed', False) for v in metrics['ligatures'].values()) else 0.0)  # Ligatures
    )
    
    if 'table_accuracy' in metrics:
        quality_score = 0.8 * quality_score + 0.2 * metrics['table_accuracy']
    
    metrics['quality_score'] = quality_score
    
    return metrics

