# Generate-new-WARCs
Generate new WARCs from broken collections (e.g., Internet Memory)


### Setup

```
git clone https://github.com/arquivo/Generate-new-WARCs.git
cd Generate-new-WARCs
pip install --upgrade virtualenv
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
```
### Run

```
python Generate_New_WARCs.py
```

### Parameters

<pre>
-p or --path                      --> Localization of the patching files
-d or --destination               --> Destination of the patching files merged
-r or --destination_removed_warcs --> Destination of the removed warcs from warcio step
-n or --filename                  --> Filename_template of the patching files merged
-e or --extension                 --> Extension of originated files
-s or --size                      --> Size of the files merged (MB)
</pre>

### Example

Example and default parameters:

```
python 
```

### Authors

- [Pedro Gomes](pedro.gomes@fccn.pt)
