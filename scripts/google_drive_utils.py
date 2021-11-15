import os
import time
import random
import logging
import pydrive
import numpy as np
import multiprocessing as mp

from pydrive import auth
from pydrive import drive


LOG = logging.getLogger(os.path.basename(__file__))
ch = logging.StreamHandler()
log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
ch.setFormatter(logging.Formatter(log_fmt))
ch.setLevel(logging.INFO)
LOG.addHandler(ch)
LOG.setLevel(logging.INFO)


class GDFolderDownloader:
    
    def __init__(self, root_dir_id, out_dir, config_path, processed_paths_file):
        self.gauth = auth.GoogleAuth()
        self.gauth.LoadClientConfigFile(config_path)
        self.gauth.LoadCredentialsFile("credentials.txt")
        if self.gauth.credentials is None:
            self.gauth.CommandLineAuth()
        elif self.gauth.access_token_expired:
            self.gauth.Refresh()
        else:
            self.gauth.Authorize()
        self.gauth.SaveCredentialsFile("credentials.txt")
        self.gdrive = drive.GoogleDrive(self.gauth)
        query = "'{}' in parents".format(root_dir_id)
        LOG.info("QUERY: " + query)
        self.file_list = self.gdrive.ListFile({"q": query}).GetList()
        self.out_dir = out_dir
        self.processed_paths = processed_paths_file

        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        
    def download_all_files(self, num_files=-1):
        for fm in self.file_list:
            LOG.info("DOWNLOADING FILE: {}".format(fm["title"]))
            start = time.time()
            self.download_one_file(fm, self.out_dir, self.gdrive)
            LOG.info("Download took: {} seconds".format(time.time() - start))

    def download_one_file(self, file_meta, outdir, gdrive):
        gh = gdrive.CreateFile({"id": file_meta["id"]})
        outpath = "{}/{}".format(outdir, file_meta["title"])
        if os.path.exists(outpath):
            LOG.warning(
                "Path: {} exists. Delete it to download again".format(outpath))
            return outpath
        with open(self.processed_paths) as fh:
            to_skip = fh.read().split("\n")
        if outpath in to_skip:
            LOG.warning(
                "Path: {} exists. Delete it to download again".format(outpath))
            return None

        total_size = int(file_meta["fileSize"])
        if total_size <= 1e9:
            gh.GetContentFile(outpath)
        else:
            url = file_meta["downloadUrl"]
            chunksize = int(5e8)
            chunks = self.partial(total_size, chunksize)
            chunks[-1][1] += 1
            service = self.gauth.service
            try:
                with open(outpath, "wb") as fh:
                    for byte_begin, byte_end in chunks:
                        content = self.download_chunk(
                            url, service, byte_begin, byte_end)
                        fh.write(content)
            except:
                os.unlink(outpath)
                raise

        return outpath

    @staticmethod
    def partial(total_byte_len, part_size_limit):
        s = []
        for p in range(0, total_byte_len, part_size_limit):
            last = min(total_byte_len - 1, p + part_size_limit - 1)
            s.append([p, last])
        return s

    @staticmethod
    def download_chunk(url, service, byte_begin, byte_end):
        headers = {"Range": "bytes={}-{}".format(byte_begin, byte_end)}
        start = time.time()
        resp, content = service._http.request(url, headers=headers)
        if resp.status != 206:
            msg = "Error downloading chunk: {}".format(resp)
            raise StandardError(msg)
        return content        


    def file_iterator(self, num_files=-1):
        num_files = num_files if num_files > 0 else len(self.file_list)
        for fm in self.file_list:
            print("DOWNLOADING FILE: {}".format(fm["title"]))
            start = time.time()
            try:
                outpath = self.download_one_file(fm, self.out_dir, self.gdrive)
            except pydrive.files.ApiRequestError:
                outpath = None

            print("Download took: {} seconds".format(time.time() - start))
            yield outpath