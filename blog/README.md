# Bitácora personal · Víctor Hugo Torres

Entrada pública: https://serymente.github.io/otrogranprograma/blog/

- Escribir/importar/revisar: `blog/escribir/`.
- Fuentes públicas aprobadas: `blog/entries/*.json`.
- Constructor determinista sin dependencias: `python scripts/build-personal-blog.py`.
- Pruebas: `python scripts/test-personal-blog.py`.
- Salidas: HTML por entrada, índice estático, `archivo.json`, RSS `feed.xml`.
- El laboratorio previo se conserva en `blog/laboratorio/`; sus paquetes siguen en `blog/playground/`.

## Publicar
Escribir o importar una selección de Khora; revisar; aprobar; confirmar el JSON con la cuenta autorizada en GitHub. El editor no guarda tokens ni publica con credenciales del visitante. Un borrador en localStorage no es respaldo: descargar JSON. El puente con Khora es asistido/importación, no sincronización ni botón dentro de Khora. No incorporar notas privadas, credenciales o IDs internos como efecto automático.

## Editar y retirar
Editar o eliminar el archivo JSON y confirmar en main. El despliegue recompone el archivo desde las fuentes; el historial de Git y copias de terceros pueden conservar lo anterior. La huella SHA-256 prueba integridad del texto, no veracidad ni identidad legal.

## Reversión
Revertir el commit de implementación para recuperar la entrada de laboratorio previa. Exportar las entradas antes de cambiar de plataforma.

Gobierno y originales privados: objeto único en `SeryMente/metodologia`, carpeta `frentes/blog-personal/`. No se replican dictados personales en este repositorio público.
