# Plan de preprocesamiento
He hido haciendo este documento a la misma vez de programar, por eso algunas soluciones tiene ese tono. Ademas termine todo el preprocesamiento antes de dijieran que se podrian ignorar los errores ortograficos y *typos* de algunas de las columnas con strings, pero ya habia aplicado una solucion y la verdad que estoy bastante orgulloso.

## Columnas a dropar
No pienso que las siguientes columnas tengan algo que ver con el objetivo del preprocesamiento. Es decir, puede que exista una relacion muy abstracta con el un diagnostico de cancer pero no pienso que valga la pena el trabajo en preprocesar.
1. **favorite_color**
2. **education**
3. **marital_status**
4. **insurance_provider**
5. **patient_id**

Las siguientes columnas **edad_paciente** y **hospital**tienen informacion redundate ya que **birth_year** y **hospital_code**, respectivamente, contienen la misma informacion y ya procesada. 

## Columnas a procesar

### sexo_paciente
Ordinal encoding: 0 si es *male* o cualquiera de sus variaciones y 1 si es *female* o cualquiera de sus variaciones.

### cancer_stage
Ordinal encoding: se convierte el numero romano a decimal y los que no sean lo ponemos 0. 

## Genes
Hay una gran cantidad de columnas que tienen una formatacion similar, les voy a llamar de *genes* pero puede que no sean. Las indico por su formato de valores.

### Formato *wild-mutated*
Formato:
- Wild-type
- Mutated

Columnas: 
1. KRAS
2. BRAF
3. HER2
4. AR
5. C-KIT

Ordinal encoding: 1 si el valor es *Mutaded* y cero en cualquier otro caso.

## Formato *condition*
Formato: 
- Positive
- Negative

Columnas: 
1. ER
2. PR
3. ALK
4. EGFR
5. PSA

Ordinal encoding: 1 si es *Positive* y 0 en cualquier otro caso.

## Formato *lowhigh*
Formato: 
- Stable
- Low
- High

Columnas: 
1. MSI
2. PD-L1

Ordinal encoding: 1 si *Low*, 2 si *High* y 0 en cualquier otro caso.

### employment
Ordinal encoding: 1 si es *Employed* o *Student* y 0 en cualquier otro caso. 

### diagnosis_date_paciente
Ordinal encoding: reemplazar cada fecha con el *timestamp* a que le corresponde. Como los valores estan o bien en formato ISO o bien en un formato patron, se pueden convertir facilmente con una biblioteca.

### cancer_subtype
Frequency encoding: la solucion ideal seria algun encoding que mantenga la informacion de cada tipo, como one-hot encoding, pero tiene existen demasiados valores. Ademas algo como ordinal encoding, aunque mantiene la informacion, aplica una idea de distancia entre datos que no tiene sentido. Entonces voy a aplicar frequency encoding, porque mantiene la informacion y la distancia entre datos que aplica tiene un sentido deseable. 

### diagnosis
Ordinal encoding: Como el anterior, lo ideal seria un encoding que mantenga la informacion de cada diagnostico como one-hot, pero demasiados datos. Como el objetivo del modelo seria prever si tiene cancer o no, me voy a cargar los diagnosticos distintos y aplicar un 0 si es *No Cancer* y un uno en otro caso.

### blood_type
One-hot encoding: Se pueden representar los valores de esta columna en el formato A, B y R+-. Por ejemplo:
tipo | A | B | R+
AB+    1   1   1
O-     0   0   0
A+     A   0   1 

Entonces aplico one-hot encoding con tres columnas de nombres *blood_group_a*, *blood_group_b*, *blood_r_factor* y al final me cargo *blood_type*.

## Text parsing
En las siguientes columnas pienso en aplicar una tecnica similar que voy a explicar aqui. Le voy a llamar de "frequency correct".

Al investigar los datos de algunas columnas que llevan *strings* he notado que los errores en los textos son poco comunes, es decir, la gran mayoria de datos son una *string* sin errores. Entonces existe una version "correcta" para cada dato en el texto. 

A partir de eso, la tecnica es: sustituir cada dato con el dato mas comun entre el grupo de los datos que se parecen al dato original. Es decir, un maximo entre similtud entre cadenas y frequencia de aparicion. 

No es una tecnica perfecta y puede fallar en algunos casos obscuros, especialmente en aquellos que "confundan" el algoritmo de clasificar similtud entre palabras que voy a usar (algo como levenshtein distance).

### doctor
Primero aplicar "frequency correct" y despues frequency encoding a los valores resultantes. Asi nos libramos de las *strings* se exponen algunas relaciones como el caracter del medico y las relaciones que tienen sus pacientes. 

### symptoms y comorbidities
En ambos casos se tratan de un conjunto de datos.
La columna de *comorbidities* tiene los valores de *arrays* o listas en *strings* de diferentes syntomas. Antes de todo pasar todas a *arrays* de strings. 

A ambas aplicar "frequency correct". Por ultimo, aplicar frequency encoding a cada syntoma individualmente y sumar las frecuencias en de cada lista. 
No es la mejor solucion pero como son demasiadas combinaciones de datos pienso que es una manera de relacionar un numero a la lista.

### medications
Primero aplicar "frequency correct". Despues ordinal encoding al sustituir cada medicamiento con su *RXCUI* correspondiente. El *RXCUI* es una especie de *ID* del medicamento, el cual planeao extrair de la api https://rxnav.nlm.nih.gov". 
No es la mejor solucion pues, aunque el *RXCUI* tenga un razonamiento por detras (por lo que entendido en la web), ordinal encoding adiciona una idea de distancia entre datos puede que no tenga mucho sentido. Lo ideal seria algo como una representacion vectorial de cada medicamiento y incluso he encontrado modelos de clasificacion de medicamientos que hacen justo eso, pero lo veo un poco dificil de integrar. 
