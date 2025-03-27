# ProxyFinder

Un script en Python para encontrar y verificar proxies

## Instalación

Instale el paquete y sus dependencias usando `pip`:

```bash
pip install git+https://github.com/CalumRakk/proxyfinder
```

## Uso

Después de la instalación, ejecuta el script desde la línea de comandos:

```bash
proxyfinder
```

Esto iniciará el proceso de búsqueda y verificación de proxies. Los resultados se guardarán en la base de datos SQLite (`proxies.db`)

**Ejemplo de Salida (en la consola):**

```
2024-10-27 10:00:00,000 [INFO] proxyfinder - Obteniendo proxies de la fuente: https://www.sslproxies.org/ (tipo: table)
2024-10-27 10:00:05,000 [INFO] proxyfinder - Obtenidos 50 proxies limpios de https://www.sslproxies.org/
2024-10-27 10:00:10,000 [INFO] proxyfinder - Proxy 192.168.1.100:8080 funciona (150.25 ms)
2024-10-27 10:00:15,000 [INFO] proxyfinder - Actualizados 10 proxies en la base de datos.
...
```

El archivo `proxyfinder.log` contendrá información de logging más detallada.
