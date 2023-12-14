from Game import Game

from const.users import RANKS



# constants, names, tables etc.

_DATABASES = {
	"registered_users":"backend_registeredusers"
}

# get functions

def get_user_rank(session_id:str, rank_type:str) -> int:
	"""
	:param session_id: session id field
	:param rank_type: game type, form const.RANKS
	"""

	if rank_type not in RANKS:
		print("Invalid rank type")
		return 0

	if session_id is None:
		print("Invalid session id")
		return 0
	
	Game.cursor.execute(
		f"""
		SELECT {rank_type} 
		FROM {_DATABASES['registered_users']} 
		WHERE session_id = %s
		""",
		(session_id,)
	)
	rank = Game.cursor.fetchone()

	print(f"[db] got rank:{rank}")
	#prendo le informazioni dal database e le salvo in session
	return rank

# update functions

def set_user_rank(session_id:str, rank_type:str, diff:int) -> bool:
	"""
	:param session_id: session id field
	:param rank_type: game type, form const.RANKS
	:param diff: `new_rank-old_rank`
	
	:return: True if success, False otherwise
	"""

	if rank_type not in RANKS:
		print("Invalid rank type")
		return 0
	
	if session_id is None:
		print("Invalid session id")
		return 0

	old_rank = get_user_rank(session_id, rank_type)

	Game.cursor.execute(
		f"""
		UPDATE {_DATABASES['registered_users']} 
		SET {rank_type} = %(new_rank)s
		WHERE session_id = %(sid)s
		""",
		{
			'new_rank': old_rank + diff,
   			'sid': session_id
		}
	)
	Game.conn.commit()

	print(f"[db] set rank to:{old_rank + diff}")
	return True