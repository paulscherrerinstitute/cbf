#pragma once

#ifdef __cplusplus
extern "C" {
#endif

//compression uncompression of uin32 data
unsigned int decodeCBFuin32(const unsigned char *inBuf, const int inNumByte, unsigned char *outBuf);
unsigned int encodeCBFuin32(const unsigned char *inBuf, unsigned int inNumElem, unsigned char *outBuf, unsigned int outNumBytes);

unsigned int decodeCBFuin16(const unsigned char *inBuf, const int inNumByte, unsigned short *outBuf);
unsigned int encodeCBFuin16(const unsigned short *inBuf, unsigned int inNumElem, unsigned char *outBuf, unsigned int outNumBytes);

#ifdef __cplusplus
}
#endif
