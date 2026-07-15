# Modelo de amenazas — THEKEY 0.2.0

> Versión en inglés: [THREAT_MODEL.en.md](THREAT_MODEL.en.md)

Este documento es honesto y técnico; no hace afirmaciones absolutas sobre la
seguridad de THEKEY. THEKEY es un núcleo pequeño para transacciones Git
gobernadas.

## Objetivos de seguridad (realistas)

- Que un cambio de código automatizado sea **reproducible y auditable**.
- Que la fuente original no se modifique nunca (aislamiento de flujo de
  trabajo).
- Que una puerta obligatoria fallida detenga la liberación de forma
  determinista.
- Que la evidencia permita detectar manipulación posterior.

## Activos protegidos

- La fuente original del proyecto bajo cambio (solo lectura para THEKEY).
- Los artefactos de evidencia por ejecución (`runs/<RUN_ID>/`).
- El event store encadenado por hash (`.thekey/`).
- La política de puertas (`governance/policies/`).

## Fronteras de confianza

- **Dentro:** el proceso THEKEY, el workspace aislado, la política local.
- **Fuera:** el sistema anfitrión, otros procesos, la red, el usuario que
  ejecuta la demo, proveedores externos (p. ej. NPSC como adaptador).

THEKEY confía en que el sistema anfitrión no está comprometido. Ese límite está
fuera de su alcance.

## Superficie de ataque relevante

- Manipulación de la política o de los parámetros de ejecución.
- Escritura fuera del workspace aislado (escapada de ruta).
- Alteración de artefactos de evidencia tras la ejecución.
- Inyección a través del adaptador de solo lectura (entrada no confiable).
- Configuración incorrecta del entorno (Python, permisos, `PATH`).

## Amenazas plausibles

- **T1 — Escritura fuera del workspace:** un defecto de ruta podría escribir
  fuera del espacio aislado. Mitigación actual: el gestor de workspace
  autoriza rutas relativas al workspace; la fuente original no se toca por
  diseño.
- **T2 — Falsificación de evidencia:** un actor con acceso al disco podría
  reescribir artefactos. Mitigación actual: hashes SHA-256 y event store
  encadenado; la verificación (`thekey evidence verify`) detecta
  discrepancias. No es a prueba de un atacante con control total del disco.
- **T3 — Política débil:** una política mal configurada podría relajar
  puertas. Mitigación actual: las puertas se declaran explícitamente y una
  obligatoria no se compensa. Sigue dependiendo de la política cargada.
- **T4 — Entrada no confiable vía adaptador:** un adaptador de solo lectura
  podría recibir datos manipulados. Mitigación actual: el adaptador es de
  solo lectura y no ejecuta el proveedor; la validación de entrada es
  responsabilidad del consumidor.

## Mitigaciones presentes

- Aislamiento de flujo de trabajo (workspace controlado).
- Autorización de política determinista (hash del plan, sin aprobación
  interactiva).
- Event store de solo adición y encadenado por hash.
- Hashes SHA-256 de artefactos principales.
- Escaneo de secretos limitado y honesto sobre el workspace.
- Verificación reproducible de build + tests en aislamiento.

## Mitigaciones aún no presentes

- Identidades humanas criptográficas.
- Aislamiento de procesos mediante container o VM (aún no implementado).
- Concurrencia multi-desarrollador con bloqueo.
- Escaneo de secretos exhaustivo (no es un sustituto de herramientas
  dedicadas).
- Firma de evidencia con clave externa.

## Limitaciones explícitas

THEKEY **no proporciona sandboxing a nivel de sistema operativo**. El
aislamiento es de **flujo de trabajo**: el código se ejecuta en el mismo
sistema anfitrión que el usuario. No debe presentarse como un límite de
seguridad del sistema operativo.

## Relación entre aislamiento de flujo de trabajo y ausencia de sandbox de SO

El aislamiento de flujo de trabajo protege la **fuente original** y acota
**dónde se escriben los cambios**. No aísla el proceso del sistema operativo:
un workspace comprometido comparte los privilegios del usuario que ejecuta
THEKEY. Quien necesite aislamiento de SO debe ejecutar THEKEY dentro de su
propio sandbox (container, VM, cuenta restringida).

## Integridad de la evidencia y sus supuestos

La integridad se basa en:
- que el event store y los artefactos no fueron alterados tras la ejecución;
- que los hashes se calcularon sobre el contenido real;
- que la política aplicada es la esperada.

Si un atacante controla el disco o la política, la evidencia puede ser
regenerada coherentemente y la detección falla. Por eso la evidencia es
**auditable**, no **a prueba de manipulación absoluta**.

## Amenazas del adaptador de solo lectura opcional

NPSC y otros adaptadores externos son de solo lectura y opcionales. No forman
parte del núcleo. Una amenaza es que un adaptador mal escrito inyecte datos en
la entrada del núcleo. Mitigación: el adaptador no ejecuta el proveedor y el
núcleo valida lo que consume. NPSC no se integra en el núcleo.

## Riesgos por configuración incorrecta

- Ejecutar THEKEY con privilegios de administrador innecesarios.
- Usar una política que omita puertas obligatorias.
- No revisar el escaneo de secretos antes de liberar.
- Mezclar el estado de ejecución (`.thekey/`, `runs/`) con el control de
  versiones del proyecto.

## Riesgos residuales

- Dependencia de la integridad del sistema anfitrión.
- Identidad de autorización local simplificada.
- Cobertura de escaneo de secretos limitada.
- Sin garantía frente a un atacante con control total del entorno.

## Fuera de alcance

- Aislamiento de procesos a nivel de sistema operativo mediante container o VM.
- Autorización enterprise.
- Ejecución remota de agentes.
- Integración de NPSC en el núcleo.

## Referencias

- [SECURITY.md](SECURITY.md)
- [README.md](README.md)
