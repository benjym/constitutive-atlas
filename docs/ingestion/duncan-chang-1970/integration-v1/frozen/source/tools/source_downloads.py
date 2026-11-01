"""Read selected members of large public ZIPs without fetching unrelated assets.

Original member bytes are checked against registry SHA-256 pins by the caller.
ZIP CRC checks and HTTP ETags additionally protect each range-based read.
"""
import io
import urllib.request
import zipfile


class PublicZip(io.RawIOBase):
    def __init__(self, url):
        if not url.startswith('https://data.openei.org/files/4075/'):
            raise ValueError('Unreviewed public ZIP host')
        self.url, self.pos = url, 0
        request = urllib.request.Request(url, headers={'Range': 'bytes=0-0'})
        with urllib.request.urlopen(request, timeout=45) as response:
            if response.status != 206 or not response.headers['Content-Range'].startswith('bytes 0-0/'):
                raise ValueError('Public ZIP server does not support exact ranges')
            self.size = int(response.headers['Content-Range'].split('/')[-1])
            self.etag = response.headers.get('ETag')
            response.read(1)

    def seekable(self): return True
    def readable(self): return True
    def tell(self): return self.pos

    def seek(self, offset, whence=0):
        self.pos = offset + (self.pos if whence == 1 else self.size if whence == 2 else 0)
        if not 0 <= self.pos <= self.size:
            raise ValueError('Invalid public ZIP seek')
        return self.pos

    def read(self, size=-1):
        size = min(size if size >= 0 else self.size-self.pos, self.size-self.pos)
        if size <= 0: return b''
        if size > 50_000_000:
            raise ValueError('Unreviewed public ZIP read size')
        last = self.pos+size-1
        headers = {'Range': f'bytes={self.pos}-{last}'}
        if self.etag: headers['If-Match'] = self.etag
        request = urllib.request.Request(self.url, headers=headers)
        with urllib.request.urlopen(request, timeout=60) as response:
            if response.status != 206 or response.headers['Content-Range'] != f'bytes {self.pos}-{last}/{self.size}':
                raise ValueError('Public ZIP range mismatch')
            content = response.read(size+1)
        if len(content) != size:
            raise ValueError('Public ZIP byte count differs')
        self.pos += size
        return content


def zip_member(file):
    with zipfile.ZipFile(PublicZip(file['url'])) as archive:
        member = archive.getinfo(file['zip_member'])
        if member.file_size != file['size_bytes'] or member.CRC != file['zip_crc32']:
            raise ValueError('Pinned ZIP member metadata differs')
        return archive.read(member)
