from slowapi import Limiter
from slowapi.util import get_remote_address

#SECURITY UNTUK API MENCEGAH REQUEST GALAK
limiter = Limiter(key_func=get_remote_address)