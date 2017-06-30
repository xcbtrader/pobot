# pobot_MAX
Pobot_MAX - Bot para Poloniex Multi Coin 

Pobot_MAX es un bot autotrader en Multi Altcoin, que nos permite escoger entre casi todas las AltCoins con las que opera POLONIEX, operar tanto en USDT_xxx, BTC_xxx, ETH_xxx y XMR_xxx y definir para cada AltCoin el margen de beneficio que queremos. Este Bot está preparado para trabajar bajo Python 3.x. y necesita las liberias requests de python.

Utilizarlo bajo vuestra responsabilidad !!!! Nunca invertir el 100% del saldo ni dinero que no estemos dispuestos a perder.

No me hago responsable de posibles fallos, pérdidas o operaciones incorrectas que pueda realizar el Bot

El Bot es gratuito, hoy y siempre, pero para la gente que lo usa y está sacando beneficios, hemos creado ua dirección bitcoin para donaciones: 1Ec5rcFuH2VTMwxVfNuFeE7WJ121jQ6GYu (Usar sólo si estais contentos con el bot)

Antes de ejecutar el programa, hay que editar el fichero pobot_MAX.cfg y modificar la línea donde se pide los datos del API. Si no los tenemos creados, antes hay que ir a la web de Poloniex y crear una llave de API.

Para ejecutarlo poner:

WINDOWS:

Ejecutar la orden cmd

Ir al directorio donde hemos grabado los ficheros pobot_MAX.py y pobot_MAX.cfg (utilizando la orden cd)

ejecutar el bot con python3 pobot_MAX.py o python pobot_MAX.py (depende de la configuración de cada ordenador)

LINUX:

Abrir la cónsola de linux y mediante la instrucción cd ir al directorio donde tenemos el ichero pobot_MAX.py

ejecutar el bot con python3 pobot_MAX.py o python pobot_MAX.py (depende de la configuración de cada ordenador)

Si da error seguramente es porque no tenemos correctamente la libreria requests o la clave API no la hemos puesto.

Una vez ejecutado, nos aparecerá un menú para escoger el tipo de Alt con el que vamos a operar y el saldo que tenemos en POLONIEX para cada una: USDT, BTC, ETH, XMR.

En función de la Alt que escojamos, tendremos diferentes pares para escoger. Estos pares se encuentran en el fichero pobot_MAX.cfg y que podemos editar con cualquier editor de textos (CUIDADO USUARIOS DE WINDOWS. Notepad no funciona correctamente. Mejor ejecutar notepad ++)

Después nos pedirá el sado máximo a invertir (NUNCA PONGAIS EL 100%) el bot dividirá ese saldo entre todas las alts con las que vayamos a operar: EJEMPLO. Si ponemos 0.1 btc y trabajamos con 10 alts, el bot entrará en cada una con 0.01 btc.

Después hay que poner la opción de inversión con la que queremos operar con el bot. En funcón de la opción escogida se nos pide unos datos o otros. Estas son las 6 opciones disponibles:

1-> Según Margen de Incremento 24h (Con todas las Alts)

Trabajando con todas las alts que tenemos en nuestro fichero de configuración, ponemos el margen de incremento de esa alt en las ultimas 24h, su situación actual,el beneficio que queremos obtener por cada operación, y el número de ciclos que va durar el trader.

2-> Según Margen de Incremento 24h (Escogiendo Manualmente las Alts)

Lo mismo que la opción anterior pero escogiendo nosotros manualmente las alts a tradear

3-> Versión Antigua - Pone ordenes instantáneas (Con todas las Alts)

Versión antigua de Pobot... NO RECOMENDABLE.

4-> Versión Antigua - Pone ordenes instantáneas (Escogiendo Manualmente las Alts)

Versión antigua de pobot...escogiendo manualmente las alts. NO RECOMENDABLE

5-> Vamos a por el PUMP (Una sola Alt entrada Manualmente)

¿Tenemos información privilegiada de una alt que va a entrar en PUMP ... Esta opción nos permite poner la alt que queramos, y trabajar sólo con ella aprovechando las subidas...

6-> Automático. Escoge las mejores Alts para tradear en cada momento

Esta opción es novedad total, y es la más inteligente de todas, ya que busca en cada momento las alts que tienen un margen mejor, y entra a operar con ellas.

Datos adicionales que, en función de la opción escogida nos va a pedir el Bot:

- margen de incremento de las ultimas 24h para entrar a invertir: este es el márgen de incremento que tiene la moneda en las últimas 24h. Valores recomendables de 1 a 10.

- margen de incremento actual de la Alt para entrar a invertir: Este margen es complicado de entender, pero muy útil para no entrar en alts que están uy subidas de valor. 

Vamos a poner un ejemplo:

Alt USDT_BTC. Max 24h = 1100, Min 24h = 1000, Incremento 24h = 10%. Si le ponemos como valor 60% significa que sólo entrará a invertir si USDT_BTC tiene un valor inferior a: Min 24h + (Max 24h - Min 24h) * Margen/ 100 = 1000 + (1100 - 1000)* 60/100 = 1060

Esto significa que mientras el valor actual del par USDT_BTC esté por arriba de 1060, no entrará. Cuando baje de ese valor, pondrá la orden.

- Después nos pide el margen de beneficio, para todas las Alts, o para cada una. Este valor tiene que ser superior a 0.5, ya que sinó los fees de POLONIEX noscomerán el beneficio. Valores muy elevados harán que la orden no cierre casi nunca. Valores recomendados: de 1 a 5.

- Ya para finalizar, el bot nos pedirá el número de ciclos que va a durar el trader. Entendemos un CICLO como el proceso completo de que se cierre una orden de compra y su correspondiente orden de venta. Si estamos en la opción 6,los ciclos son pares de alts independientes. En las demás opciones, si operamos con 5 alts a la vez los ciclos no se incrementan hasta que no se hayan finalizado las ordenes de cada Alt. 

Evidentemente, para que el bot funcione, se necesita tenerlo siempre funcionando y una conexión a internet. Los datos los consulta cada 10 segundos, por lo que no consume ancho de banda.

El bot finalizará cuando se finalicen todos los ciclos. Para finalizar el bot de forma manual (NO RECOMENDABLE), simplemente apretar CTRL + c. Si lo cerramos así, tendremos que ir a POLONIEX y cerrar manualmente las órdenes que queden abiertas. (Esto puede provocar pérdidas)

NOTA:

Por configuración y forma de trabajar del bot, este no puede genrar nunca pérdidas: El pone una orden de compra, y cuando se cierra pone una orden de venta para la misma alt al precio de compra + margen de beneficio.

Sólo se generarán pérdidas si, por impaciencia se cierra manualmente una orden que está tardando en cerrarse.

LAS ALTS, SUBEN Y BAJAN... EN ESO RADICA EL BENEFICIO DEL TRADER...

Espero que este bot, realizado de forma altruista para que todos podamos tener las opciones que tienen las grandes firmas, les permita obtener beneficios de este mundo tan adictivo.

xcbtrader ...

Dirección de donaciones: 1Ec5rcFuH2VTMwxVfNuFeE7WJ121jQ6GYu

Enlace del grupo de TELEGRAM:https://t.me/joinchat/AAAAAELwarzwaE1U7fMGpA
