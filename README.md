# ProxyFinder

Un script sencillo en Python para encontrar y verificar proxies HTTP

## Instalación

Instale el paquete usando `pip`:

```bash
pip install git+https://github.com/CalumRakk/proxyfinder
```

## Uso

Después de la instalación, ejecuta el script desde la línea de comandos:

```bash
proxyfinder
```

**Ejemplo de Salida:**

```
Obtenidos 50 proxies de https://www.sslproxies.org/
Obtenidos 100 proxies de https://free-proxy-list.net/
Obtenidos 75 proxies de https://www.us-proxy.org/
Obtenidos 25 proxies de https://www.proxy-list.download/HTTP
Obtenidos 200 proxies de https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all
Obtenidos 150 proxies de https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt
Obtenidos 125 proxies de https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt
Obtenidos 100 proxies de https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/proxy.txt

Total de proxies únicos obtenidos: 825
Proxy 192.168.1.100:8080 funcionando (150.25 ms)
Proxy 10.0.0.5:3128 funcionando (220.50 ms)
Proxy 172.16.0.15:80 funcionando (185.75 ms)
Proxies guardados en proxies.txt
```

El archivo `valid_proxies.csv` contendrá los proxies en funcionamiento y sus latencias:

```csv
Proxy,Latencia (ms),Funciona
192.168.1.100:8080,150.25,True
10.0.0.5:3128,220.50,True
172.16.0.15:80,185.75,True
```
