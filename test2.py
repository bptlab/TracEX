from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity

# Beispieltexte
text1 = "Der schnelle braune Fuchs springt über den faulen Hund"
text2 = "Ein fauler Hund wird vom schnellen braunen Fuchs überquert"

# Tokenisierung der Texte
tokens1 = text1.split()
tokens2 = text2.split()

# Erstellen eines Word2Vec-Modells
model = Word2Vec([tokens1, tokens2], min_count=1)

# Durchschnittlicher Vektor für jeden Text
vector1 = sum(model.wv[word] for word in tokens1) / len(tokens1)
vector2 = sum(model.wv[word] for word in tokens2) / len(tokens2)

# Cosinus-Ähnlichkeit zwischen den Vektoren
similarity = cosine_similarity([vector1], [vector2])[0][0]
print("Die semantische Ähnlichkeit zwischen den beiden Texten beträgt:", similarity)
