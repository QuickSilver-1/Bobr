TOKEN = '${{ BOT_TOKEN }}'


ip = '${{ IP_SERVER }}'
PGUSER = '${{ PG_USER }}'
PGPASSWORD = '${{ PG_PASSWORD }}'
DATABASE = ' ${{ DATABASE }}'

POSTGRES_URL = f'postgresql://{PGUSER}:{PGPASSWORD}@{ip}/{DATABASE}'

SECRET_KEY = b'${{ SECRET_KEY }}'
