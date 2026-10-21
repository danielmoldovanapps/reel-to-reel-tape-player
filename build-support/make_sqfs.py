#!/usr/bin/env python3
"""Minimal SquashFS4 writer for flat AppDir: uncompressed blocks and metadata."""
import sys,struct,os,time,pathlib
S=struct.pack
BLOCK=131072

def meta(content):
 assert len(content)<=8192
 return S('<H',len(content)|0x8000)+content

def build(root,out):
 root=pathlib.Path(root); out=pathlib.Path(out)
 names=sorted([x for x in root.iterdir() if x.is_file()])
 assert len(names)<250
 positions={}; blocks={}; offset=96
 with out.open('wb') as f:
  f.write(b'\x00'*96)
  for x in names:
   positions[x.name]=offset
   blocks[x.name]=[]
   with x.open('rb') as fin:
    while (chunk:=fin.read(BLOCK)):
     f.write(chunk); offset+=len(chunk)
     blocks[x.name].append(len(chunk)|0x1000000)
  # Build inode records; directory inode root first
  directory=b''
  inode=b''
  mt=int(time.time());N=len(names)
  def base(t,mode,n):return S('<HHHHII',t,mode,0,0,mt,n)
  root_dir_size=12+sum(8+len(x.name.encode()) for x in names)
  inode+=base(1,0o755,1)+S('<IIHHI',0,N+2,root_dir_size,0,0)
  entries=[]
  for n,x in enumerate(names,2):
   nodepos=len(inode)
   sz=x.stat().st_size
   assert sz<2**32
   mode=x.stat().st_mode & 0o777
   inode+=base(2,mode,n)+S('<IIII',positions[x.name],0xFFFFFFFF,0,sz)+S('<'+'I'*len(blocks[x.name]),*blocks[x.name])
   entries.append((nodepos,n,x.name))
  assert len(inode)<=8192
  directory+=S('<III',N-1,0,2)
  for nodepos,n,name in entries:
   b=name.encode()
   directory+=S('<HhHH',nodepos,n-2,2,len(b)-1)+b
  assert len(directory)==root_dir_size
  inode_table=offset;payload=meta(inode);f.write(payload);offset+=len(payload)
  directory_table=offset;payload=meta(directory);f.write(payload);offset+=len(payload)
  ids_table=offset;payload=meta(S('<I',0));f.write(payload);offset+=len(payload)
  id_ptr=offset;f.write(S('<Q',ids_table));offset+=8
  # pad to 4096; bytes_used stores actual data end
  f.write(b'\0'*((-offset)%4096))
  # magic,inodes,mtime,blocksize,fragments,compression,blocklog,flags,no_ids,major,minor
  # flags: no_fragments bit 4
  sb=S('<IIIIIHHHHHHQQQQQQQQ',0x73717368,N+1,mt,BLOCK,0,1,17,1<<4,1,4,0,0,offset,id_ptr,2**64-1,inode_table,directory_table,2**64-1,2**64-1)
  assert len(sb)==96,len(sb)
  f.seek(0); f.write(sb)
 return out
if __name__=='__main__':print(build(sys.argv[1],sys.argv[2]))
