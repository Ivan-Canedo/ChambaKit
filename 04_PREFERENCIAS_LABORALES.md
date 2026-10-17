# 04 — Preferencias laborales

**Versión:** 1.0 — 2026-10-17 — Plantilla inicial.
**Estado:** plantilla sin llenar. Lo llena el paso 4 de `/configurar` (Preferencias) con las respuestas del titular; el bloque de PREF-UBICACION no trae valores.

## PREF-USO — Interpretación

- **Autoridad:** este archivo manda sobre condiciones deseadas; `02_PERFIL_MAESTRO.md`, sobre trayectoria. Aspirar a un puesto no acredita experiencia en él.
- **Fuerza de cada criterio:** distinguir preferencia de condición indispensable. Solo una condición indispensable excluye vacantes (08/EVAL-CONDICIONES). Un criterio pendiente no es aceptación ni filtro de descarte.
- **Situación actual:** la residencia, modalidad y contratación actuales no determinan preferencias futuras.
- **Sin ponderación:** no asignar pesos ni puntuaciones; el método va en `08_EVALUACION_DE_VACANTES.md`.
- **Fuentes y vigencia:** cada decisión cita su declaración (`[PREF-U03]`, ver PREF-FUENTES) y vale desde su fecha. Ningún valor sale de la plantilla ni de una sugerencia del agente.
- **Opiniones sobre el mercado:** lo que el titular piense del mercado (por ejemplo, cuánta competencia hay en una modalidad) se registra como suyo, no como hallazgo. No se convierte en cuota de esfuerzo ni en exclusión salvo que él lo pida.

## PREF-FUNCIONES — Dirección profesional

Rutas que el titular quiere considerar: seguir en su función actual o cambiar de enfoque o de carrera, con el alcance que declare y sus límites frente a 02. Se anota si hay orden entre ellas; si no lo hay, no se fuerza. 05 construye las familias de roles desde estas rutas.

| Ruta | Interés declarado | Alcance y límites |
| --- | --- | --- |
| «pendiente» | | |

**Nivel y transición:** «pendiente»: nivel al que aspira, si es un mínimo o una aspiración, y qué acepta en una transición (otro nivel, otro sueldo). Una aspiración no acredita el nivel actual.

## PREF-TIPOS — Tipos de puesto excluidos

Tipos de puesto que el titular no acepta aunque coincidan con sus rutas, como prácticas, puestos para recién egresados u otros que él nombre. Cada tipo excluido es la condición «Tipo de puesto» de 08, y la búsqueda (07) no gasta trabajo en esas vacantes. Si no excluye ninguno, la tabla dice «Ninguno» y la condición no se aplica.

| Tipo excluido | Cómo se reconoce en un anuncio | Fuente |
| --- | --- | --- |
| «pendiente» | | |

«Cómo se reconoce» lleva los términos del título o del anuncio que lo delatan, en los idiomas de los anuncios, y los requisitos que lo implican (por ejemplo, estar inscrito como estudiante).

## PREF-UBICACION — Región, zona horaria y moneda

Dónde acepta trabajar el titular y desde dónde acepta vacantes remotas. Los lugares de `localidades` son su región. El bloque de abajo es la única autoridad de su región, el alcance del remoto, su zona horaria y su moneda: lo lee el script de búsqueda (07) y lo aplican las condiciones de 08. No trae valores: el paso 4 de `/configurar` lo llena con lo que declare el titular. Un script que lo encuentre sin llenar se detiene con un mensaje.

```json
{
  "paises": {},
  "localidades": [],
  "remoto": {
    "alcance": null,
    "paises": []
  },
  "zona_horaria": null,
  "moneda": null
}
```

**Campos del bloque:**

| Campo | Qué lleva |
| --- | --- |
| `paises` | Cada país que nombran `localidades` o `remoto.paises`. La clave es su código ISO 3166-1 alfa-2, en mayúsculas; el valor, la lista de nombres con que lo escriben los anuncios: en español, en inglés y en otro idioma si sus portales lo usan |
| `localidades` | Un grupo por cada lugar donde el titular acepta trabajo presencial o híbrido: una ciudad, varias, una zona metropolitana, una división del país o el país completo. Lista vacía si solo busca remoto |
| `localidades[].pais` | Código del país del grupo, clave de `paises` |
| `localidades[].divisiones` | El estado, provincia, departamento u otra división del país que contiene el grupo, con sus abreviaturas usuales. Vacía si el grupo es el país completo o si las localidades no necesitan división para reconocerse |
| `localidades[].zona` | Nombre de la zona metropolitana que nombró el titular, como referencia; `null` si no nombró una. No se usa para comparar: si los anuncios escriben la zona como ubicación, ese nombre va también en `nombres` |
| `localidades[].nombres` | Las localidades aceptadas (ciudad, municipio, comuna, distrito o como se llamen en ese país), cada una con las formas en que la escriben los anuncios, como su nombre corto o en inglés. Vacía si el grupo acepta toda su división o todo el país |
| `remoto.alcance` | `"ninguno"` si no acepta remoto; `"paises"` si acepta vacantes remotas de los países de `remoto.paises`; `"cualquiera"` si las acepta de cualquier país |
| `remoto.paises` | Códigos de `paises`, solo con el alcance `"paises"`; vacía con los otros dos |
| `zona_horaria` | La de su residencia (02 §2), con su nombre IANA (`Región/Ciudad`); si la residencia cambia, se revisa. Da las fechas de los registros y la hora de la ventana de jornada (PREF-JORNADA) |
| `moneda` | Código ISO 4217, de tres letras, de la moneda en que declara su sueldo (PREF-COMPENSACION) |

**Cómo se lee un grupo de `localidades`:**

- **Con `nombres`:** acepta solo esas localidades. Una ubicación que nombra una de sus `divisiones`, o solo su país, sin nombrar ninguna localidad aceptada queda por revisar, porque puede estar dentro.
- **Sin `nombres`, con `divisiones`:** acepta cualquier localidad de esas divisiones. Una ubicación que solo nombra el país queda por revisar.
- **Sin `nombres` ni `divisiones`:** acepta cualquier localidad del país.

Una ubicación por revisar no se descarta: el script la señala con una línea «revisar» (07). Cada nombre coincide si aparece en la ubicación como palabra o frase completa, sin distinguir mayúsculas ni acentos, así que esas variantes no se repiten; las de idioma o abreviatura, sí.

**Reglas del bloque:**

- `remoto.alcance`, `zona_horaria` y `moneda` no pueden quedar en `null`.
- Con `localidades` vacía, el alcance no puede ser `"ninguno"`: no habría nada que buscar.
- Cada `pais` de `localidades` y cada código de `remoto.paises` es una clave de `paises`.
- Los lugares son los que nombró el titular, con el alcance con que los nombró: si nombró una ciudad, va solo la ciudad; si nombró una zona metropolitana, las localidades que confirmó al desglosarla.
- El bloque cuadra con PREF-MODALIDAD: si el titular acepta presencial o híbrido, `localidades` tiene al menos un grupo; si acepta remoto, el alcance no es `"ninguno"`.

**Fuera del bloque:**

- **Traslados:** «pendiente»: límite de tiempo o distancia dentro de su región, si lo hay. Si no lo hay, no se inventa.
- **Reubicación:** «pendiente»: si la acepta, hacia dónde y en qué condiciones.
- **Remoto:** en cada vacante remota se comprueba que permita trabajar desde la residencia del titular (02 §2); la etiqueta «remoto» no basta.

## PREF-EJEMPLOS — Cómo se llena el bloque de región

Casos con nombres ficticios y los códigos `XA` y `XB`, que la norma ISO reserva y no son países. Muestran solo los campos de región; `zona_horaria` y `moneda` se llenan igual en todos.

**Solo remoto, desde cualquier país:**

```json
{
  "paises": {},
  "localidades": [],
  "remoto": {
    "alcance": "cualquiera",
    "paises": []
  }
}
```

**Varias ciudades en dos países, más remoto desde uno de ellos:**

```json
{
  "paises": {
    "XA": ["País A", "Country A"],
    "XB": ["País B", "Country B"]
  },
  "localidades": [
    {
      "pais": "XA",
      "divisiones": ["Provincia A1"],
      "zona": null,
      "nombres": ["Ciudad A1"]
    },
    {
      "pais": "XA",
      "divisiones": ["Provincia A2"],
      "zona": null,
      "nombres": ["Ciudad A2", "A2 City"]
    },
    {
      "pais": "XB",
      "divisiones": [],
      "zona": null,
      "nombres": ["Ciudad B1"]
    }
  ],
  "remoto": {
    "alcance": "paises",
    "paises": ["XA"]
  }
}
```

**Una zona metropolitana desglosada, sin remoto:**

```json
{
  "paises": {
    "XA": ["País A", "Country A"]
  },
  "localidades": [
    {
      "pais": "XA",
      "divisiones": ["Estado A", "Edo. A"],
      "zona": "Zona metropolitana de Ciudad A",
      "nombres": ["Ciudad A", "Municipio A2", "Municipio A3", "Área metropolitana de Ciudad A"]
    }
  ],
  "remoto": {
    "alcance": "ninguno",
    "paises": []
  }
}
```

**Un país completo y una provincia de otro, más remoto desde ambos:**

```json
{
  "paises": {
    "XA": ["País A", "Country A"],
    "XB": ["País B", "Country B"]
  },
  "localidades": [
    {
      "pais": "XA",
      "divisiones": [],
      "zona": null,
      "nombres": []
    },
    {
      "pais": "XB",
      "divisiones": ["Provincia B1"],
      "zona": null,
      "nombres": []
    }
  ],
  "remoto": {
    "alcance": "paises",
    "paises": ["XA", "XB"]
  }
}
```

## PREF-MODALIDAD — Prioridad de búsqueda

Modalidades que acepta (presencial, híbrido, remoto) y el orden en que las prefiere, si lo hay. Una prioridad no excluye: solo una modalidad que no acepte es condición en 08.

| Prioridad | Modalidad | Aplicación |
| --- | --- | --- |
| «pendiente» | | |

- **Asistencia presencial:** «pendiente»: máximo de días por semana en la oficina que acepta en presencial o híbrido. Es un máximo aceptable, no una preferencia ni una redefinición de híbrido.
- Registrar por separado la modalidad declarada por la vacante y la asistencia efectiva. Si la vacante no publica días o sede, el dato queda pendiente.

## PREF-COMPENSACION — Objetivo y mínimo

| Concepto | Registro | Fuerza |
| --- | --- | --- |
| Objetivo | «pendiente» | Deseado |
| Mínimo | «pendiente» | Indispensable: por debajo de este monto no acepta |
| Base | «pendiente»: bruto o neto, periodicidad (mensual, anual u otra) y qué incluye (sueldo base, bonos, prestaciones) | Las cifras de las vacantes se comparan sobre esta base; no se suman componentes que la base excluye para alcanzar el mínimo |
| Moneda | La del bloque de PREF-UBICACION. «pendiente»: si acepta pagos en otras monedas | |

**Cómo comparar:**

- **Otra moneda:** conservar el monto original y calcular el equivalente en la moneda del bloque con un tipo de cambio consultado en esa evaluación, con fecha y fuente. No fijar equivalentes permanentes ni inventar un margen por fluctuaciones.
- **Otra periodicidad o base:** convertir solo si no hace falta suponer nada. Un monto anual se divide entre los pagos del año que diga el anuncio, o entre 12 si no dice otro número. Una cifra neta no se convierte a bruta ni al revés.
- **Sueldo no publicado:** registrar «compensación pendiente de conocer» y evaluar el resto. La falta del dato no prueba que cumpla ni que incumpla.
- **Datos incompletos:** solo comparar cuando estén claras moneda, periodicidad, bruto o neto y componentes; si no, dejarlo pendiente. No estimar sueldos por empresa, título o nivel.

## PREF-CONTRATACION — Duración y relación

| Condición | Decisión | Aplicación |
| --- | --- | --- |
| Duración | «pendiente»: qué duraciones acepta (indefinida, temporal, por proyecto) | |
| Relación | «pendiente»: qué relaciones acepta (empleo asalariado, contrato como independiente, honorarios o factura) | |
| Intermediarios | «pendiente»: si acepta la contratación a través de una consultora o agencia | |

Si la vacante no aclara duración o relación, cada criterio queda pendiente. No deducir la relación por la modalidad, la moneda o la empresa. «Tiempo completo» no implica «indefinido»: jornada, duración y relación se evalúan por separado.

## PREF-JORNADA — Horario

| Aspecto | Decisión | Aplicación |
| --- | --- | --- |
| Horario | «pendiente» | |
| Fines de semana | «pendiente» | |
| Guardias y turnos rotativos | «pendiente» | |
| Turnos nocturnos | «pendiente» | |
| Remoto con otra zona horaria | «pendiente»: ventana de horas, en la zona horaria del bloque, en que acepta trabajar | Es una ventana para ubicar la jornada, no una jornada de esa duración ni disponibilidad permanente |

En remoto, distinguir la zona horaria del equipo del horario que el titular tendría que cubrir en la suya.

## PREF-DISPONIBILIDAD — Viajes e incorporación

- **Viajes:** «pendiente»: si acepta viajar (dentro de su país o al extranjero) y con qué límite de frecuencia o duración. Aceptarlos sin límite no autoriza viajes ilimitados ni reubicación.
- **Incorporación:** «pendiente»: tiempo que necesita para empezar después de aceptar una oferta. La fecha concreta se acuerda con la oferta.

## PREF-PENDIENTES

Lo que el titular no supo o no quiso decidir todavía, con `PREF-P##` y cuándo conviene resolverlo. Al resolverse, sale de la tabla y pasa a una línea de resueltos, con la sección donde quedó.

| ID | Pendiente | Tratamiento |
| --- | --- | --- |

## PREF-FUENTES — Declaraciones del titular

Cada bloque de respuestas del titular recibe un `PREF-U##` correlativo, con la fecha en la zona horaria del bloque. Las cifras, alcances y denominaciones se anotan con sus palabras.

| ID | Fecha | Contenido |
| --- | --- | --- |
