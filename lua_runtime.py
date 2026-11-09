"""Isolated Lua loader using the installed client runtime; no game libraries are shipped."""
import ctypes, os
class Lua:
    def __init__(self,plugins):
        self.directory=os.add_dll_directory(str(plugins))
        self.lib=ctypes.CDLL(str(plugins/'tolua.dll'))
        L=self.lib
        L.luaL_newstate.restype=ctypes.c_void_p
        L.luaL_openlibs.argtypes=[ctypes.c_void_p]
        L.luaL_loadbufferx.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_char_p,ctypes.c_char_p];L.luaL_loadbufferx.restype=ctypes.c_int
        L.lua_pcallk.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_ssize_t,ctypes.c_void_p];L.lua_pcallk.restype=ctypes.c_int
        L.lua_tolstring.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.POINTER(ctypes.c_size_t)];L.lua_tolstring.restype=ctypes.c_void_p
        L.lua_settop.argtypes=[ctypes.c_void_p,ctypes.c_int];L.lua_close.argtypes=[ctypes.c_void_p]
        self.state=L.luaL_newstate();assert self.state;L.luaL_openlibs(self.state)
    def run(self,source,execute=True):
        b=source.encode('utf-8');buf=ctypes.create_string_buffer(b)
        rc=self.lib.luaL_loadbufferx(self.state,buf,len(b),b'@AkagiPlus-local-test',b't')
        if rc==0 and execute:rc=self.lib.lua_pcallk(self.state,0,0,0,0,None)
        if rc:
            n=ctypes.c_size_t();ptr=self.lib.lua_tolstring(self.state,-1,ctypes.byref(n));msg=ctypes.string_at(ptr,n.value).decode('utf-8',errors='replace')
            raise AssertionError(msg)
        self.lib.lua_settop(self.state,0)
    def close(self):self.lib.lua_close(self.state);self.directory.close()
