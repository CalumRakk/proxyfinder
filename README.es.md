# ProxyFinder

Un script en Python para encontrar, verificar y administrar proxies HTTP con una interfaz de línea de comandos (CLI).

## Características

- **Encontrar Proxies:** Extrae proxies de múltiples fuentes en línea.
- **Verificar Proxies:** Verifica la funcionalidad de los proxies.
- **Almacenar Proxies:** Almacena proxies y su estado en una base de datos SQLite.
- **Administrar Proxies:** Proporciona comandos para filtrar, mostrar y exportar proxies.

## Instalación

Instale el paquete y sus dependencias usando `pip`:

```bash
pip install git+https://github.com/CalumRakk/proxyfinder
```

## Uso

El script se ejecuta desde la línea de comandos utilizando el comando `proxyfinder` seguido de la acción que desea realizar y las opciones correspondientes.

### Descripción General de los Comandos

La estructura general de los comandos es:

```bash
proxyfinder <comando> [opciones]
```

### Comandos Disponibles:

1.  **`find`:** Encuentra y agrega nuevos proxies a la base de datos.

    ```bash
    proxyfinder find [--concurrency <num>]
    ```

    - `--concurrency <num>` (opcional): Número de subprocesos (threads) a utilizar para la búsqueda. El valor por defecto es 10.

    Este comando busca nuevos proxies en las fuentes configuradas y los agrega a la base de datos. No verifica los servidores proxy, por lo que debe usar el comando `check`.

    **Ejemplo:**

    ```bash
    proxyfinder find
    ```

    Este comando encuentra nuevos proxies.

2.  **`check`:** Verifica el estado de los proxies.

    ```bash
    proxyfinder check [--status <estado>] [--concurrency <num>] [--older-than <días>]
    ```

    - `--status <estado>` (opcional): Filtra los proxies a verificar según su estado. Los valores posibles son: `working` (funcionando), `broken` (roto/no funcionando), `unchecked` (sin verificar) o `all` (todos). El valor por defecto es `working`.
    - `--concurrency <num>` (opcional): Número de subprocesos a utilizar para la verificación. El valor por defecto es 10.
    - `--older-than <días>` (opcional): Verifica solo los proxies que no se han verificado en los últimos N días. El valor por defecto es 0 (verifica todos los proxies).

    Este comando verifica la funcionalidad de los proxies en la base de datos y actualiza su estado (funcionando/roto).

    **Ejemplos:**

    ```bash
    proxyfinder check --status unchecked
    proxyfinder check --older-than 7
    ```

    El primer comando verifica todos los proxies sin verificar. El segundo comando verifica los proxies que no se han verificado en los últimos 7 días.

3.  **`show`:** Muestra los proxies de la base de datos en un formato paginado en la terminal.

    ```bash
    proxyfinder show [--status <estado>] [--limit <num>] [--count] [--sort-by <campo>] [--reverse] [--older-than <días>]
    ```

    - `--status <estado>` (opcional): Filtra los proxies por estado. Los valores posibles son: `working`, `broken`, `unchecked` o `all`. El valor por defecto es `working`.
    - `--limit <num>` (opcional): Limita el número de proxies a mostrar.
    - `--count` (opcional): Muestra solo el número de proxies en lugar de mostrar la lista completa.
    - `--sort-by <campo>` (opcional): Ordena los proxies por el campo especificado. Los valores posibles son: `latency` (latencia), `created_at` (fecha de creación), `updated_at` (fecha de actualización). El valor por defecto es `latency`.
    - `--reverse` (opcional): Invierte el orden de clasificación.
    - `--older-than <días>` (opcional): Muestra solo los proxies que han pasado esos dias.

    **Ejemplos:**

    ```bash
    proxyfinder show --status working --limit 20 --sort-by latency --reverse
    proxyfinder show --status all --count
    ```

    El primer comando muestra los 20 mejores proxies funcionales ordenados por latencia en orden inverso. El segundo comando muestra el número total de proxies en la base de datos.

4.  **`export`:** Exporta los proxies a un archivo CSV.

    ```bash
    proxyfinder export <archivo_de_salida> [--all]
    ```

    - `<archivo_de_salida>` (obligatorio): La ruta al archivo CSV de salida.
    - `--all` (opcional): Exporta todos los proxies, no solo los que funcionan.

    Este comando exporta los proxies seleccionados a un archivo CSV.

    **Ejemplos:**

    ```bash
    proxyfinder export proxies_funcionales.csv
    proxyfinder export todos_los_proxies.csv --all
    ```

    El primer comando exporta solo los proxies funcionales a `proxies_funcionales.csv`. El segundo comando exporta todos los proxies a `todos_los_proxies.csv`.

5.  **`update`:** Encuentra nuevos proxies y verifica los proxies encontrados.

    ```bash
    proxyfinder update [--concurrency <num>]
    ```

    - `--concurrency <num>` (opcional): Número de subprocesos a utilizar para la búsqueda y verificación. El valor por defecto es 10.

    Este comando combina los comandos `find` y `check`. Primero, encuentra nuevos proxies y luego verifica estos proxies.

    **Ejemplo:**

    ```bash
    proxyfinder update --concurrency 15
    ```

    Este comando encuentra y verifica nuevos proxies, utilizando 15 subprocesos para ambas operaciones.

**Consejos para usar la CLI:**

- Utilice `proxyfinder help <comando>` para obtener ayuda detallada sobre un comando específico.
- Tenga en cuenta el parámetro `--concurrency`. Usar demasiados subprocesos puede sobrecargar su sistema. Sin embargo, los hilos especificados se ajustan según los disponibles en el sistema, sin embargo, esto solo es una guía, no un límite absoluto.
- Ejecute `proxyfinder check` regularmente para mantener actualizada su lista de proxies.
