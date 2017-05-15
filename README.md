# pobot
Pobot - Bot para Poloniex Multi Coin 

Pobot es un bot autotrader en Multi Altcoin, que nos permite escoger entre 10 AltCoins diferents, y definir para cada una el margen de beneficio que queremos. Este Bot está preparado para trabajar en Python 2.7 y Python 3.x.

Utilizarlo bajo vuestra responsabilidad !!!!

No me hago responsable de posibles fallos, pérdidas o operaciones incorrectas que pueda realizar el Bot

Antes de ejecutar el programa, hay que editar el fichero pobot.cfg y modificar la línea donde se pide los datos del API. Si no los tenemos creados, antes hay que ir a la web de Poloniex y crear una llave de API.

Para ejecutarlo poner:

Para Python 2.7

python pobot.py

Para Python 3.x

python3 pobot.py

Una vez ejecutado, primero nos pedirá si queremos continuar con la última sesión creada, el márgen de beneficio que queremos para cada Altcoin y la cantidad total de USDT que queremos invertir. Cuanto más grande sea el margen de beneficio escogido, tardará más en cerrar las operaciones, pero más beneficio tendremos. Si no queremos que el bot opera con alguna AltCoin, simplemente le ponemos margen 0 y ya está.

El bot funcionrá mientras tengamos saldo. Para su correcto funcionamiento, necesitamos tener saldo de USDT, y ninguna operacion abierta en las Altcoins con las que vamos a operar.

También nos pedirá el número de ciclos completos (Un ciclo = compra + venta) que queremos que dure el bot.

Evidentemente, para que el bot funcione, se necesita tenerlo siempre funcionando y una conexión a internet. Los datos los consulta cada 30 segundos, por lo que no consume ancho de banda.

El funcionamiento del bot es sencillo:

Al iniciarlo, comprueba que no haya operaciones abiertas, y mira nuestro saldo USDT. La cantidad que se utilizará en cada orden, se calcula con la siguiente fórmula: saldo_inicial_USDT a invertir/número de AltCoins escogidos.

Entonces el sistema pone una órden de compra de cada AltCoin, al precio del mercado. Una vez cerrada esta orden, el bot hace el proceso contrario, pone una órden de venta al precio del mercado + margen de beneficio, y así continuamente para cada AltCoin por separado hasta finalizar el número de ciclos deseado.

Para finalizar el proceso, simplemente apretar CTRL + c. Suiempre podemos volver a iniciar el bot y continuar donde lo habíamos dejado.

Si el bot nos deja órdenes abiertas, y las queremos cerrar, simplemente, vamos a POLONIEX, y las cerramos.
