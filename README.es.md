<!-- Traducción de README.md, sincronizada el 2026-08-09. El inglés es el canónico:
     al modificar README.md, actualice este archivo en el mismo cambio. -->

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/logo/oab-logo-on-dark.png">
  <img src="assets/logo/oab-logo-on-light.png" alt="OAB — Open Architecture Brain" width="420">
</picture>

**Inteligencia de arquitectura para agentes de código con IA.**

> Open knowledge. Open reasoning. Open architecture.

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Scenarios](https://img.shields.io/badge/scenarios-5%2F5%20passing-brightgreen.svg)](evaluations/)
[![Release](https://img.shields.io/badge/release-v0.1.7%20·%20M1-brightgreen.svg)](https://github.com/mhayk/oab/releases/tag/v0.1.7)

[English](README.md) · [Português (BR)](README.pt-BR.md) · **Español**

---

## El problema

Pídale a un agente de código que "diseñe una API escalable" y normalmente recibirá Kubernetes,
Kafka, Redis y tres microservicios — para un producto con 100 usuarios y un desarrollador.

El agente aprendió la *estética* del diseño de sistemas en charlas y artículos de blog, extraídos
casi por completo del 0,1% más grande de los sistemas. No aprendió la *economía*.

**100 usuarios con 40 peticiones por sesión son 0,28 peticiones por segundo.** Una sola instancia
tiene cuatro órdenes de magnitud de margen. OAB lo calcula, lo dice, y nombra la medición exacta
que cambiaría la respuesta.

## Qué hace OAB

| Comando | |
| :-- | :-- |
| `/oab:design` | Diseña un sistema proporcional a su escala medida |
| `/oab:review` | Revisa la arquitectura de este repositorio, ponderada por la escala a la que realmente opera |
| `/oab:capacity` | Planificación de capacidad con aritmética reproducible |
| `/oab:adr` | Registra una decisión con disparadores de revisión medibles |

Además, una skill de fondo que mejora la conversación *cotidiana* sobre arquitectura, no solo los
comandos explícitos.

## Instalación

```
/plugin marketplace add mhayk/oab
/plugin install oab@oab
```

![Instalando OAB — real, sin montaje](demo/out/install.gif)

Verificado de extremo a extremo: clon limpio en 0,8 s / 8,1 MB, y los ejemplos incluidos en el
repositorio contienen una ejecución real de `/oab:design` que pasa todas las aserciones de
escenario y una revisión real de un repositorio de terceros con todas las citas de evidencia
comprobadas ([`examples/live-run/`](examples/live-run/),
[`examples/live-review/`](examples/live-review/)). Una salvedad: los hooks de validación de
artefactos no se ejecutaron para plugins instalados desde el marketplace en sesiones headless
([#45](https://github.com/mhayk/oab/issues/45)); la validación a nivel de skill es el respaldo
hasta que eso se resuelva.

## Cómo se ve la salida

El corazón determinista — mismas entradas, mismos números, comprobables a mano
([`demo/`](demo/) guarda los tapes; nada está montado):

![El sobre de capacidad: supuestos, fórmula, cálculo, sensibilidad](demo/out/calculator.gif)

Y de [`examples/tiny-startup/`](examples/tiny-startup/) — 100 usuarios, £50/mes, dos
desarrolladores:

```
## Complexity: 4 / 4  — no headroom

| Component                    | Kind                  | Cost | Why                                    |
| Application instance         | application-runtime   |    1 | 0.28 peak RPS against a single          |
|                              |                       |      | instance leaves ~4 orders of magnitude  |
|                              |                       |      | of headroom.                            |
| Managed relational database  | relational-database   |    1 | 0.66 GB/year. Managed for tested        |
|                              |                       |      | point-in-time recovery, which a         |
|                              |                       |      | two-person team will not build.         |
```

**Qué se rechazó, y cuándo reconsiderarlo**

> **`cache`** — Con 0,24 lecturas/segundo en pico, no hay presión de lectura medida que aliviar.
> *Reconsiderar cuando: una sola consulta supere 10 peticiones/segundo por encima de 50 ms, o la
> CPU de la base de datos se mantenga por encima del 60% durante 3 días.*

> **`orchestration-platform`** — Tres veces el presupuesto de complejidad y cuatro veces el
> presupuesto económico, para un sistema con cuatro órdenes de magnitud de margen en una instancia.
> *Reconsiderar cuando: existan más de 4 servicios desplegables de forma independiente y haya un
> ingeniero de operaciones dedicado en el equipo.*

Esa segunda sección — lo que se consideró, se rechazó, y **la medición que revierte el rechazo** —
es la parte que un asistente genérico nunca produce.

## Cómo evita la sobreingeniería

Cada componente cuesta **puntos de complejidad**, y cada equipo tiene un presupuesto:

```
available = 4 + 1.5 × (engineers − 2) + 4 × dedicated_ops
```

Dos desarrolladores tienen 4 puntos. Una base de datos gestionada cuesta 1; una plataforma de
orquestación autogestionada cuesta 4. Por encima del presupuesto se **rechaza por defecto**, y una
excepción debe nombrar qué se elimina o quién operará el exceso.

A unas **£240 por punto al mes** en atención de ingeniería, autoalojar una base de datos para
ahorrar £250/mes cuesta alrededor de £720/mes. El servicio gestionado es más barato — y OAB lo dice
con aritmética, no con preferencia.

Es una heurística calibrada, no una ley — y la salida también lo dice.

## Pruebas, no promesas

Toda afirmación de OAB es sobre comportamiento, y las afirmaciones de comportamiento sin pruebas
son marketing.

| | |
| :-- | --: |
| Escenarios pasando | **5 / 5** |
| — guardas de sobreingeniería | 3 / 3 |
| — guardas de infraingeniería | 2 / 2 |
| Pruebas de las calculadoras | 43 |
| Fixtures de esquema (en ambos sentidos) | 33 |
| Unidades de conocimiento | 37 |

![La suite de escenarios con perturbación de magnitud](demo/out/evaluation.gif)

Las aserciones se ejecutan contra **campos del artefacto**, nunca contra prosa — un framework puede
ajustarse para producir palabras tranquilizadoras con mucha más facilidad que la estructura
correcta. Los escenarios también se perturban a 100× y 0,01× para demostrar que responden a la
magnitud en lugar de reconocer números concretos.

El escenario 07 es *"no hay que cambiar nada"*, y el escenario 08 es *"estos requisitos son
inconsistentes"*. Son las respuestas que un asistente ansioso nunca da.

## Qué no está construido todavía

Lista honesta: sin servidor MCP · sin generación del grafo de conocimiento · sin segunda
integración · `/oab:evolve` y los otros nueve comandos son M2 · ningún sitio más allá de una
landing page · 6 dominios de conocimiento, no 18.

Vea el [ROADMAP.md](ROADMAP.md) y el [§32 del diseño](docs/design/07-roadmap-and-risks.md#32-overengineering-review)
— una crítica a nuestro propio brief fundacional.

## Contribuir

**La contribución de mayor valor es conocimiento de arquitectura, y no exige entender nada del
código** — copie una plantilla, rellénela, abra un pull request.

→ [docs/contributing/knowledge.md](docs/contributing/knowledge.md)

Engine, integraciones y evaluación: [CONTRIBUTING.md](CONTRIBUTING.md).

## Apoyo

OAB es gratuito, local-first, y no tiene servicio alojado que monetizar. Si se gana un lugar en su
flujo de trabajo, [patrocinar](https://github.com/sponsors/mhayk) financia la parte sin glamur:
mantener 37 unidades de conocimiento revisadas y al día, las ejecuciones de evaluación y el
dominio.

## Licencia

[Apache-2.0](LICENSE). El nombre y el logo de OAB son marcas y no están cubiertos por esa
licencia — vea el [NOTICE](NOTICE).

[oab.run](https://oab.run/es/) · [Propuesta de diseño](docs/design/) · [Ejemplos](examples/)
