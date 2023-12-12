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

# update functions

def set_user_rank(sid:str, rank_type:str, diff:int) -> bool:
	"""
	:param sid: session id
	:param rank_type: game type, form const.RANKS
	:param diff: `new_rank-old_rank`
	
	:return: True if success, False otherwise
	"""

	if rank_type not in RANKS:
		raise ValueError("Invalid rank type")

	old_rank = get_user_rank(sid, rank_type)

	Game.cursor.execute(
		f"""
		UPDATE {_DATABASES['registered_users']} 
		SET {rank_type} = %(new_rank)s
		WHERE session_id = %(sid)s
		""",
		{
			'new_rank': old_rank + diff,
   			'sid': sid
		}
	)
	Game.conn.commit()

	print(f"[db] set rank to:{old_rank + diff}")
	return True