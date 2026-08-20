import yaml

hotes = [
    {
        "nom": "boucle-locale",
        "adresse": "127.0.0.1",
        "role": "test"
    },
    {
        "nom": "localhost",
        "adresse": "localhost",
        "role": "test"
    },
    {
        "nom": "hote-injoignable",
        "adresse": "192.0.2.1",
        "role": "test"
    }
]

test_yaml = yaml.dump(hotes, sort_keys=False)
print(test_yaml)