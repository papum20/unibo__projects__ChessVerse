from Game import Game

from const import RANKS



# constants, names, tables etc.

_DATABASES = {
	"registered_users":"backend_registeredusers"
}

# get functions

def get_user_rank(sid:str, rank_type:str) -> int:
	"""
	:param sid: session id
	:param rank_type: game type, form const.RANKS
	"""

	if rank_type not in RANKS:
		raise ValueError("Invalid rank type")
	
	Game.cursor.execute(
		f"""
		SELECT {rank_type} 
		FROM {_DATABASES['registered_users']} 
		WHERE session_id = %s
		""",
		(sid,)
	)
	rank = Game.cursor.fetchone()

	print(f"[db] got rank:{rank}")
	#prendo le informazioni dal database e le salvo in session
	return rank
