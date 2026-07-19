# Registro de contribución — OpenAI Build Week 2026
`VERIFIED_PREEXISTING` exige evidencia anterior al corte;
`VERIFIED_BUILD_WEEK`, evidencia posterior; `VERIFIED_THIS_CODEX_SESSION`,
implementación verificada en este hilo; `PROVENANCE_UNRESOLVED`, evidencia
insuficiente.
El propietario afirma que THEKEY existía antes del evento, pero el repositorio
público nació el 15 de julio de 2026 y el primer commit visible es
`b7b6c32cf3a2621d29ef2c5856db50d116d8dff6`. Por ello, la historia previa sigue
`PROVENANCE_UNRESOLVED`. El ciclo, workspaces, gates, policy loader, evidencia,
CLI y demo ya estaban en el baseline `3a8456416ed9ae9183840585b488cec04e9a069d`.
`VERIFIED_THIS_CODEX_SESSION`: contratos estrictos; doble recibo persistido;
guard físico limitado a EXECUTOR; PolicyEngine productivo; 5/5 callers con
contexto; procedencia y hash de estado; tests y schemas; Judge Mode con ALLOW
de un handler, DENY de cero handlers, cuatro gates, evidencia JSON y rutas con
espacios; documentación bilingüe y material Devpost.
Codex ejecutó inspección, diseño adversarial, implementación, AST, TDD,
regresión, rollback y documentación. moli conservó las decisiones sobre
autoridad, scope, LIVE_E, publicación y envío.
Pendiente: `/feedback` `PENDING_REAL_FEEDBACK_SESSION_ID`; GPT-5.6
`PENDING_SESSION_METADATA_VERIFICATION`; YouTube `PENDING_PUBLIC_YOUTUBE_URL`.
No se afirma integración runtime con GPT-5.6. Es aislamiento de workflow, no
sandbox de SO. El grant local queda fijado a ruta/hash del demo canónico y al
workspace aislado, con reutilización productiva denegada; no es firma
criptográfica. El secret scan es limitado.
