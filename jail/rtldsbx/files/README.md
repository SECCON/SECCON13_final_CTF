Source: https://ftp.gnu.org/gnu/glibc/glibc-2.39.tar.gz
Patch for `elf/rtld.c`:
```diff
1340a1341,1359
> static unsigned char __sbx_filter[] = {
>   32,0,0,0,4,0,0,0,21,0,0,5,62,0,0,192,32,0,0,0,0,0,0,0,53,0,3,0,0,0,0,64,21,0,2,0,59,0,0,0,21,0,1,0,66,1,0,0,6,0,0,0,0,0,255,127,6,0,0,0,0,0,0,0
> };
> static int
> __sbx_prctl(int op, unsigned long arg2, unsigned long arg3, unsigned long arg4, unsigned long arg5) {
>   asm (".intel_syntax noprefix\n"
>        "mov r8, %4\n"
>        "mov r10, %3\n"
>        "mov rdx, %2\n"
>        "mov rsi, %1\n"
>        "mov edi, %0\n"
>        "mov eax, 0x9d\n"
>        "syscall\n"
>        ".att_syntax\n"
>        : : "r"(op), "r"(arg2), "r"(arg3), "r"(arg4), "r"(arg5)
>        : "rax", "rcx", "rdi", "rsi", "rdx", "r10", "r8", "r9", "r11");
>   return 0;
> }
> 
1352a1372,1384
> 
>   // Sandbox!
>   struct prog {
>     unsigned short len;
>     unsigned char *filter;
>   } rule = {
>     .len = sizeof(__sbx_filter) >> 3,
>     .filter = __sbx_filter
>   };
>   if (__sbx_prctl (38, 1, 0, 0, 0) < 0)
>     _exit (1);
>   if (__sbx_prctl (22, 2, (unsigned long)&rule, 0, 0) < 0)
>     _exit (1);
```
