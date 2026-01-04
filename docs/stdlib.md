# Jusu++ Standard Library (Minimal)

This document describes the minimal standard library provided in `runtime/stdlib.py`.

Provided modules:
- `math` — `pi`, `sqrt`, `sin`
- `json` — `loads`, `dumps`
- `time` — `now()`
- `random` — `rand()`

Usage examples:

```
val = math.sqrt(9)
js = json.dumps({'a':1})
```

Next steps:
- Data science utils: optional `np` (NumPy) and `pd` (Pandas) modules — available when packages are installed ✅
- Web helpers: `http.get(url)` with async `http.async_get(url)` when `aiohttp` is installed. Use `http.get` for simple scripts and `http.async_get` inside async code. ✅
- Add file / OS helpers and IO module

Usage examples:

```
arr = np.array([1,2,3])
print(np.mean(arr))
# If pandas is installed
df = pd.DataFrame({'a':[1,2,3]})
print(df.head())
```
