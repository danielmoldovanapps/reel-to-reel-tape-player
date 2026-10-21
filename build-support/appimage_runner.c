#define _GNU_SOURCE
#define _XOPEN_SOURCE 700
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/wait.h>
#include <ftw.h>
#include <errno.h>
#include <limits.h>
#include <signal.h>

static uint16_t u16(const unsigned char*p){return p[0]|((uint16_t)p[1]<<8);}
static uint32_t u32(const unsigned char*p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static uint64_t u64(const unsigned char*p){return (uint64_t)u32(p)|((uint64_t)u32(p+4)<<32);}
static void fail(const char*s){fprintf(stderr,"Reel-to-Reel Tape Player AppImage: %s\n",s); exit(1);}
static void readat(int fd,void*p,size_t n,off_t where){
 if(pread(fd,p,n,where)!=(ssize_t)n)fail("could not read image contents");
}
static int delete_cb(const char *path,const struct stat *st,int type,struct FTW *ftw){(void)st;(void)type;(void)ftw;return remove(path);}
static int append_image_offset(int fd){
 unsigned char magic[4];
 // ELF runtime is 4096-byte padded; SquashFS starts at an aligned offset
 for(int pos=4096;pos<=2097152;pos+=4096){
  if(pread(fd,magic,4,pos)!=4)break;
  if(memcmp(magic,"hsqs",4)==0)return pos;
 }
 fail("embedded SquashFS not found"); return 0;
}
static int mk_dir(const char*p){
 if(mkdir(p,0700)==0 || errno==EEXIST)return 0;
 fprintf(stderr,"mkdir(%s): %s\n",p,strerror(errno));return -1;
}
static void extract_sqfs(int fd,int off,const char *dir){
 unsigned char sb[96];readat(fd,sb,96,off);
 if(u32(sb)!=0x73717368 || u16(sb+28)!=4 || u32(sb+12)!=131072)fail("invalid SquashFS header");
 uint64_t inode_table=u64(sb+64),directory_table=u64(sb+72);
 if(inode_table>3000000000ULL || directory_table>3000000000ULL)fail("invalid SquashFS pointers");
 unsigned char h[2];readat(fd,h,2,off+inode_table);int insize=u16(h)&0x7fff;
 if((u16(h)&0x8000)==0 || insize<32 || insize>8192)fail("unexpected inode metadata compression");
 unsigned char in[8192];readat(fd,in,insize,off+inode_table+2);
 readat(fd,h,2,off+directory_table);int dirsize=u16(h)&0x7fff;
 if((u16(h)&0x8000)==0 || dirsize<12 || dirsize>8192)fail("unexpected directory metadata compression");
 unsigned char d[8192];readat(fd,d,dirsize,off+directory_table+2);
 uint32_t count=u32(d)+1;
 if(count>80)fail("unexpected file count");
 size_t cursor=12;
 for(uint32_t i=0;i<count;i++){
  if(cursor+8>=(size_t)dirsize)fail("malformed directory entry");
  int inode_offset=u16(d+cursor),type=u16(d+cursor+4),namesize=u16(d+cursor+6)+1;cursor+=8;
  if(cursor+namesize>(size_t)dirsize || namesize<1 || namesize>255 || type!=2)fail("invalid directory entry");
  char name[256];memcpy(name,d+cursor,namesize);name[namesize]=0;cursor+=namesize;
  if(strchr(name,'/') || strstr(name,".."))fail("unsafe archive filename");
  if(inode_offset+32>insize || u16(in+inode_offset)!=2)fail("invalid file inode");
  const unsigned char *node=in+inode_offset;
  uint32_t begin=u32(node+16),size=u32(node+28);
  uint32_t bcount=(size+131071U)/131072U;
  if(inode_offset+32+4*bcount>insize)fail("invalid block sizes");
  char path[PATH_MAX];if(snprintf(path,sizeof(path),"%s/%s",dir,name)>=sizeof(path))fail("path too long");
  int out=open(path,O_CREAT|O_WRONLY|O_EXCL|O_NOFOLLOW,0600);
  if(out<0)fail("could not create extracted file");
  uint32_t offset=begin,remain=size;
  unsigned char *buf=malloc(131072);if(!buf)fail("out of memory");
  for(uint32_t b=0;b<bcount;b++){
   uint32_t packed=u32(node+32+b*4),n=packed&0xffffff;
   if(!(packed&0x1000000) || n>131072 || n>remain){fail("unsupported compressed block");}
   readat(fd,buf,n,off+offset);
   if(write(out,buf,n)!=(ssize_t)n)fail("could not write file");
   remain-=n;offset+=n;
  }
  free(buf);
  if(remain)fail("incomplete file");
  if(fchmod(out,u16(node+2)&0777)!=0)fail("could not set executable bit");
  close(out);
 }
}
int main(int argc,char**argv){
 char self[PATH_MAX]; ssize_t n=readlink("/proc/self/exe",self,sizeof(self)-1);
 if(n<=0 || n>=sizeof(self))fail("could not locate launcher");self[n]=0;
 int fd=open(self,O_RDONLY);if(fd<0)fail("could not open launcher");
 int off=append_image_offset(fd);
 if(argc>1 && !strcmp(argv[1],"--appimage-offset")){printf("%d\n",off);return 0;}
 if(argc>1 && !strcmp(argv[1],"--appimage-version")){puts("Reel-to-Reel Tape Player 1.3.0 (extract-and-run runtime)");return 0;}
 int do_extract=(argc>1 && !strcmp(argv[1],"--appimage-extract"));
 char dir[PATH_MAX];
 if(do_extract){
  if(!getcwd(dir,sizeof(dir)))fail("could not find cwd");
  if(strlen(dir)+14>=sizeof(dir))fail("path too long");
  strcat(dir,"/squashfs-root");if(mk_dir(dir))return 1;
 }else{
  const char*tmp=getenv("TMPDIR");if(!tmp || !*tmp)tmp="/tmp";
  if(snprintf(dir,sizeof(dir),"%s/ReelPlayer-%ld-XXXXXX",tmp,(long)getuid())>=sizeof(dir))fail("tempdir name too long");
  if(!mkdtemp(dir))fail("could not create secure temporary directory");
 }
 extract_sqfs(fd,off,dir);close(fd);
 if(do_extract){printf("%s\n",dir);return 0;}
 char app[PATH_MAX];snprintf(app,sizeof(app),"%s/AppRun",dir);
 pid_t pid=fork();if(pid<0)fail("fork failed");
 if(pid==0){
  setenv("APPDIR",dir,1);
  setenv("APPIMAGE",self,1);
  // Skip --appimage-extract-and-run; launch as normal.
  int skip=(argc>1 && !strcmp(argv[1],"--appimage-extract-and-run"));
  char**args=calloc(argc+2,sizeof(char*));
  args[0]=app;int j=1;
  for(int i=1+skip;i<argc;i++)args[j++]=argv[i];
  args[j]=NULL;
  execv(app,args);perror("exec AppRun");_exit(127);
 }
 int status=0;while(waitpid(pid,&status,0)<0 && errno==EINTR){}
 nftw(dir,delete_cb,64,FTW_DEPTH|FTW_PHYS);
 if(WIFEXITED(status))return WEXITSTATUS(status);
 if(WIFSIGNALED(status))return 128+WTERMSIG(status);
 return 1;
}
