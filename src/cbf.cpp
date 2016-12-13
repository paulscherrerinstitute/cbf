#ifdef __cplusplus
extern "C" {
#endif

#include <stdio.h>
#include <stdlib.h>
#include "cbf.h"


// The byte offset compression is explained in detail at:
// http://www.esrf.eu/computing/Forum/imgCIF/cbf_definition.html
// and
// ftp://www.bernstein-plus-sons.com/software/CBF/doc/CBFlib.html

//The "byte_offset" compression algorithm is the following:
//
//Start with a base pixel value of 0.
//Compute the difference delta between the next pixel value and the base pixel value.
//If -127 ≤ delta ≤ 127, output delta as one byte, make the current pixel value the base pixel value and return to step 2.
//Otherwise output -128 (80 hex).
//We still have to output delta. If -32767 ≤ delta ≤ 32767, output delta as a little_endian 16-bit quantity, make the current pixel value the base pixel value and return to step 2.
//Otherwise output -32768 (8000 hex, little_endian, i.e. 00 then 80)
//We still have to output delta. If -2147483647 ≤ delta ≤ 2147483647, output delta as a little_endian 32 bit quantity, make the current pixel value the base pixel value and return to step 2.
//Otherwise output -2147483648 (80000000 hex, little_endian, i.e. 00, then 00, then 00, then 80) and then output the pixel value as a little-endian 64 bit quantity, make the current pixel value the base pixel value and return to step 2.
//The "byte_offset" decompression algorithm is the following:
//
//Start with a base pixel value of 0.
//Read the next byte as delta
//If -127 ≤ delta ≤ 127, add delta to the base pixel value, make that the new base pixel value, place it on the output array and return to step 2.
//If delta is 80 hex, read the next two bytes as a little_endian 16-bit number and make that delta.
//If -32767 ≤ delta ≤ 32767, add delta to the base pixel value, make that the new base pixel value, place it on the output array and return to step 2.
//If delta is 8000 hex, read the next 4 bytes as a little_endian 32-bit number and make that delta
//If -2147483647 ≤ delta ≤ 2147483647, add delta to the base pixel value, make that the new base pixel value, place it on the output array and return to step 2.
//If delta is 80000000 hex, read the next 8 bytes as a little_endian 64-bit number and make that delta, add delta to the base pixel value, make that the new base pixel value, place it on the output array and return to step 2.

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
