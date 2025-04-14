#include <ctype.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/evp.h>
#include <unistd.h>

const uint8_t hextable[0x100] = {
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 0, 0, 0, 0, 0, 0, 10, 11, 12, 13, 14, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 11, 12, 13, 14, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};
const char *strtable[0x100] = {
  "00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "0a", "0b", "0c", "0d", "0e", "0f", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "1a", "1b", "1c", "1d", "1e", "1f", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "2a", "2b", "2c", "2d", "2e", "2f", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "3a", "3b", "3c", "3d", "3e", "3f", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "4a", "4b", "4c", "4d", "4e", "4f", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "5a", "5b", "5c", "5d", "5e", "5f", "60", "61", "62", "63", "64", "65", "66", "67", "68", "69", "6a", "6b", "6c", "6d", "6e", "6f", "70", "71", "72", "73", "74", "75", "76", "77", "78", "79", "7a", "7b", "7c", "7d", "7e", "7f", "80", "81", "82", "83", "84", "85", "86", "87", "88", "89", "8a", "8b", "8c", "8d", "8e", "8f", "90", "91", "92", "93", "94", "95", "96", "97", "98", "99", "9a", "9b", "9c", "9d", "9e", "9f", "a0", "a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8", "a9", "aa", "ab", "ac", "ad", "ae", "af", "b0", "b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9", "ba", "bb", "bc", "bd", "be", "bf", "c0", "c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8", "c9", "ca", "cb", "cc", "cd", "ce", "cf", "d0", "d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8", "d9", "da", "db", "dc", "dd", "de", "df", "e0", "e1", "e2", "e3", "e4", "e5", "e6", "e7", "e8", "e9", "ea", "eb", "ec", "ed", "ee", "ef", "f0", "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "fa", "fb", "fc", "fd", "fe", "ff"
};

void crack(uint8_t *data_prefix, size_t data_prefix_len,
           const char *hash_prefix, size_t hash_prefix_len,
           size_t offset, const char *algo) {
  uint8_t digest[EVP_MAX_MD_SIZE], hexdigest[EVP_MAX_MD_SIZE*2];
  int digest_len;
  EVP_MD_CTX *ctx = EVP_MD_CTX_new();
  const EVP_MD *md = EVP_get_digestbyname(algo);

  for (uint32_t c1 = 0; c1 < 0x100; c1++) {
    for (uint32_t c2 = 0; c2 < 0x100; c2++) {
      for (uint32_t c3 = 0; c3 < 0x100; c3++) {
        for (uint32_t c4 = 0; c4 < 0x100; c4++) {
          EVP_DigestInit_ex(ctx, md, NULL);
          data_prefix[data_prefix_len+0] = c1;
          data_prefix[data_prefix_len+1] = c2;
          data_prefix[data_prefix_len+2] = c3;
          data_prefix[data_prefix_len+3] = c4;
          EVP_DigestUpdate(ctx, data_prefix, data_prefix_len+4);
          EVP_DigestFinal_ex(ctx, digest, &digest_len);

          for (size_t i = 0; i < digest_len; i++)
            *(uint16_t*)(&hexdigest[i*2]) = *(uint16_t*)(strtable[digest[i]]);

          if (memcmp(hexdigest + offset, hash_prefix, hash_prefix_len) == 0) {
            write(1, strtable[c1], 2);
            write(1, strtable[c2], 2);
            write(1, strtable[c3], 2);
            write(1, strtable[c4], 2);
            write(1, "\n", 1);
            exit(0);
          }
        }
      }
    }
  }
}

int main(void) {
  size_t data_prefix_len, hash_prefix_len, offset;
  uint8_t data_prefix[0x4000], data_prefix_hex[0x8000], hash_prefix[0x100], inp_algo[10];

  scanf("%s %s %lu %s", data_prefix_hex, hash_prefix, &offset, inp_algo);

  data_prefix_len = strlen(data_prefix_hex) / 2;
  for (size_t i = 0; i < data_prefix_len; i++)
    data_prefix[i] = hextable[data_prefix_hex[i*2+1]] | (hextable[data_prefix_hex[i*2]] << 4);

  hash_prefix_len = strlen(hash_prefix);
  for (size_t i = 0; i < hash_prefix_len; i++)
    hash_prefix[i] = tolower(hash_prefix[i]);

  char *algo = "sha256";
  if (strcmp(inp_algo, "md5") == 0) 
    algo = "md5";
  else if (strcmp(inp_algo, "sha512") == 0)
    algo = "sha512";

  crack(data_prefix, data_prefix_len, hash_prefix, hash_prefix_len, offset, algo);
  return 0;
}
