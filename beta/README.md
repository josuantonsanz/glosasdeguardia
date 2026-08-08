# Beta — una portada nueva para Glosas de guardia

Un prototipo de portada con diseño propio, **sin tocar el markdown de la nota**.
`content/Garden-home.md` (la nota con `dg-home: true`) sigue siendo la única
fuente de contenido: el script la procesa con el mismo pipeline que `build.py`
y la maqueta como landing page.

## Cómo verla

```bat
.venv\Scripts\python.exe beta\build_beta.py
```

Genera `beta/index.html` (más `beta/garden.jpg`, copia de `content/garden.jpg`).
Ábrela en el navegador. Los enlaces internos apuntan a `../public/`, así que la
portada es clicable si antes has generado el sitio real (`.venv\Scripts\python.exe build.py`).

## Cómo el markdown se convierte en diseño

La estructura de la nota se respeta al 100 %; el diseño es solo maquillaje:

| En el markdown                                   | En la portada                          |
| ------------------------------------------------ | -------------------------------------- |
| párrafos antes del primer `##`                   | intro del héroe                        |
| cada `## Título` + sus listas                    | una tarjeta (en orden)                 |
| la primera imagen tras la última sección         | fotografía enmarcada bajo el héroe     |
| todo lo que venga después (imagen / `- - -`)     | panel «Contacto» del pie               |
| `created` / `updated` del frontmatter            | chips «Plantado…» / «Atendido…»        |
| `updated` de **todas** las notas publicadas      | columna «Atendidas recientemente» (5)  |

Puedes **añadir, quitar o renombrar secciones** (`## Películas` → `## Cineforum`,
por ejemplo) y el diseño se adapta solo: cada `##` genera una tarjeta con su
icono y su lista de enlaces, en el mismo orden. No hay nombres de sección
cableados en ningún sitio.

## Decisiones de diseño

- **Un solo acento** (naranja Flexoki, el mismo de la web) y **un solo icono**
  repetido en todas las tarjetas: un sendero punteado, dibujado en SVG. Nada de
  emojis por sección; el estilo es uniforme.
- **Enlaces como en el resto de la web**: subrayado naranja, texto en tinta.
  Única excepción de la portada: una flecha `→` delante de cada enlace de las
  tarjetas. Y los enlaces externos llevan `↗` (esto se ha añadido también al
  sitio real, en `templates/style.css`, para que aparezca en todas las páginas).
- **Tipografías**: Fraunces (display), Lora (lectura), Caveat (anotaciones a
  mano) e Inter (interfaz).
- **Detalles ilustrados**: grano de papel en el héroe, fotografía enmarcada
  como postal (ligeramente girada), tarjetas con sombra suave, panel de
  contacto con el mismo estilo que el TOC móvil de las notas (pero sin
  desplegable).
- El estado del jardín (`Plantado hace 2 años`, `Atendido hoy`) sale del
  frontmatter, no está escrito a mano.

## Qué es contenido y qué es decoración

- **Contenido** (de la nota): título, intro, secciones, enlaces, foto y la nota
  final con el correo; además, los títulos y fechas de la columna derecha salen
  de las demás notas publicadas.
- **Decoración** (en `beta/home.html`, solo si quieres cambiarla): la etiqueta
  «Un jardín digital», el titular «Los caminos del jardín», el título del panel
  («Contacto») y el de la columna («Atendidas recientemente»).

## Cambios ya aplicados al sitio real

- `templates/style.css`: los enlaces externos (`http(s)://`) muestran un `↗`
  pequeño después del texto, en todas las páginas. Solo la flecha; el color de
  los enlaces no cambia.

## Cómo integrarlo en el sitio real (si te gusta)

1. Copiar `home.html` a `templates/` (o refundir la lógica de
   `TopLevelSplitter` + `split_home` en `build.py`).
2. En `build.py`, al final del bucle de notas: si `is_home_note(post)`, renderizar
   con `home.html` en lugar de `note.html` para el `index.html` final.
3. Añadir el CSS al final de `templates/scss/_home.scss` (el compilador SCSS
   se encarga del resto) o como `home.min.css` aparte.
4. El `root_path` del index ya es `./`, y `garden.jpg` ya se copia por el
   pipeline de imágenes.
5. Para la columna «Atendidas recientemente», pasar a la plantilla la lista de
   notas ordenadas por `updated` (el código está en `compute_recent` de
   `build_beta.py`).

## Limitaciones conocidas

- La detección de «pie» es: primera imagen o `<hr>` tras la última sección.
  Si pones una imagen en mitad de una sección, se tratará como inicio del pie.
- La nota «Cómo resolver el cubo de rubik» no tiene enlace porque la nota no
  existe/publicada; se muestra como texto atenuado en cursiva (igual que en la
  web actual).
- La columna derecha usa el `updated` (o `created`) del frontmatter de las
  notas publicadas; las notas sin fecha quedan fuera.
