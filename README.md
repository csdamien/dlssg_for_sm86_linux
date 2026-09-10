# DLSSG-SM86 on Linux / Proton

> **This fork exists for one purpose: getting `dlssg_for_sm86` working under Wine/Proton on Linux.**
> For the actual mod — the `version.dll` proxy, `dlssg_sm86.ini`, Windows install steps, releases,
> and everything else — go to the original repo:
>
> **[sdli1995/dlssg_for_sm86](https://github.com/sdli1995/dlssg_for_sm86)**
>
> Install it there first, exactly as documented. Come back here only once you've hit the crash
> described below.

## The problem

Install the mod's `version.dll` on Linux (any Proton flavor, or vanilla Wine) and the game exits
immediately. `PROTON_LOG=1` shows:

```
Loaded ...\bin\x64\VERSION.dll ... native
Loaded C:\windows\system32\version.dll ... builtin
err:module:loader_init "VERSION.dll" failed to initialize, aborting
Initializing dlls for ...\<Game>.exe failed, status c0000142
```

No `dlssg_sm86/logs` directory ever gets created — the proxy fails before its own logger opens.

### Why

Traced with `WINEDEBUG=+relay,+seh,+module`. The proxy's `DllMain` looks up a function called
`GetFileVersionInfoByHandle` on the real system `version.dll`:

```
Call KERNEL32.GetProcAddress(hVersionDll, "GetFileVersionInfoByHandle")
warn:module:LdrGetProcedureAddress "GetFileVersionInfoByHandle" not found in "version.dll"
Ret  KERNEL32.GetProcAddress() retval=00000000
  9× RtlDeleteCriticalSection, 2× FlsFree   ← a teardown path, not forward progress
Ret  PE DLL (VERSION.dll, PROCESS_ATTACH) retval=0
err:module:loader_init "VERSION.dll" failed to initialize, aborting
```

`GetFileVersionInfoByHandle` doesn't exist in **any** Wine build — checked directly via PE export
tables on CachyOS Proton, GE-Proton (10-25 through 10-34), Valve's own Proton 8.0/9.0/10.0/Experimental,
vanilla upstream WineHQ 11.0, and a staging+TKG patched build (11.17). All of them export only the
classic set: `GetFileVersionInfo{A,W,ExA,ExW}` and `GetFileVersionInfoSize{A,W,ExA,ExW}`. Switching
Proton flavors won't fix this — it's a gap in Wine itself, not a packaging bug in any one build.

## The fix

A small forwarding shim stands in for `version.dll`. It passes all 16 real exports straight through
to Wine's actual implementation (kept alongside it, renamed) and adds the one missing export as a
harmless stub. The proxy only checks that the function *exists* at load time — it never needs to
behave correctly to get past the check.

Source, `.def` file, a precompiled binary, and checksums are in [`linux-proton-fix/`](linux-proton-fix/).

**Scope:** installed into one Wine prefix's `system32` folder only. Your Proton installation itself
is never touched — other games and prefixes on the same Proton build are unaffected, and it's two
file deletions to undo.

Confirmed working: RTX 3090, CachyOS Proton, Cyberpunk 2077, DLSSG Native 0.2.3 — sustained live 2×
frame generation through a full play session, verified via the proxy's own event log.

## Steps

### 1. Get the shim

It's a plain, portable Windows DLL — nothing about it is tied to a particular machine, Wine build,
or GPU. It only ever calls `LoadLibraryA` / `GetProcAddress` on `kernel32.dll`.

**Path A — use the prebuilt copy (easiest).** Grab
[`linux-proton-fix/version.dll`](linux-proton-fix/version.dll) directly. Verify it against
[`linux-proton-fix/SHA256SUMS`](linux-proton-fix/SHA256SUMS):

```
2f6978f6c311412fdc1a1582fcd83bc33314e37bd9fd837da83968f4d61c4539  version.dll
```

**Path B — build it yourself**, if you'd rather not run someone else's binary inside your game
process. Takes a few minutes with a disposable container, nothing installs on your host:

```bash
podman run --rm -it -v "$PWD":/work -w /work registry.fedoraproject.org/fedora:42 bash
dnf install -y mingw64-gcc
```

Grab [`linux-proton-fix/version_shim.c`](linux-proton-fix/version_shim.c) and
[`linux-proton-fix/version_shim.def`](linux-proton-fix/version_shim.def), then, inside the
container:

```bash
x86_64-w64-mingw32-gcc -shared -O2 -o version.dll version_shim.c version_shim.def
```

Produces a `version.dll` a few dozen KB in size — the same file Path A gives you.

### 2. Find your prefix

For a Steam/Proton game this is `steamapps/compatdata/<AppID>/pfx/drive_c/windows/system32/`. The
AppID is the number in the game's Steam store URL.

### 3. Swap in the shim

With the game fully closed, in that `system32` folder:

```bash
# keep Wine's real implementation around under a new name
cp -L version.dll version_orig.dll
# replace the original (often a symlink) with the shim from step 1
rm version.dll
cp /path/to/version.dll .
```

`version.dll` is frequently a symlink into your Proton installation's own files, not a real file in
the prefix — `cp -L` follows it and copies the actual bytes, which is what you want.

### 4. Set the DLL override

The proxy needs Wine to prefer the on-disk (`native`) `version.dll` over its own builtin, for this
game specifically. Via `protontricks`, `winecfg`, or a direct registry edit, set:

```
version = native,builtin
```

If editing `pfx/user.reg` directly, make sure no Wine/Proton process is attached to the prefix
first — a live `wineserver` holds the registry in memory and can silently overwrite a manual edit
on exit.

### 5. Launch and verify

Start the game. If your Proton build has an opt-in native CUDA bridge (CachyOS Proton needs
`PROTON_NVIDIA_NVCUDA=1` in launch options, for example), make sure it's set — without it, the
driver-connection step below fails even with the shim in place.

Check the proxy's own log, written next to the game executable at `bin/x64/dlssg_sm86/logs/*.jsonl`:

| See this | Means |
|---|---|
| the log file exists at all | fixed — the `c0000142` abort is gone |
| `"event":"ngx_driver_connected"` | connected to the NVIDIA driver, past the old wall |
| `"event":"evaluate"`, repeating | live frame generation, once enabled in-game |

In-game, a DLSS Frame Generation option should now appear in Graphics settings. Enable it, restart
when prompted, and the log's `generated_count` field tells you the multiplier: `1` is 2×, `2` is 3×,
`3` is 4×.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Still `c0000142` right after `VERSION.dll` loads | Shim isn't actually loading. Confirm `system32/version.dll` is the compiled file, not a leftover symlink — `file version.dll` should say `PE32+ executable`, not `symbolic link`. |
| A *different* export now logs "not found" | Forwarder table is incomplete for your setup. Add that export to both `version_shim.c` and `version_shim.def`, following the existing pattern, and recompile. |
| No frame-gen toggle appears in-game | Separate, game-specific issue — several upstream reports describe this happening even on native Windows for certain titles. Not something this shim addresses. |
| `ngx_driver_connected` never appears | CUDA driver isn't reachable. Check your Proton build's CUDA-bridge launch option, and confirm the game isn't running inside a container/sandbox that hides the NVIDIA driver libraries from the process. |

---

This shim is an independent, unofficial workaround — not written or endorsed by the mod's author.
Discussion: [upstream issue #10](https://github.com/sdli1995/dlssg_for_sm86/issues/10).
