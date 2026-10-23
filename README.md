# IEEE bibitem to bibtex reference converter

Converts a TXT file with multiple entries in the IEEE format into bibtex.

## Usage

    python3 ieee2bibtex.py in.txt -o out.txt -p "prefix_"

**-o** declares the output file name

**-p** adds a prefix to the entry names (artX becomes prefix_artX, for every entry)

## Input format

    First1 Last1, First2 Last2, First3 Last3, ``Title of the article,'' Source title, (volume|vol.|v.|number|no.|n.|pages|page|pp.|p.), Year.

**Or**

    First1 Last1, First2 Last2, First3 Last3, "Title of the article," Source title, (volume|vol.|v.|number|no.|n.|pages|page|pp.|p.), Year.

## Output format

    @article|proceedings{prefix_artX,

      author = {First1 Last1 and First2 Last2 and First3 Last3},
  
      title = {Title of the article},
  
      journal = {Source title},
  
      year = {Year}
  
    }
