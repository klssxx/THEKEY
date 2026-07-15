$ErrorActionPreference = 'Stop'
$GH = "C:/Program Files/GitHub CLI/gh.exe"
$Dir = "E:\PROYECTS\GovernedOSS\release_evidence\issue_bodies"
for ($n = 1; $n -le 8; $n++) {
    $body = Get-Content -Raw -Path "$Dir\$n.md"
    & $GH issue edit $n --repo klssxx/THEKEY --body $body 2>&1 | Out-Null
    # verificar
    $got = & $GH issue view $n --repo klssxx/THEKEY --json body 2>$null | python -c "import sys,json; b=json.load(sys.stdin)['body']; print('len='+str(len(b)), 'Requisito='+str('Requisito' in b), 'verifica='+str('Cómo se verifica' in b), 'eventstore='+str('event store' in b))"
    Write-Host "#$n -> $got"
}
