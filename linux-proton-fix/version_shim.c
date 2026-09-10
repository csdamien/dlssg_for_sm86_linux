/*
 * Forwarding shim for Wine's version.dll.
 *
 * Forwards the 8 real version.dll exports through to the original Wine
 * implementation (renamed to version_orig.dll, loaded from the same
 * directory), and adds one extra export, GetFileVersionInfoByHandle,
 * which the real Wine version.dll does not implement. This unblocks
 * callers that probe for that export's presence via GetProcAddress
 * without actually needing correct behavior from it (yet).
 *
 * All forwarders are declared with 5 generic 64-bit argument slots
 * (the maximum used by any real version.dll export, GetFileVersionInfoExA/W),
 * matching the Windows x64 calling convention where every integer/pointer
 * argument -- regardless of its real type -- occupies one register/stack
 * slot. Extra unused slots are harmless: the callee only reads as many
 * as its real signature needs.
 */
#include <windows.h>

typedef LONG_PTR (WINAPI *FN5)(LONG_PTR, LONG_PTR, LONG_PTR, LONG_PTR, LONG_PTR);

static HMODULE hOrig;
static FN5 pGetFileVersionInfoA;
static FN5 pGetFileVersionInfoW;
static FN5 pGetFileVersionInfoExA;
static FN5 pGetFileVersionInfoExW;
static FN5 pGetFileVersionInfoSizeA;
static FN5 pGetFileVersionInfoSizeW;
static FN5 pGetFileVersionInfoSizeExA;
static FN5 pGetFileVersionInfoSizeExW;
static FN5 pVerFindFileA;
static FN5 pVerFindFileW;
static FN5 pVerInstallFileA;
static FN5 pVerInstallFileW;
static FN5 pVerLanguageNameA;
static FN5 pVerLanguageNameW;
static FN5 pVerQueryValueA;
static FN5 pVerQueryValueW;

BOOL WINAPI DllMain(HINSTANCE inst, DWORD reason, LPVOID reserved)
{
    (void)inst; (void)reserved;
    if (reason == DLL_PROCESS_ATTACH)
    {
        hOrig = LoadLibraryA("version_orig.dll");
        if (hOrig)
        {
            pGetFileVersionInfoA     = (FN5)GetProcAddress(hOrig, "GetFileVersionInfoA");
            pGetFileVersionInfoW     = (FN5)GetProcAddress(hOrig, "GetFileVersionInfoW");
            pGetFileVersionInfoExA   = (FN5)GetProcAddress(hOrig, "GetFileVersionInfoExA");
            pGetFileVersionInfoExW   = (FN5)GetProcAddress(hOrig, "GetFileVersionInfoExW");
            pGetFileVersionInfoSizeA   = (FN5)GetProcAddress(hOrig, "GetFileVersionInfoSizeA");
            pGetFileVersionInfoSizeW   = (FN5)GetProcAddress(hOrig, "GetFileVersionInfoSizeW");
            pGetFileVersionInfoSizeExA = (FN5)GetProcAddress(hOrig, "GetFileVersionInfoSizeExA");
            pGetFileVersionInfoSizeExW = (FN5)GetProcAddress(hOrig, "GetFileVersionInfoSizeExW");
            pVerFindFileA      = (FN5)GetProcAddress(hOrig, "VerFindFileA");
            pVerFindFileW      = (FN5)GetProcAddress(hOrig, "VerFindFileW");
            pVerInstallFileA   = (FN5)GetProcAddress(hOrig, "VerInstallFileA");
            pVerInstallFileW   = (FN5)GetProcAddress(hOrig, "VerInstallFileW");
            pVerLanguageNameA  = (FN5)GetProcAddress(hOrig, "VerLanguageNameA");
            pVerLanguageNameW  = (FN5)GetProcAddress(hOrig, "VerLanguageNameW");
            pVerQueryValueA    = (FN5)GetProcAddress(hOrig, "VerQueryValueA");
            pVerQueryValueW    = (FN5)GetProcAddress(hOrig, "VerQueryValueW");
        }
    }
    return TRUE;
}

LONG_PTR WINAPI fwd_GetFileVersionInfoA(LONG_PTR a, LONG_PTR b, LONG_PTR c, LONG_PTR d, LONG_PTR e)
{ return pGetFileVersionInfoA ? pGetFileVersionInfoA(a, b, c, d, e) : 0; }

LONG_PTR WINAPI fwd_GetFileVersionInfoW(LONG_PTR a, LONG_PTR b, LONG_PTR c, LONG_PTR d, LONG_PTR e)
{ return pGetFileVersionInfoW ? pGetFileVersionInfoW(a, b, c, d, e) : 0; }

LONG_PTR WINAPI fwd_GetFileVersionInfoExA(LONG_PTR a, LONG_PTR b, LONG_PTR c, LONG_PTR d, LONG_PTR e)
{ return pGetFileVersionInfoExA ? pGetFileVersionInfoExA(a, b, c, d, e) : 0; }

LONG_PTR WINAPI fwd_GetFileVersionInfoExW(LONG_PTR a, LONG_PTR b, LONG_PTR c, LONG_PTR d, LONG_PTR e)
{ return pGetFileVersionInfoExW ? pGetFileVersionInfoExW(a, b, c, d, e) : 0; }

LONG_PTR WINAPI fwd_GetFileVersionInfoSizeA(LONG_PTR a, LONG_PTR b, LONG_PTR c, LONG_PTR d, LONG_PTR e)
{ return pGetFileVersionInfoSizeA ? pGetFileVersionInfoSizeA(a, b, c, d, e) : 0; }

LONG_PTR WINAPI fwd_GetFileVersionInfoSizeW(LONG_PTR a, LONG_PTR b, LONG_PTR c, LONG_PTR d, LONG_PTR e)
{ return pGetFileVersionInfoSizeW ? pGetFileVersionInfoSizeW(a, b, c, d, e) : 0; }

LONG_PTR WINAPI fwd_GetFileVersionInfoSizeExA(LONG_PTR a, LONG_PTR b, LONG_PTR c, LONG_PTR d, LONG_PTR e)
{ return pGetFileVersionInfoSizeExA ? pGetFileVersionInfoSizeExA(a, b, c, d, e) : 0; }

LONG_PTR WINAPI fwd_GetFileVersionInfoSizeExW(LONG_PTR a, LONG_PTR b, LONG_PTR c, LONG_PTR d, LONG_PTR e)
{ return pGetFileVersionInfoSizeExW ? pGetFileVersionInfoSizeExW(a, b, c, d, e) : 0; }

LONG_PTR WINAPI fwd_VerFindFileA(LONG_PTR a, LONG_PTR b, LONG_PTR c, LONG_PTR d, LONG_PTR e)
{ return pVerFindFileA ? pVerFindFileA(a, b, c, d, e) : 0; }

LONG_PTR WINAPI fwd_VerFindFileW(LONG_PTR a, LONG_PTR b, LONG_PTR c, LONG_PTR d, LONG_PTR e)
{ return pVerFindFileW ? pVerFindFileW(a, b, c, d, e) : 0; }

LONG_PTR WINAPI fwd_VerInstallFileA(LONG_PTR a, LONG_PTR b, LONG_PTR c, LONG_PTR d, LONG_PTR e)
{ return pVerInstallFileA ? pVerInstallFileA(a, b, c, d, e) : 0; }

LONG_PTR WINAPI fwd_VerInstallFileW(LONG_PTR a, LONG_PTR b, LONG_PTR c, LONG_PTR d, LONG_PTR e)
{ return pVerInstallFileW ? pVerInstallFileW(a, b, c, d, e) : 0; }

LONG_PTR WINAPI fwd_VerLanguageNameA(LONG_PTR a, LONG_PTR b, LONG_PTR c, LONG_PTR d, LONG_PTR e)
{ return pVerLanguageNameA ? pVerLanguageNameA(a, b, c, d, e) : 0; }

LONG_PTR WINAPI fwd_VerLanguageNameW(LONG_PTR a, LONG_PTR b, LONG_PTR c, LONG_PTR d, LONG_PTR e)
{ return pVerLanguageNameW ? pVerLanguageNameW(a, b, c, d, e) : 0; }

LONG_PTR WINAPI fwd_VerQueryValueA(LONG_PTR a, LONG_PTR b, LONG_PTR c, LONG_PTR d, LONG_PTR e)
{ return pVerQueryValueA ? pVerQueryValueA(a, b, c, d, e) : 0; }

LONG_PTR WINAPI fwd_VerQueryValueW(LONG_PTR a, LONG_PTR b, LONG_PTR c, LONG_PTR d, LONG_PTR e)
{ return pVerQueryValueW ? pVerQueryValueW(a, b, c, d, e) : 0; }

/* Not implemented by real Wine version.dll. Stubbed to return FALSE
 * (standard Win32 BOOL "operation failed" convention) so a caller that
 * actually invokes it -- rather than just checking it's non-NULL -- gets
 * a well-defined failure signal instead of executing garbage. */
BOOL WINAPI fwd_GetFileVersionInfoByHandle(LONG_PTR a, LONG_PTR b, LONG_PTR c, LONG_PTR d, LONG_PTR e)
{ (void)a; (void)b; (void)c; (void)d; (void)e; return FALSE; }
