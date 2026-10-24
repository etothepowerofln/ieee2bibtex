import re
import argparse
import sys
import os
from typing import List, Tuple

def clean_latex(text: str) -> str:
    """Removes common LaTeX formatting commands while retaining structural text."""
    text = re.sub(r'\\\$|\$', '', text)
    text = text.replace('\\&', '&').replace('\\_', '_').replace('\\%', '%').replace('\\#', '#')
    text = re.sub(r'\\(textbf|textit|emph|underline|textsc|mathrm)\{([^}]+)\}', r'\2', text)
    text = re.sub(r'\\(bf|it|em|small|large|Large)\b', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_bibitem_blocks(raw_text: str) -> List[Tuple[str, str]]:
    """Splits raw LaTeX input into individual (cite_key, body) tuples."""
    pattern = re.compile(r'\\bibitem(?:\s*\[[^\]]*\])?\s*\{([^}]+)\}')
    matches = list(pattern.finditer(raw_text))
    
    entries = []
    for i, match in enumerate(matches):
        cite_key = match.group(1).strip()
        start_idx = match.end()
        end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(raw_text)
        block_text = raw_text[start_idx:end_idx].strip()
        entries.append((cite_key, block_text))
    
    return entries

def parse_ieee_bibitem(cite_key: str, block_text: str, force_article: bool = False) -> str:
    """Parses IEEE bibitem matching exact quote boundaries and journal termination rules."""
    cleaned = clean_latex(block_text)
    
    # Match: Authors, followed by ``Title'' or "Title", followed by Source and Year/Details
    match = re.search(r'^(.*?)(?:``(.+?)\'\'|"(.+?)")(.*)$', cleaned)
    
    if match:
        author_part = match.group(1).strip().rstrip(',')
        title = (match.group(2) or match.group(3)).strip().rstrip(',')
        rest = match.group(4).strip().lstrip(',')
    else:
        author_part = "Unknown Author"
        title = cleaned
        rest = ""

    # Format authors: comma-separated list -> ' and ' separated list
    author_list = [a.strip() for a in author_part.split(',') if a.strip()]
    author_formatted = " and ".join(author_list)

    # Extract Year (4-digit number)
    year_match = re.search(r'\b(19\d{2}|20\d{2})\b', rest)
    year = year_match.group(1) if year_match else "n.d."

    # Journal/Source name stops at , vol., , no., , pp., or , yyyy
    stop_pattern = r',\s*(?:vol\.|v\.|no\.|n\.|pp\.|p\.|volume|number|page|pages|' + re.escape(year) + r')'
    source_match = re.split(stop_pattern, rest, flags=re.IGNORECASE)
    source = source_match[0].strip().rstrip('.,;') if source_match else "Unknown Source"
    
    if not source:
        source = "Unknown Source"

    # Determine entry type and field name
    if force_article:
        entry_type = 'article'
        source_type = 'journal'
    else:
        lower_source = source.lower()
        if 'proceedings' in lower_source or 'conference' in lower_source:
            entry_type = 'inproceedings'
            source_type = 'booktitle'
        else:
            entry_type = 'article'
            source_type = 'journal'

    bibtex_entry = (
        f"@{entry_type}{{{cite_key},\n"
        f"  author = {{{author_formatted}}},\n"
        f"  title = {{{title}}},\n"
        f"  {source_type} = {{{source}}},\n"
        f"  year = {{{year}}}\n"
        f"}}"
    )
    return bibtex_entry

def convert_bibitem_to_bibtex(bibitem_text: str, prefix: str = "", force_article: bool = False) -> str:
    parsed_entries = parse_bibitem_blocks(bibitem_text)
    
    if not parsed_entries:
        return "% No valid \\bibitem entries detected in the input text."
    
    bibtex_results = []
    
    for cite_key, block_text in parsed_entries:
        final_key = f"{prefix}{cite_key}" if prefix else cite_key
        converted = parse_ieee_bibitem(final_key, block_text, force_article=force_article)
        bibtex_results.append(converted)
    
    return "\n\n".join(bibtex_results)

def main():
    parser = argparse.ArgumentParser(description="Convert IEEE LaTeX bibitem list to BibTeX entries 100% offline.")
    parser.add_argument("input_file", help="Path to input .txt file containing \\bibitem entries")
    parser.add_argument("-o", "--output", help="Path to output .txt file for BibTeX entries", default=None)
    parser.add_argument("-p", "--prefix", help="Optional prefix string to prepend to all generated citation keys", default="")
    parser.add_argument("-a", "--force-article", action="store_true", help="Force every generated entry to be an @article type with a journal field")
    
    args = parser.parse_args()
    
    input_path = args.input_file
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.", file=sys.stderr)
        sys.exit(1)
        
    if args.output:
        output_path = args.output
    else:
        base_name = os.path.splitext(input_path)[0]
        output_path = f"{base_name}_bibtex.txt"
        
    with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    bibtex_output = convert_bibitem_to_bibtex(content, prefix=args.prefix, force_article=args.force_article)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(bibtex_output + "\n")
        
    print(f"Successfully converted {len(parse_bibitem_blocks(content))} entries offline.")
    print(f"BibTeX entries saved to: {output_path}")

if __name__ == "__main__":
    main()