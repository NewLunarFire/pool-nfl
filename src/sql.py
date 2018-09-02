from datetime import datetime
from db import get_db
from hashlib import sha256

def get_matches_for_week(week, uid):
    conn = get_db()
    cur = conn.cursor()

    cur.execute('SELECT matches.rowid, matches.time, thome.name, taway.name, picks.pick_ishome \
        FROM matches \
        JOIN teams AS thome ON matches.home_team = thome.rowid \
        JOIN teams AS taway ON matches.away_team = taway.rowid \
        LEFT JOIN picks ON (picks.match_id = matches.rowid AND picks.user_id = {uid}) \
        WHERE week = {week} \
        ORDER BY matches.time'.format(week=week, uid=uid)
    )
    
    matches = []
    for match in cur.fetchall():
        (id, time, home, away, pick_ishome) = match
        (pick_home, pick_away)  = (False, False) if pick_ishome == None else (pick_ishome, not pick_ishome)
        matches.append({'id': id, 'time': datetime.fromtimestamp(time).strftime("%d %B, %H:%M"), 'home': home, 'away': away, 'pick_home': pick_home, 'pick_away': pick_away})
    
    cur.close()
    return matches

def save_picks(picks, uid):
    conn = get_db()
    cur = conn.cursor()

    for match_id in picks:
        value = '1' if picks[match_id] == 'home' else '0'
        cur.execute("SELECT rowid FROM picks \
            WHERE match_id = {match_id} \
            AND user_id = {uid} \
            LIMIT 1".format(match_id=match_id, uid=uid)
        )

        result = cur.fetchone()
        if result == None:
            cur.execute("INSERT INTO picks (match_id, pick_ishome, user_id) \
                VALUES ({match_id}, {value}, {uid})".format(match_id=match_id, value=value, uid=uid))
        else:
            cur.execute("UPDATE picks SET pick_ishome = {value} WHERE rowid = {rowid}".format(value=value, rowid=result[0]))
    
    conn.commit()
    cur.close()

def verify_user_password(uname, pw):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT rowid, password, salt FROM users WHERE name = '{uname}'".format(uname=uname))
    result = cur.fetchone()
    cur.close()

    if result == None:
        return None
    
    (id, password, salt) = result

    hash = sha256()
    hash.update(pw.encode('utf-8'))
    hash.update(salt.encode('utf-8'))
    print("{hash}".format(hash=hash.hexdigest()))

    if hash.hexdigest() == password:
        return id
    
    return None