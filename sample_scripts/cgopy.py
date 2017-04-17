__all__ = [ 'libgobgp', '_PATTRS_CAP', '_AF_NAME', 'Buf', 'Path', 'unpack_buf', ]

from ctypes import *
from struct import *
import os

# load C shared library
libgobgp = cdll.LoadLibrary(os.environ["GOPATH"] +"/src/github.com/osrg/gobgp/gobgp/lib/libgobgp.so")

# constants 
_PATTRS_CAP = 32
_AF_NAME = dict([(4, "ipv4-unicast"), (6, "ipv6-unicast"), ])

# structs
class Buf(Structure):
  _fields_ = [("value", POINTER(c_char)),
              ("len", c_int),
             ]
class Path(Structure):
  _fields_ = [("nlri", Buf),
              ("path_attributes", POINTER(POINTER(Buf) * _PATTRS_CAP)),
              ("path_attributes_len", c_int),
              ("path_attributes_cap", c_int),
             ]

# argument and return type definitions
libgobgp.serialize_path.restype = POINTER(Path)
libgobgp.serialize_path.argtypes = (c_int, c_char_p)
libgobgp.decode_path.restype = c_char_p
libgobgp.decode_path.argtypes = (POINTER(Path), )

def unpack_buf(buf):
  # unpack Buf obj
  return unpack(str(buf.len)+"s", buf.value[:buf.len])[0]

if __name__ == '__main__':
  pass

