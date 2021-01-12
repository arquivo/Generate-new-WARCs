from warcio.archiveiterator import ArchiveIterator
from warcio.warcwriter import WARCWriter
from warcio.exceptions import ArchiveLoadFailed
import os
import string
import random
import click
import argparse
import datetime
from bsddb3 import db
import time

exit_value = 0

def random_id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

parser = argparse.ArgumentParser(description='Description of your program')
parser.add_argument('-p','--path', help='Localization of the patching files', default= "./ARC/")
parser.add_argument('-r','--destination_removed_warcs', help='Destination of the removed warcs from warcio step', default= "./REMOVED_WARCS/")
parser.add_argument('-d','--destination', help='Destination of the patching files merged', default= "./NEW_WARCS/")
parser.add_argument('-n','--filename', help='Filename_template of the patching files merged', default="NEW-IM-WARC-{timestamp}-{random}.warc.gz")
parser.add_argument('-s','--size', help='Size of the files merged (MB)', type=int, default=100)
args = vars(parser.parse_args())


def namePatchingMergedFile(filename_template, destination):
    
    string_aux = filename_template
    if "{timestamp}" in filename_template:
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d%H%M%S')
        string_aux = string_aux.replace("{timestamp}", str(timestamp))
    if "{random}" in filename_template:
        random_generated = random_id_generator()
        string_aux = string_aux.replace("{random}", str(random_generated))
    if "{timestamp}" not in filename_template and "{random}" not in filename_template:
        raise ValueError('Filename without unique identifiers (e.g., timestamp).')
    if destination.endswith("/"):
        return destination + string_aux
    else:
        return destination + "/" + string_aux


def _read_entire_stream(stream):

    while True:
        piece = stream.read(1024*1024)
        if len(piece) == 0:
            break

def check_from_warcio(filename):

    printed_filename = False
    with open(filename, 'rb') as stream:
        it = ArchiveIterator(stream, check_digests=True)
        for record in it:
            try:
                digest_present = (record.rec_headers.get_header('WARC-Payload-Digest') or
                              record.rec_headers.get_header('WARC-Block-Digest'))
                _read_entire_stream(record.content_stream())

                d_msg = None
                output = []

                rec_id = record.rec_headers.get_header('WARC-Record-ID')
                rec_type = record.rec_headers.get_header('WARC-Type')
                rec_offset = it.get_record_offset()
            except:
                raise ValueError('Represents a hidden bug, do not catch this')

            if record.digest_checker.passed is False:
                exit_value = 1
                output = list(record.digest_checker.problems)
                raise ValueError('Represents a hidden bug, do not catch this')
            elif record.digest_checker.passed is True:
                d_msg = 'digest pass'
            elif record.digest_checker.passed is None:
                if digest_present and rec_type == 'revisit':
                    d_msg = 'digest present but not checked (revisit)'
                elif digest_present:  # pragma: no cover
                    # should not happen
                    d_msg = 'digest present but not checked'
                else:
                    d_msg = 'no digest to check'

            if d_msg or output:
                if not printed_filename:
                    printed_filename = True


def processWarcio(mypath, destination_removed_warcs):

    ##Step similar to warcio checker.
    for subdir, dirs, files in os.walk(mypath):
        with click.progressbar(length=len(files), show_pos=True) as progress_bar:
            for file in files:
                progress_bar.update(1)
                file_name = os.path.join(subdir, file)
                try:
                    res = check_from_warcio(file_name)
                except:
                    os.system("mv " + file_name + " " + destination_removed_warcs)


def processArcToWarc(IMdb_Records, IMdb_WARCs, mypath, destination, filename_template,sizeFile):

    #import pdb;pdb.set_trace()

    click.secho("Start ARC to WARC...", fg='green')

    #Check if exists Directory of destination
    if not os.path.exists(destination):
        os.makedirs(destination)
    
    #Create the first WARC file
    filename = namePatchingMergedFile(filename_template, destination)
    output = open(filename  , 'wb')
    writer = WARCWriter(output, gzip=True)

    for subdir, dirs, files in os.walk(mypath):
        if files:
            with click.progressbar(length=len(files), show_pos=True) as progress_bar:
                for file in files:
                    progress_bar.update(1)
                    file_name = os.path.join(subdir, file)
                    
                    #Check if name of the WARC is on berkeley db IMdb_WARCs
                    if not IMdb_WARCs.has_key(file_name.encode('utf_8')):
                        ##Recompress arc to warc.gz
                        os.system("warcio recompress " + file_name + " " + subdir + "warc/" + file.replace(".arc.gz", ".warc.gz"))

                        with open(subdir + "warc/" + file.replace(".arc.gz", ".warc.gz"), 'rb') as stream:
                            for record in ArchiveIterator(stream):
                                if record.rec_type != 'warcinfo':
                                    try:
                                        #Build a unique indentifier
                                        string_compare = (record.rec_headers.get_header('WARC-Payload-Digest') or
                                                      record.rec_headers.get_header('WARC-Block-Digest'))
                                        string_compare += record.rec_headers.get_header('WARC-Date')
                                        string_compare += record.rec_headers.get_header('WARC-Target-URI')
                                        
                                        #Check if record is on berkeley db IMdb_Records
                                        if not IMdb_Records.has_key(string_compare.encode('utf_8')):
                                            if os.path.getsize(filename) > sizeFile:
                                                output.close()
                                                filename = namePatchingMergedFile(filename_template, destination)
                                                output = open(filename, 'wb')
                                                writer = WARCWriter(output, gzip=True)

                                            IMdb_Records.put(string_compare.encode('utf_8'), None)
                                            writer.write_record(record)
                                    except:
                                        continue
                        IMdb_WARCs.put(file_name.encode('utf_8'), None)
                    #remove WARC from "warcio recompress" to save space (disk)
                    os.system("rm -rf " + subdir + "warc/" + file.replace(".arc.gz", ".warc.gz"))
                break
        else:
            raise ValueError('No files to be merged. Empty localization \"-path\"')

if __name__ == '__main__':

    click.secho("Read inputs...", fg='green')
    
    ##Process input
    mypath = args['path']
    destination = args['destination']
    filename_template = args['filename']
    sizeFile = args['size'] * 1000000
    destination_removed_warcs = args['destination_removed_warcs']
    
    processWarcio(mypath, destination_removed_warcs)
    
    click.secho("Start berkeley db...", fg='green')
    
    ##Init berkeley db with the records
    IMdb_Records = db.DB()
    IMdb_Records.open("IM_RECORDS", None, db.DB_BTREE, db.DB_CREATE)

    ##Init berkeley db with the name of the WARCs processed
    IMdb_WARCs = db.DB()
    IMdb_WARCs.open("IM_WARCS_NAME", None, db.DB_BTREE, db.DB_CREATE)

    processArcToWarc(IMdb_Records, IMdb_WARCs, mypath, destination, filename_template,sizeFile)
    
    IMdb_Records.close()
    IMdb_WARCs.close()
