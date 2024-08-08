import requests

# Configurer le proxy pour les connexions HTTP et HTTPS
proxies = {
    "http": "http://srv-tmg:8080",
    "https": "http://srv-tmg:8080"
}

# Exemple de requête GET en utilisant le proxy configuré
url = "https://example.com/api"

try:
    response = requests.get(url, proxies=proxies)
    response.raise_for_status()  # Vérifie si la requête a réussi (statut 200)
    
    # Afficher le contenu de la réponse
    print(response.text)
except requests.exceptions.RequestException as e:
    print(f"Erreur lors de la requête : {e}")
