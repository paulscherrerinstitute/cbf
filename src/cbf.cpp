#ifdef __cplusplus
extern "C" {
#endif

#include <stdio.h>
#include <stdlib.h>
#include "cbf.h"

//for origin source code of the cbf [de]compression:
//http://sourceforge.net/projects/cbflib/files/cbflib/
//CBFlib-0.9.3.1
//cbf_byte_offset.c:int cbf_compress_byte_offset (void         *source,...)
//cbf_byte_offset.c:int cbf_decompress_byte_offset_slow (void         *destination,...)

//origin code from Dectris
//www.dectris.com/ -> Download ->3rd party -> CBF Reader -> cbf_c.tar (28.0 KiB)
//(the code here is based from the dectris sources)

//Dectris: CBF_decode.c: int read_diskimage_cbf_raw(struct object_descriptor *ObjPtr,...)
unsigned int decodeCBFuin32(const unsigned char *inBuf, const int inNumByte, unsigned char *outBuf)
{
  unsigned int *outBufX = (unsigned int *) outBuf;
  unsigned int *outBufStart;
  outBufStart=outBufX;

  union
  {
    const unsigned char *uint8;
    const char *int8;
    const unsigned short *uint16;
    const short *int16;
    const unsigned int *uint32;
    const int *int32;
  } enc, encStart;

  encStart.uint8=enc.uint8=inBuf;
  unsigned int val_curr=0;
  unsigned int diff=0;
  while(enc.uint8-encStart.uint8<inNumByte)
  {
    if(*enc.uint8!=0x80)
    {
      diff=(int)*enc.int8++;
    }
    else
    {
      enc.uint8++;
      if(*enc.uint16!=0x8000)
      {
        diff=(int)*enc.int16++;
      }
      else
      {
        enc.uint16++;
        diff=(int)*enc.int32++;
      }
    }
    val_curr+=diff;
    *outBufX=val_curr;
    outBufX++; // Increment by 4 bytes as outBuf is now char*
  }
  return (outBufX-outBufStart)*4;
}

//Dectris: CBF_encode.c: int write_diskimage_det_cbf(struct object_descriptor *ObjPtr,
unsigned int encodeCBFuin32(const unsigned char *inBuf, unsigned int inNumElem, unsigned char *outBuf, unsigned int outNumBytes)
{
  union
  {
    unsigned char *uint8;
    char *int8;
    unsigned short *uint16;
    short *int16;
    unsigned int *uint32;
    int *int32;
  } enc, encStart;
  
  unsigned int i;
  int cval, nval, diff;
  const int* in = (int *)inBuf;
  const char* encEnd = (const char*)&outBuf[outNumBytes-6]; //one pixel before end (max pix size=6 bytes)
  int res;
  inNumElem = inNumElem/4; // TODO to be verified
  encStart.uint8=enc.uint8=outBuf;
  cval = 0;
  for (i=0; i<inNumElem; i++)
  {
    if(enc.int8>encEnd)// if compression is going badly
      return 0;
    nval = *in++;      // next value to consider
    diff = nval - cval;
    if (abs(diff) <= 127)
      *enc.int8++ = (char)diff;
    else
    {
      *enc.int8++ = 0x80;
      if (abs(diff) <= 32767)
        *enc.int16++ = (short)diff;
      else
      {
        *enc.int16++ = 0x8000;
        *enc.int32++ = diff;
      }
    }
    cval = nval;      // current value
  }
  res = (unsigned int)(enc.int8-encStart.int8);
  return res;
}

unsigned int decodeCBFuin16(const unsigned char *inBuf, const int inNumByte, unsigned short *outBuf)
{
  unsigned short *outBufStart;
  outBufStart=outBuf;

  union
  {
    const unsigned char *uint8;
    const char *int8;
    const unsigned short *uint16;
    const short *int16;
  } enc, encStart;

  encStart.uint8=enc.uint8=inBuf;
  unsigned int val_curr=0;
  unsigned int diff=0;
  while(enc.uint8-encStart.uint8<inNumByte)
  {
    if(*enc.uint8!=0x80)
    {
      diff=(int)*enc.int8++;
    }
    else
    {
      enc.uint8++;
      diff=(int)*enc.int16++;
    }
    val_curr+=diff;
    *outBuf=val_curr;
    outBuf++;
  }
  return (outBuf-outBufStart)*2;
}

//Dectris: CBF_encode.c: int write_diskimage_det_cbf(struct object_descriptor *ObjPtr,
unsigned int encodeCBFuin16(const unsigned short *inBuf, unsigned int inNumElem, unsigned char *outBuf, unsigned int outNumBytes)
{
  union
  {
    unsigned char *uint8;
    char *int8;
    unsigned short *uint16;
    short *int16;
  } enc, encStart;
  unsigned int i;
  int cval, nval, diff;
  const short* in = (short*)inBuf;
  const char* encEnd = (const char*)&outBuf[outNumBytes-3]; //one pixel before end (max pix size=3 bytes)
  int res;
  encStart.uint8=enc.uint8=outBuf;
  cval = 0;
  for (i=0; i<inNumElem; i++)
  {
    if(enc.int8>encEnd)// if compression is going badly
      return 0;
    nval = *in++;      // next value to consider
    diff = nval - cval;
    if (abs(diff) <= 127)
      *enc.int8++ = (char)diff;
    else
    {
      *enc.int8++ = 0x80;
      *enc.int16++ = (short)diff;
    }
    cval = nval;      // current value
  }
  res = (unsigned int)(enc.int8-encStart.int8);
  return res;
}


#ifdef __cplusplus
}
#endif
