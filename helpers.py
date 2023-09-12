
def check_value(value):
    try:
        # Convertir la valeur en entier
        value = int(value)

        # Vérifier si la valeur est entre 1 et 100 inclus
        if 1 <= value <= 100:
            return True
        else:
            return False
    except ValueError:
        return False