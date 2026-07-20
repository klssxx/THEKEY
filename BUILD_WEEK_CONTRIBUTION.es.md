# Registro de contribución — OpenAI Build Week 2026
`CLAIM_RECORDED` identifica una declaración del propietario;
`PENDING_EVIDENCE_IMPORT`, material todavía no importado;
`VERIFIED_GIT_OBJECT`, un objeto Git comprobable; y
`VERIFIED_THIS_CODEX_SESSION`, implementación verificada en este hilo.
THEKEY se declara explícitamente como proyecto preexistente. La declaración
pre-pública queda `CLAIM_RECORDED`. El historial Git público accesible empieza
con `b7b6c32cf3a2621d29ef2c5856db50d116d8dff6`, fechado el 15 de julio de 2026,
después del corte. Chats, backups o snapshots anteriores no importados quedan
`PENDING_EVIDENCE_IMPORT`. El ciclo, workspaces, gates, policy loader,
evidencia, CLI y demo ya estaban en el baseline
`3a8456416ed9ae9183840585b488cec04e9a069d`. Consulta la
[declaración de procedencia](docs/build-week/PRE_PUBLIC_PROVENANCE.md) y el
[delta verificable](docs/build-week/BUILD_WEEK_DELTA.md).
`VERIFIED_THIS_CODEX_SESSION`: contratos estrictos; doble recibo persistido;
guard físico limitado a EXECUTOR; PolicyEngine productivo; 5/5 callers con
contexto; procedencia y hash de estado; tests y schemas; Judge Mode con ALLOW
de un handler, DENY de cero handlers, cuatro gates, evidencia JSON y rutas con
espacios; aplicación portable Windows 10/11 x64 con interfaz bilingüe, icono de
rey y apertura propiedad del autor; inspección de solo lectura y verificación
aislada de proyectos Python, Node.js, Go, Rust, .NET y Maven reconocidos con CHECKMATE, PolicyEngine,
consentimiento explícito, checks/tests fijos por adaptador, escaneo limitado, documentación y
prueba de origen intacto; diagnósticos redactados; reparación automática
acotada de un punto, aceptada solo tras todos los gates; autorización separada
para aplicar los bytes verificados; protección contra baseline obsoleto,
backup, reverificación y rollback; documentación bilingüe, verificador de
evidencia y material Devpost.
Codex ejecutó inspección, diseño adversarial, implementación, AST, TDD,
regresión, rollback y documentación. usuario conservó las decisiones sobre
autoridad, scope, LIVE_E, publicación y envío.
Evidencia: `/feedback` `019f79f2-6a7e-74f0-b1fa-d65335b29a7c`; registro
saneado en
[docs/build-week/CODEX_SESSION_EVIDENCE.md](docs/build-week/CODEX_SESSION_EVIDENCE.md).
Índice público:
[evidence/build-week/provenance/PUBLIC_EVIDENCE_INDEX.json](evidence/build-week/provenance/PUBLIC_EVIDENCE_INDEX.json).
Pendiente: YouTube `PENDING_PUBLIC_YOUTUBE_URL`. No se afirma integración
runtime con GPT-5.6. Es aislamiento de workflow, no
sandbox de SO. El grant local queda fijado a ruta/hash del demo canónico y al
workspace aislado, con reutilización productiva denegada; no es firma
criptográfica. El secret scan es limitado.
La superficie portable se prueba en Windows 11 y tiene como objetivo Windows
10/11 x64. Los tests elegidos son código de confianza y no se ejecutan en un
sandbox del SO; no se instalan dependencias y un proyecto no compatible o sin
evidencia suficiente nunca se presenta como verificado.
La reparación automática no cambia tests ni instala dependencias. Los fallos
fuera de su conjunto cerrado permanecen bloqueados y se entregan como
diagnóstico, sin afirmar una reparación arbitraria.
