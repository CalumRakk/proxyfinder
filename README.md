# ProxyFinder

Un script en Python para encontrar y verificar proxies HTTP.

## Instalación

Instale el paquete y sus dependencias usando `pip`:

```bash
pip install git+https://github.com/CalumRakk/proxyfinder
```

## Uso

El script se puede ejecutar desde la línea de comandos utilizando el comando `proxyfinder` seguido de la acción que deseas realizar y las opciones correspondientes

### **`check`:** Busca y verifica proxies

```bash
proxyfinder check
```

Este comando no requiere argumentos adicionales.

### **`export`:** Exporta los proxies a un archivo CSV.

```bash
proxyfinder export <ubicacion> [--all]
```

- `<ubicacion>` (opcional): La ubicación del archivo CSV al que se exportarán los proxies (por ejemplo, `proxies.csv` o `mi_directorio/proxies.csv`). Si no se especifica, se utilizará el nombre de archivo `proxies.csv` por defecto y se guardará en el directorio de trabajo actual.

- `--all` (opcional): Un flag para exportar _todos_ los proxies de la base de datos, independientemente de si están funcionando o no. Si no se especifica, solo se exportarán los proxies que se hayan verificado y que se considere que están funcionando.

## Ejemplos de uso:

- **Verificar proxies:**

  ```bash
  proxyfinder check
  ```

  Este comando iniciará el proceso de búsqueda y verificación de proxies, actualizando la base de datos con los resultados.

- **Exportar proxies funcionales a una ubicación específica (`mi_archivo.csv`):**

  ```bash
  proxyfinder export mi_archivo.csv
  ```

  Este comando exportará los proxies funcionales al archivo `mi_archivo.csv` en el directorio actual.

- **Exportar _todos_ los proxies a una ubicación específica (`todos_los_proxies.csv`):**

  ```bash
  proxyfinder export todos_los_proxies.csv --all
  ```

  Este comando exportará _todos_ los proxies de la base de datos (incluyendo los que no funcionan) al archivo `todos_los_proxies.csv` en el directorio actual.
