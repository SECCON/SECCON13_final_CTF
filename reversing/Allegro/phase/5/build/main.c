#include <stdio.h>
#include <lua.h>
#include <lualib.h>
#include <lauxlib.h>

#define INC_BIN(sect, file, sym) asm (          \
    ".section " #sect "\n"                      \
    ".balign 8\n"                               \
    ".global " #sym "\n"                        \
    #sym ":\n"                                  \
    ".incbin \"" file "\"\n"                    \
    ".global _sizeof_" #sym "\n"                \
    ".set _sizeof_" #sym ", . - " #sym "\n"     \
    ".balign 8\n"                               \
    ".section \".text\"\n")                     \

INC_BIN(".rodata", "main.luac", bytecode);
extern const char bytecode[];
extern const int _sizeof_bytecode;

int main() {
  size_t n;
  long long v;
  lua_State *L = luaL_newstate();
  if (L == NULL) return 1;

  if (luaL_loadbuffer(L, (const char *)bytecode, _sizeof_bytecode, "embedded")
      || lua_pcall(L, 0, LUA_MULTRET, 0))
    goto out;

  scanf("%lu", &n);

  lua_getglobal(L, "G");
  lua_getglobal(L, "F");
  lua_getglobal(L, "F");

  lua_createtable(L, n, 0);
  for (size_t i = 0; i < n; i++) {
    lua_createtable(L, n, 0);
    for (size_t j = 0; j < n; j++) {
      scanf("%lld", &v);
      lua_pushinteger(L, v);
      lua_rawseti(L, -2, j + 1);
    }
    lua_rawseti(L, -2, i + 1);
  }

  lua_createtable(L, n, 0);
  for (size_t i = 0; i < n; i++) {
    lua_createtable(L, n, 0);
    for (size_t j = 0; j < n; j++) {
      scanf("%lld", &v);
      lua_pushinteger(L, v);
      lua_rawseti(L, -2, j + 1);
    }
    lua_rawseti(L, -2, i + 1);
  }

  if (lua_pcall(L, 2, 1, 0) != LUA_OK)
    goto out;
  lua_pushvalue(L, -1);
  if (lua_pcall(L, 2, 1, 0) != LUA_OK)
    goto out;
  if (lua_pcall(L, 1, 1, 0) != LUA_OK)
    goto out;

  for (size_t i = 0; i < n; i++) {
    lua_rawgeti(L, -1, i + 1);
    printf("[");
    for (size_t j = 0; j < n; j++) {
      lua_rawgeti(L, -1, j + 1);
      if (j == n - 1){
        printf("%lld", lua_tointeger(L, -1));
      } else {
        printf("%lld, ", lua_tointeger(L, -1));
      }
      lua_pop(L, 1);
    }
    printf("]\n");
    lua_pop(L, 1);
  }

 out:
  lua_close(L);
  return 0;
}
