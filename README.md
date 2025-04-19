# Cancer Treatment Preprocessing
A script to preprocess the `data/train.csv` file, a dataset of cancer patients.

# Run the program
Create a virtual enviorment from the `requirements.txt` file.
Execute `python3 preprocess.py` to the `data/out.csv`.

[!WARNING]
This projectis for the Machine Learning extra class in UPM. This repository contains only my personal work. All university-provided materials (e.g., assignment descriptions, starter files, or datasets) have been excluded and are not covered under this license.

## Todo 
Based on feedback: 
 [x] *date_paciente*: Cycling encoding para el mes
 [x] *date_paciente*: Reducir resolucion; Columnas para el dia, mes y ano talvez.
 [x] *symptoms*, *comorbities*: Poner en minusculas 
 [x] *comorbities*: Encode de alguna otra manera (talvez agrupar) 
 [x] *medications*: Multilabel encoding (sklearn: MultiLabelBinarizer) 
 [ ] limpiar codigo con column transformers, pipelines, function transformers
 

## Feedback on first version
El trabajo realizado sobrepasa considerablemente el 10, por tanto no te evaluaré siguiendo los criterios y simplemente te daré feedback. Aun así te adjunto los criterios de corrección por si quieres tomar algunas ideas.

En cuanto a la columna "diagnosis_date_paciente" el timestamp es una forma práctica de utilizar la información. No obstante, puedes explotar mucho más los datos contenidos en ella, por ejemplo, a lo mejor los subtipos de cáncer dependen del mes (una posibilidad es que haya más cáncer de piel tras verano), por tanto te animo a probar los cyclic encodings para el mes. También ten en cuenta que le estás dando una resolución muy grande para algo que no depende tanto del tiempo (ya que el timestamp mide minutos, milisegundos, etc) y puede ser un origen de inestabilidad para los modelos.

Luego, siento que has sacado muy bien la información de las columnas symptoms y comorbidities, pero usando frequency encoding has perdido parte del potencial. Has pasado de tener los síntomas exactos que es información muy útil en el diagnóstico de cualquier cosa a un valor numérico que mide la rareza/frecuencia de los síntomas que tiene una persona. Siento que esto no es demasiado buen indicador de cáncer. Recomendaría ver cuántos síntomas hay (no hay muchos) y hacer un multi-label encoding (en sklearn lo tienes como MultiLabelBinarizer). Para comorbidities te faltaría ponerlos en minúsculas (tienes duplicados en tu extracción con distintas capitalizaciones) y te salen 38 comorbidities distintos... Considerando que hay 84 mil filas en el dataset y es muy complicado hacer overfitting, podría hacerse otro multi-label encoding. En caso contrario, podría intentar agruparse en tipos, pero es algo que tendrías que hacer manual o aplicar técnicas más complicadas que se salen totalmente de lo que vamos a dar en clase.

Paralelamente, tengo que comentarte varias cosas de la columna medications. En primer lugar no tiene mucho sentido sumar los ids de los medicamentos, estás destruyendo información y las relaciones entre los ids son arbitrarias, por tanto recomiendo encodings alternativos. En este sentido va por la misma vía que comorbidities, y recomiendo un MultiLabelBinarizer ya que 36 medicaciones distintas no son tantas en comparación con el número de filas. Si haces esto, no es necesario sacar los ids, porque al modelo le da igual que una columna se llame "Fluorouracil" versus que se llame "4492".

Si no estás de acuerdo en añadir tantas columnas nuevas te recomiendo quizás aplicar una especie de Target encoding aplicado a listas de elementos. Sería realizar algo parecido al frequency encoding, pero en vez de sacar la media de frecuencias de los medicamentos o las comorbilidades, sacas la media de cómo de frecuente tienen pacientes cáncer con cada uno. Pero a mí no me convence demasiado esta opción porque luego para buscar el subtipo o lo adaptas a ello y puedes cometer un data leakage considerable, o no te sirve siquiera.

Para el blood_type te recomiendo codificar también el tipo de sangre 0. Sé que ese tipo de sangre es equivalente a no tener antígenos A o B y entonces estaría implícitamente codificado en el encoding que tienes. El problema es que también tienes valores nulos y entradas que pone "Unknown", entonces estarías diciendo que tener el tipo de sangre 0 es lo mismo que no conocer el tipo de sangre.

Como habrás visto en el nuevo kaggle, no codifiques el subtipo de esa manera, ya que vas a tener que predecir el subtipo concreto.

Dicho todo esto, te recomiendo practicar con sklearn, tiene elementos muy útiles para trabajar con los datos y no lo aprovechas. Recuerda set_output(transform='pandas') para poder trabajar con pandas (sino te lo cambiaría a matrices de numpy). Te comento que utilizando sklearn puedes ponerlo todo en un objeto Pipeline que representa un modelo entero, y no tienes que estar llamando funciones para preprocesar y predecir. Para preprocesar podrías utilizar el ColumnTransformer que te permite realizar operaciones en columnas específicas y para adaptar tus códigos a este formato fácilmente el FunctionTransformer. Mencionado todo esto, no es necesario aplicarlo, se sale del ámbito de este curso aplicar todo esto, pero te doy la idea por si quieres profundizar más.

En general, te felicito por el buen trabajo, cuesta creerse que seas de primero ;)

Criterios de corrección:

Hay unos criterios fijos sobre los que se evaluará del con la escala clásica de 0 a 10, pero se pueden conseguir puntos extra para compensar haberse olvidado de otras cosas o no haber hecho algo bien. Máxima nota aun así es un 10/10.

Quitar filas duplicadas (0.5 pt)
Tratamiento de nulos correcto (1.5 pt)
- Imputación de valores adecuadas (1.5 pt)
- Imputación de valores compleja (+ hasta 1 pt)
Tratamiento de columnas categóricas correctas (4 pt)
- Uso de cualquier encoding (2 pt)
- Uso de encodings adecuados (1.5 pt)
- Uso de encodings complejos (0.5 pt) (+ hasta 1 pt)
Aprovechamiento de columnas (3 pt)
- Eliminación de columnas justificada argumentativamente (1.5 pt)
- Eliminación de columnas justificada con datos (0.5 pt)
- Extracción de información de las columnas (1 pt) (+ hata 1 pt)
Misceláneo (ejemplos a continuación) (1 pt)
- Aplicación de Scalers bien justificados (+ hasta 0.5 pt)
- Aplicación de herramientas customizadas (+ hasta 1 pt)
- Tratamiento de atípicos muy bien justificado (+ hasta 0.5 pt)
- Uso avanzado de los objetos de Sklearn (+ hasta 1 pt)
- Otros (+)
