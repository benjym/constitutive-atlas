"""Streaming JSON reference extraction; no source hashing or persistent source copy.
Duplicate object keys are rejected, so dict-overwrite semantics cannot silently widen closure.
"""
import json,re
class Reader:
 def __init__(self, stream, block=1024*1024):self.stream=stream;self.block=block;self.buf='';self.pos=0;self.eof=False;self.decoder=json.JSONDecoder();self.refs=set()
 def fill(self):
  self.buf=self.buf[self.pos:];self.pos=0;b=self.stream.read(self.block);self.buf+=b;self.eof=not b
 def char(self):
  while True:
   while self.pos<len(self.buf) and self.buf[self.pos].isspace():self.pos+=1
   if self.pos<len(self.buf):return self.buf[self.pos]
   if self.eof:raise ValueError('Unexpected end of JSON')
   self.fill()
 def take(self,c):
  assert self.char()==c,('Unexpected JSON token',self.char(),c);self.pos+=1
 def scalar(self):
  while True:
   try:
    value,end=self.decoder.raw_decode(self.buf,self.pos)
    # A numeric token may continue in the next block.
    if end==len(self.buf) and not self.eof:self.fill();continue
    self.pos=end;return value
   except json.JSONDecodeError:
    if self.eof:raise
    self.fill()
 def value(self):
  c=self.char()
  if c=='{':
   self.take('{');seen=set();fields={}
   if self.char()=='}':self.take('}');return None
   while True:
    assert self.char()=='"';key=self.scalar();assert key not in seen,('Duplicate key',key);seen.add(key);self.take(':');v=self.value()
    if key in ('sha256','hash','path','original_path','archived_path'):fields[key]=v
    if '/' in key and isinstance(v,str) and len(v)==64:self.refs.add(key)
    c=self.char()
    if c=='}':self.take('}');break
    self.take(',')
   if any(isinstance(fields.get(k),str) and len(fields[k])==64 for k in ('sha256','hash')):
    for k in ('path','original_path','archived_path'):
     if isinstance(fields.get(k),str):self.refs.add(fields[k])
   return None
  if c=='[':
   self.take('[')
   if self.char()==']':self.take(']');return None
   while True:
    self.value()
    if self.char()==']':self.take(']');break
    self.take(',')
   return None
  return self.scalar()
 def parse(self):
  self.value()
  while True:
   assert not self.buf[self.pos:].strip(), 'Trailing JSON bytes'
   if self.eof:break
   self.pos=len(self.buf);self.fill()
  return sorted(self.refs)
def references(stream,block=1024*1024):return Reader(stream,block).parse()
