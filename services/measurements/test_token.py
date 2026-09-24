import jwt
# Usa la misma clave que pusiste en auth.py
SECRET_KEY = "super_secret_key_compartida" 
ALGORITHM = "HS256"

# Simulamos un usuario con un UUID inventado
payload = {"sub": "123e4567-e89b-12d3-a456-426614174000"}
token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

print("\nCopia este token:\n")
print(token)
print("\n")