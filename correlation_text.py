# text for the correlation tab
# correlation title
correlation_title = {
    'en': '__Correlation of land-use features__',
    'fr': '__Corrélation des caractéristiques d\'utilisation des sols__',
    'de': '__Korrelation der Landnutzungsmerkmale__'
}

correlation_en = "The correlation matrix is a table that shows the correlation coefficients between the magnnitude of " \
                 "the land use features. The magnitude is measured in m² of dry-land attributed to a given land use " \
                 "category. The identification of the land use mix around a survey area serves two purposes."

correlation_en2 = "Positively correlated features are those that increase in magnitude together. Combining correlated " \
                  "features can be used to reduce the number of variables in a model and better understand the " \
                  "effects of the variables under consideration. With the land use data we consider combining the " \
                  "features additively or as a ratio of one to the other. "

correlation_en3 = "Given the results from the correlation matrix, the following variables will be combined to create " \
                  "a new land use case: "

correlation_en4 = "There are two methods used in this example to combine the variables. The first is `<sum>`, which is " \
                  "the sum of the two variables. This operation is valid for land-use variables that are " \
                  "considerred `cover` according to ([linke to tlmRegio]" \
                  "(https://www.swisstopo.admin.ch/de/landschaftsmodell-swisstlmregio)). These categories do not overlap, " \
                  "this means that an area of the map cannot be designated both forest and building.  The second is " \
                  "`<rate>`, this is for land use cases such as `<public services>` which are areas of defined use " \
                  "that are superimposed over a particular land `<cover>` . These elements are multiplied together, " \
                  "to test the _effect_ that `<public services>` has on the underlying land cover. Note: that the " \
                  "results for both operations are scaled between 0 and 1. This gives us another set of variables to " \
                  "evaluate the sampling strategy and sample results."

correlation_fr = "La matrice de corrélation est un tableau qui montre les coefficients de corrélation entre l'ampleur des " \
                 "caractéristiques d'utilisation des terres. L'ampleur est mesurée en m² de terre sèche attribuée à une catégorie " \
                 "d'utilisation des terres donnée. L'identification du mélange d'utilisation des terres autour d'une zone d'enquête " \
                 "remplit deux objectifs."

correlation_fr2 = "Les caractéristiques corrélées positivement sont celles qui augmentent ensemble en amplitude. Combiner des " \
                  "caractéristiques corrélées peut être utilisé pour réduire le nombre de variables dans un modèle et mieux comprendre " \
                  "les effets des variables en cours d'examen. Avec les données d'utilisation des terres, nous envisageons de " \
                  "combiner les caractéristiques de manière additive ou sous forme de rapport de l'une à l'autre."

correlation_fr3 = "Compte tenu des résultats de la matrice de corrélation, les variables suivantes seront combinées pour créer " \
                  "un nouveau cas d'utilisation des terres :"

correlation_fr4 = "Il existe deux méthodes utilisées dans cet exemple pour combiner les variables. La première est `<sum>`, qui est " \
                  "la somme des deux variables. Cette opération est valable pour les variables d'utilisation des terres qui sont " \
                  "considérées comme `couverture` selon ([lien vers tlmRegio]" \
                  "(https://www.swisstopo.admin.ch/de/landschaftsmodell-swisstlmregio)). Ces catégories ne se chevauchent pas, " \
                  "ce qui signifie qu'une zone de la carte ne peut pas être désignée à la fois forêt et bâtiment. La deuxième est " \
                  "`<rate>`, c'est pour les cas d'utilisation des terres tels que `<services publics>` qui sont des zones d'utilisation " \
                  "définie qui se superposent à une certaine `<couverture>` terrestre. Ces éléments sont multipliés ensemble, " \
                  "pour tester l'_effet_ que `<services publics>` a sur la couverture terrestre sous-jacente. Remarque : les " \
                  "résultats pour les deux opérations sont échelonnés entre 0 et 1. Cela nous donne un autre ensemble de variables pour " \
                  "évaluer la stratégie d'échantillonnage et les résultats des échantillons."

correlation_de = "Die Korrelationsmatrix ist eine Tabelle, die die Korrelationskoeffizienten zwischen der Größe der " \
                 "Nutzungseigenschaften des Landes zeigt. Die Größe wird in m² Trockenland gemessen, das einer bestimmten " \
                 "Nutzungskategorie zugeordnet ist. Die Identifizierung des Landnutzungsmixes rund um einen Untersuchungsbereich " \
                 "erfüllt zwei Zwecke."

correlation_de2 = "Positiv korrelierte Merkmale sind solche, die gemeinsam an Größe zunehmen. Das Kombinieren korrelierter " \
                  "Merkmale kann verwendet werden, um die Anzahl der Variablen in einem Modell zu reduzieren und die " \
                  "Effekte der betrachteten Variablen besser zu verstehen. Mit den Daten zur Landnutzung erwägen wir, die " \
                  "Merkmale additiv oder im Verhältnis zueinander zu kombinieren."

correlation_de3 = "Angesichts der Ergebnisse aus der Korrelationsmatrix werden die folgenden Variablen kombiniert, um zu erstellen " \
                  "einen neuen Fall von Landnutzung:"

correlation_de4 = "Es gibt zwei Methoden, die in diesem Beispiel verwendet werden, um die Variablen zu kombinieren. Die erste ist `<sum>`, die " \
                  "Summe der beiden Variablen. Diese Operation ist gültig für die Landnutzungsvariablen, die als `Abdeckung` betrachtet werden " \
                  "laut ([Link zu tlmRegio]" \
                  "(https://www.swisstopo.admin.ch/de/landschaftsmodell-swisstlmregio)). Diese Kategorien überlappen sich nicht, " \
                  "das bedeutet, dass ein Bereich auf der Karte nicht gleichzeitig als Wald und Gebäude bezeichnet werden kann. Die zweite ist " \
                  "`<rate>`, dies ist für Fälle von Landnutzung wie `<öffentliche Dienste>`, die Bereiche mit definierter Nutzung sind " \
                  "die über einer bestimmten `<Abdeckung>` des Landes liegen. Diese Elemente werden multipliziert, " \
                  "um die _Wirkung_ zu testen, die `<öffentliche Dienste>` auf die zugrunde liegende Landbedeckung haben. Hinweis: die " \
                  "Ergebnisse für beide Operationen sind zwischen 0 und 1 skaliert. Dies gibt uns einen weiteren Satz von Variablen, um " \
                  "bewerten Sie die Stichprobenstrategie und die Ergebnisse der Stichproben."

corr_content_en = [correlation_en, correlation_en2, correlation_en3, correlation_en4]
corr_content_fr = [correlation_fr, correlation_fr2, correlation_fr3, correlation_fr4]
corr_content_de = [correlation_de, correlation_de2, correlation_de3, correlation_de4]

land_use_correlation = {
    'en': corr_content_en,
    'fr': corr_content_fr,
    'de': corr_content_de
}