# Generate-new-WARCs
Generate new WARCs from broken collections (e.g., Internet Memory)

### Algorithm

1. Identify malformed ARC/WARC files using warc check from [warcio checker](https://github.com/webrecorder/warcio/blob/master/warcio/checker.py) and then remove them from the process.
2. Eliminate duplicate records and generate new WARC files from the unique records:<br />
To check if a record is a duplicate we use a unique identifier which consists of the combination of Digest + Timestamp + URL and we store the value in a Berkeley DB (since it is the best database for key-value search). However, if the documents are ARC, we need to transform the ARC file into a WARC file since we need de Digest. Since step 1. is not 100% secure, we use [warcio recompress](https://github.com/webrecorder/warcio/blob/master/warcio/recompressor.py) which tries the best way to transform ARC to WARC.<br />
2.1 [warcio recompress](https://github.com/webrecorder/warcio/blob/master/warcio/recompressor.py)<br />
2.2 Check if Digest + Timestamp + URL exists in the Berkeley DB. If not, we will generate new WARCs with these records.

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
