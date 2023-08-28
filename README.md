pdf_to_text
-
Uses the [pdfminer.six](https://github.com/pdfminer/pdfminer.six) library to perform the task of converting .PDF to .TXT
```
pip install pdfminer.six
```

text_to_json_ti
-
Converts .TXT to .JSON, using regular expressions to separate JSON items by predetermined fields.  
URL and Filename items are extracted along with any incorrect information (not malicious) to create a whitelist array for filtering.

field_to_excel
-
Reads all of the specific field data from the .JSON files, dataframes them, and saves them to an .XLSX file with statistics as needed.
<br/><br/>

#### Copyright 2023. ClumL Inc. all rights reserved

