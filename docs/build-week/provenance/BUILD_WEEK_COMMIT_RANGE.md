# Build Week reachable commit range

There is no reachable Git base commit before `2026-07-13T16:00:00Z`. The earliest reachable object is `b7b6c32cf3a2621d29ef2c5856db50d116d8dff6` (2026-07-15).

Reproduce the accessible history and changes with:

```powershell
git log --date=iso-strict b7b6c32cf3a2621d29ef2c5856db50d116d8dff6..HEAD
git diff --stat b7b6c32cf3a2621d29ef2c5856db50d116d8dff6..HEAD
git diff --name-status b7b6c32cf3a2621d29ef2c5856db50d116d8dff6..HEAD
```

For the core technical extension presented to judges, the bounded comparison is `3a8456416ed9ae9183840585b488cec04e9a069d..HEAD`; see [BUILD_WEEK_DELTA.md](../BUILD_WEEK_DELTA.md). This is a Build Week baseline, not a verified pre-period base.
