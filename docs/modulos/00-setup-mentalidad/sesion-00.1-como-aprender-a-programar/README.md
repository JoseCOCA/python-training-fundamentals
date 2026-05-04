# S00.1 — Cómo aprender a programar

> **Sesión 1h.** ~45 min de lectura + ~15 min de reflexión guiada en `ejercicios.md`. Es la **única sesión sin código** del curso. Si la saltas, vas a sufrir el resto del curso. Si la lees con seriedad, te ahorras meses de frustración improductiva.

---

## 1. Objetivos de aprendizaje

Al terminar esta sesión vas a:

- Entender por qué aprender a programar es genuinamente difícil para **todo el mundo**, y por qué eso no significa que no seas para esto.
- Distinguir **frustración productiva** (señal de aprendizaje) de **frustración tóxica** (señal de pausa o cambio de enfoque).
- Conocer una rutina concreta para **desbloquearte** cuando estás atascado.
- Saber cómo **leer documentación técnica en inglés** sin paralizarte.
- Entender por qué **usar IA como atajo para no entender** es contraproducente, y cómo usarla como herramienta de aprendizaje real.

## 2. Prerequisitos

Ninguno. Esta es la primera sesión del curso.

## 3. Conceptos clave

1. **El bucle de aprendizaje.** Leer → intentar → equivocarse → entender el error → corregir → repetir. Si saltas alguno (sobre todo "equivocarse" y "entender el error"), no aprendes — solo memorizas.
2. **Frustración productiva vs tóxica.** La primera te enseña; la segunda te desgasta y no produce nada. Distinguirlas es una habilidad de segundo orden que vas a entrenar durante todo el curso.
3. **Práctica deliberada.** Repetir lo que ya sabes hacer no es práctica, es ejercicio. Aprender requiere atacar el borde de lo que NO sabes hacer todavía.
4. **Lectura escalonada de documentación.** *Skim* (vista de pájaro) → *focus* (lectura cercana de la sección que importa) → *execute* (probar el ejemplo). Saltarse pasos genera caos.
5. **Rubber duck debugging.** Explicar el problema en voz alta, paso a paso, a una persona / patito de goma / IA. La mitad de las veces el rato de explicarlo es el rato en el que lo resuelves.

## 4. Teoría

### 4.1. Programar es difícil. Y eso es información, no juicio.

Vas a leer en internet a gente que dice "yo aprendí a programar en 3 meses". Algunos mienten. Otros entienden "programar" como "escribir scripts que funcionan en mi máquina". Pero programar **en serio** — diseñar sistemas, depurar errores raros, leer código de otros, mantener una codebase de 50.000 líneas — eso no se aprende en 3 meses. No es porque seas lento. Es porque es genuinamente difícil.

Cuatro razones técnicas por las que es difícil:

1. **Tienes que mantener un modelo mental de algo que no puedes ver directamente.** La computadora ejecuta tu código sin que tú veas la ejecución. Si tu modelo mental no encaja con lo que la máquina realmente hace, el bug se esconde hasta que descubras la diferencia.
2. **Los errores son indirectos.** Cuando algo falla, la causa puede estar a 200 líneas de distancia, en otro archivo, escrito por otra persona, hace 3 meses.
3. **El feedback es asimétrico.** Cuando el código funciona, te dice poco (¿funciona porque está bien o porque tuviste suerte?). Cuando falla, te dice mucho. Por eso los buenos programadores aprenden a **querer** que las cosas fallen rápido.
4. **El stack es enorme.** No solo programas: también tienes terminal, git, sistema operativo, red, base de datos, librerías de terceros, contenedores. Un solo proyecto toca docenas de capas.

Si te frustras en este curso, no es porque seas torpe. Es porque estás procesando todo esto por primera vez. **La frustración es información**: te dice que tu modelo mental todavía no encaja con la realidad. La pregunta no es cómo evitarla — la pregunta es cómo procesarla productivamente.

### 4.2. Frustración productiva vs frustración tóxica

**Frustración productiva** se ve así:

- Sabes qué estás intentando hacer.
- Probaste uno o dos enfoques que no funcionaron.
- Tu cerebro está activo, generando hipótesis: "tal vez es esto, tal vez es lo otro".
- Si paras 10 minutos y vuelves, lo ves más claro.
- Cuando se resuelve, sientes que aprendiste algo concreto.

**Frustración tóxica** se ve así:

- Llevas 2-3 horas en el mismo error.
- Ya no sabes ni qué estás intentando exactamente.
- Tu cerebro está en bucle, repitiendo las mismas hipótesis fallidas.
- Cuando paras y vuelves, no cambia nada — porque el problema no es de comprensión, es de cansancio o de marco mental incorrecto.
- Cuando finalmente "se resuelve" (a veces solo), no sabes por qué se resolvió.

**La regla práctica:**

> Si llevas más de **30-45 minutos** en el MISMO error sin haber probado **nada nuevo**, la frustración es tóxica. Para.

### 4.3. Qué hacer cuando estás atascado

Rutina concreta, en este orden:

1. **Reformula el problema en una sola frase.** "Estoy intentando que X pase, pero está pasando Y, y la diferencia parece ser Z." Si no puedes escribir esa frase en una línea, el problema no es el código — es que no tienes claro el problema.
2. **Reduce la granularidad.** Si llevas rato debuggeando un sistema completo, sal de ahí. Escribe un mini-script de 10 líneas que reproduzca el bug aislado. La mayoría de los bugs se vuelven obvios cuando los aíslas.
3. **Rubber duck.** Explica el problema en voz alta, paso a paso, a una persona, a un patito de goma o a una IA. Forzar a tu cerebro a explicar lo lentamente fuerza el procesamiento serial. La mitad de las veces te das cuenta solo.
4. **Pausa de 15 minutos sin pantalla.** Camina, lava los platos, toma agua. El cerebro sigue procesando aunque no lo notes — fenómeno conocido como *incubación*. Llamar a alguien o mirar el teléfono no cuenta: necesitas que el cerebro descanse, no que cambie de carga.
5. **Duerme encima del problema.** Si después de la pausa sigue trabado y ya pasaste 2-3 horas en el día, deja. La consolidación durante el sueño es real y medible. Muchos bugs los vas a "resolver" en la ducha del día siguiente.
6. **Pide ayuda — pero después de 1-5.** Pedir ayuda antes de haber aislado el problema es pedirle a alguien que haga tu trabajo. Pedir ayuda después de haber aislado, reformulado y descrito el problema es colaboración real.

### 4.4. Cómo NO se aprende a programar

Tres anti-patrones comunes:

**❌ Mirar tutoriales sin escribir código propio.** Mirar a alguien programar es tan útil para aprender a programar como mirar el Tour de Francia es útil para aprender a andar en bici. El conocimiento entra por las manos, no por los ojos. Por cada hora de tutorial, escribe al menos 30 minutos de código tuyo.

**❌ Copiar-pegar hasta que funcione sin entender por qué.** Si tu solución es "probé 5 cosas de Stack Overflow y la cuarta funcionó", no aprendiste nada — solo entrenaste a tu yo del futuro a depender de Stack Overflow. La pregunta clave después de cada copia-pega es: **¿por qué esto funciona y lo otro no?**

**❌ Pedirle a una IA "resuelve esto" sin entender la solución.** La IA te puede dar la respuesta. Pero el objetivo del curso no es **tener la respuesta**, es **saber cómo llegar a la respuesta**. Si la IA te genera código que funciona pero no entiendes, no avanzaste — quedaste con la falsa sensación de progreso. La forma correcta es:
1. Intenta tú primero.
2. Si te trabás, pregúntale a la IA cómo pensar el problema (no la respuesta).
3. Si te da código, leelo línea por línea y asegúrate de entender CADA una. Si hay algo que no entiendes, pregúntale qué hace.
4. Cierra la IA y escribe la solución de nuevo desde cero, sin mirar.

### 4.5. Cómo SÍ se aprende a programar

Tres patrones que funcionan:

**✅ Práctica deliberada.** Identifica algo que no sabes hacer todavía. Atácalo. Si te sale a la primera, era demasiado fácil — busca algo más difícil. Si no te sale después de un día entero, era demasiado difícil — baja un escalón. El sweet spot es: te cuesta, pero progresas.

**✅ Construir cosas reales.** Por eso este curso tiene un proyecto integrador (TiendaPro Lite) que crece módulo a módulo. Hacer una API REST de verdad — con catálogo, clientes, pedidos, persistencia, tests — te enseña 10x más que 100 ejercicios de juguete. Los ejercicios sirven para introducir conceptos; el proyecto te enseña a integrarlos.

**✅ Leer código de otros.** Cada vez que uses una librería (FastAPI, pydantic, SQLAlchemy), abre su código fuente y leelo. No vas a entender todo, pero vas a ver cómo lo escriben los buenos. Es la forma más infravalorada de mejorar.

### 4.6. Cómo leer documentación técnica en inglés

La doc oficial de Python, FastAPI, SQLAlchemy y la mayoría de librerías está en inglés. Si tu inglés es regular, esto va a ser un cuello de botella al principio. La buena noticia: la lectura técnica se entrena leyéndola, y el vocabulario es más limitado de lo que parece (~300 palabras técnicas cubren el 90%).

**Método de tres pasadas:**

1. **Skim (1-2 minutos).** Lee solo títulos, primer párrafo de cada sección, y bloques de código sin leer el texto explicativo. Objetivo: tener un mapa mental de qué hay y dónde, sin entender los detalles. No te detengas en palabras que no conoces.
2. **Focus (5-15 minutos).** Identifica la sección que necesitas y leela despacio. Ahora sí, busca las palabras técnicas que no entiendes. Después de hacerlo varias veces, el vocabulario empieza a repetirse.
3. **Execute (10-30 minutos).** Copia el ejemplo de código de la doc, ejecútalo, modifícalo, rómpelo intencionalmente para ver qué pasa. La doc se entiende ejecutándola, no leyéndola.

**Trampa común:** intentar entender TODO antes de ejecutar nada. La doc no se entiende lineal — se entiende iterando entre lectura y ejecución.

**Recurso: traductor en el navegador.** Para los primeros meses está bien usar Google Translate o DeepL para traducir párrafos enteros. Pero hazlo en una pestaña aparte, no como reemplazo de la lectura. El objetivo es ir necesitándolo cada vez menos.

### 4.7. La IA como herramienta de aprendizaje (no como muleta)

La IA generativa (ChatGPT, Claude, Copilot) cambió el aprendizaje de programación. Bien usada, acelera el aprendizaje 5x. Mal usada, lo destruye. La diferencia es ENORME y vale la pena entenderla bien desde el principio.

**Forma incorrecta:** "Hazme un script que haga X." → copias el resultado → lo pegas → funciona → sigues. **Cero aprendizaje.** La IA hizo el trabajo, tú no.

**Formas correctas:**

1. **IA como tutor:** "Estoy aprendiendo Python. Explícame qué es una función como si tuviera 12 años, con un ejemplo simple, y después dame un ejercicio de práctica para resolver yo." Después resuelves el ejercicio TÚ, sin pedirle la respuesta.
2. **IA como rubber duck:** "Estoy intentando hacer X, mi código actual es este, pero falla con este error. ¿Qué preguntas debería hacerme para diagnosticar?" — la IA te devuelve preguntas, no la solución. Tú diagnosticas.
3. **IA como revisora de código:** Tú escribes el código primero. Después se lo pasas: "¿Qué problemas ves en este código? No lo arregles, solo señala los problemas." Después arreglas TÚ.
4. **IA como explicadora de código ajeno:** Encuentras una librería que usa una sintaxis rara. "Explícame qué hace esta línea y por qué se escribe así." Aprendes leyendo, no copiando.

**Regla de oro:** si después de usar la IA no puedes explicar la solución a otra persona sin mirar, no aprendiste. Cierra la IA y escribe la solución de nuevo desde cero.

## 5. Patrones y antipatrones

| ✅ Patrón | ❌ Antipatrón |
|---|---|
| Escribir código que falla y entender por qué | Probar al azar hasta que funcione |
| Aislar el bug en un mini-script de 10 líneas | Debuggear el sistema completo de 200 líneas |
| Pausar 15 min cuando llevas 30+ min en lo mismo | Forzar 3h sin parar — "ya casi" |
| Explicar el problema en voz alta antes de pedir ayuda | Pegar 200 líneas de código en un chat sin contexto |
| Usar IA para entender, pedir ejercicios y revisar | Usar IA para resolver y copiar-pegar |
| Leer la doc oficial en inglés (skim → focus → execute) | Buscar siempre tutoriales en español de YouTube |
| Construir el proyecto integrador en paralelo a las sesiones | Dejar el integrador para "cuando termine la teoría" |
| Aceptar que la frustración es parte del proceso | Asumir que si te frustras es porque "no eres para esto" |

## 6. Conexión con el proyecto integrador

TiendaPro Lite es un producto **real** — no un toy project. Cuando empieces a construirlo a partir del Módulo 1, vas a chocar con bugs reales: tipos que no encajan, peticiones HTTP que fallan, transacciones de base de datos que se quedan colgadas, tests que pasan en local y fallan en Docker.

La forma de pensar y debuggear que estableces en esta sesión es lo que va a determinar si avanzas o te quedas trabado. Relee esta sesión cada vez que sientas que estás dando vueltas en círculos en el integrador — vas a encontrar la herramienta que necesitabas usar y olvidaste.

## 7. Resumen

Los tres puntos que te tienes que llevar:

1. **Programar es difícil para todo el mundo.** No es talento natural. Es práctica deliberada con feedback rápido. La frustración no es señal de "no eres para esto" — es señal de que tu modelo mental se está construyendo.
2. **Frustración productiva vs tóxica.** Productiva = sabes qué intentas, generas hipótesis, paras y vuelves con claridad. Tóxica = bucle estéril, cansancio, marco mental incorrecto. Cuando es tóxica, **para**.
3. **La IA es una herramienta de aprendizaje, no una muleta.** Bien usada, acelera 5x. Mal usada, destruye el aprendizaje. La diferencia: ¿la IA está haciendo TU trabajo o te está enseñando a hacerlo?

## 8. Preguntas de auto-evaluación

Si no puedes responderlas sin volver a leer, vuelve a leer.

1. ¿Cuáles son los cinco pasos del bucle de aprendizaje? ¿Cuál se salta más seguido y por qué es el más importante?
2. Diferencia concreta entre frustración productiva y frustración tóxica. Da una señal observable de cada una.
3. Llevas 1h 15min en el mismo error y ya probaste tres cosas que no funcionan. ¿Qué haces, en orden?
4. ¿Por qué leer un tutorial sin escribir código propio no es aprender?
5. ¿Cuáles son las tres pasadas del método de lectura escalonada de docs en inglés? ¿Cuál es la trampa más común?
6. Da dos formas correctas y una forma incorrecta de usar IA durante el aprendizaje. ¿Cuál es la regla de oro?

Si pudiste responder todas sin trampa, pasa a `ejercicios.md`. Si no, relee las secciones donde flaqueaste antes de seguir.
