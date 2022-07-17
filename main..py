import os
import discord
import requests
import json
import random
import time
import asyncio
from replit import db
import operator
import re
from keep_alive import keep_alive

client = discord.Client()
bot_token = os.environ['TOKEN']


def get_anime():
    query = ''' 
  query ($user: String)  { 
    MediaListCollection(userName: $user type: ANIME){  
      lists {
       entries {
          id
          media {
            id
            title {
            english
            }
          }
         user {
            name
          }
          score
        }
      }
    }
  }
'''
    users_to_look_in = get_anilist_users_array()
    if (len(users_to_look_in) == 0):
        return []
    random_user = random.choice(users_to_look_in).strip()
    variables = {'user': random_user}
    url = 'https://graphql.anilist.co'
    response = requests.post(url,
                             json={
                                 'query': query,
                                 'variables': variables
                             })
    anime_list = random.choice(
        json.loads(response.text)['data']['MediaListCollection']['lists'])
    anime_entry = random.choice(anime_list['entries'])
    user_who_scored = anime_entry['user']['name']
    anime_name = anime_entry['media']['title']['english']
    anime_score = anime_entry['score']
    # return user_who_scored+" SCORED THE ANIME \""+anime_name+"\" a "+ str(anime_score)
    return [user_who_scored, anime_name, anime_score]

    # print (anime['entries']['title']['english'])


def test_if_user_exists(user):
    query = ''' 
  query ($user: String) {
  MediaListCollection(userName: $user, type: ANIME) {
    user {
      id
      }
    }
  }
  '''
    url = 'https://graphql.anilist.co'
    variables = {'user': user}
    # print(user)
    response = requests.post(url,
                             json={
                                 'query': query,
                                 'variables': variables
                             })
    # print(response.text)
    if (response.status_code == 404):
        return 0
    else:
        return 1


def test_user_score_format(user):
    print(user)
    query = '''
        query ($user: String) {
          User(name: $user) {
            mediaListOptions {
              scoreFormat
            }
          }
        }
        '''
    url = 'https://graphql.anilist.co'
    variables = {'user': user}
    response = requests.post(url,
                             json={
                                 'query': query,
                                 'variables': variables
                             })
    print(response.text)
    score_format = json.loads(
        response.text)['data']['User']['mediaListOptions']['scoreFormat']
    if (score_format == "POINT_3"):
        return 0
    else:
        return 1


def add_anilist_users(user):
    if (test_if_user_exists(user.strip()) == 0):
        return "USER DOES NOT EXIST"
    if (test_user_score_format(user.strip()) == 0):
        return "Can't add this User Reason: is using the Smiley System"
    if 'anilist_users_current' in db.keys():
        anilist_users_current = db["anilist_users_current"]
        anilist_users_current.append(user)
        db["anilist_users_current"] = anilist_users_current
    else:
        db['anilist_users_current'] = [user]
    return "user ADDED"


def delete_anilist_users(user):
    anilist_users_current = db["anilist_users_current"]
    if user in anilist_users_current:
        anilist_users_current.remove(user)
        db["anilist_users_current"] = anilist_users_current
        return "user DELETED"
    else:
        return "user is not in list"


def clear_anilist_users(author):
    if (author.name == 'DODE2K'):
        db["anilist_users_current"] = []
        return "CLEARED"
    else:
        return "can't do that"


def get_anilist_users():
    if 'anilist_users_current' in db.keys():
        anilist_users_current = db["anilist_users_current"]
        if (len(anilist_users_current) > 0):
            return ' '.join(anilist_users_current)

        else:
            return 'NO USERS'
    else:
        return 'NO USERS'


def get_anilist_users_array():
    if 'anilist_users_current' in db.keys():
        anilist_users_current = db["anilist_users_current"]
        if (len(anilist_users_current) > 0):
            return anilist_users_current

        else:
            return []
    else:
        return []


@client.event
async def on_ready():
    print('we have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    timeout_on_play = 0
    if message.author == client.user:
        return
    if message.content.startswith('$phish'):
        name_to_phish = message.content.split("$phish", 1)[1].lower()
        print(re.search(name_to_phish, 'joy'))
        if (operator.contains(name_to_phish, 'dode')):
            await message.channel.send('CAN\'T PHISH ME YOU GET PHISHED')
        elif (name_to_phish == 'joy'):
            await message.channel.send('The Bitch got phished')
        else:
            await message.channel.send(name_to_phish +
                                       ' is phished successfully')
    if message.content.startswith('$users add'):
        user_to_add = name_to_phish = message.content.split("$users add", 1)[1]
        await message.channel.send(add_anilist_users(user_to_add))
    if message.content.startswith('$users remove'):
        user_to_remove = name_to_phish = message.content.split(
            "$users remove", 1)[1]
        await message.channel.send(delete_anilist_users(user_to_remove))
    if message.content.startswith('$users clear'):
        user = message.author
        await message.channel.send(clear_anilist_users(user))
    if message.content.startswith('$users list'):
        await message.channel.send(get_anilist_users())
    if message.content.startswith('$play'):
        channel = message.channel
        # id = my_message.split("$test",1)[1]
        our_game_final = []
        users_that_answerd_correctly = []
        i = 0
        while i < 1:
            our_game = get_anime()
            if (len(our_game) == 0):
                break
            if (our_game[2] == 0):
                continue
            our_game_final = our_game
            break
        if (len(our_game_final) == 0):
            await message.channel.send('no users')
            return
        await message.channel.send('who rated **' + our_game_final[1] +
                                   '** a ' + str(our_game_final[2]))

        def check(m):
            return 1 == 1

        i = -1
        expire_time = time.time() + 10
        while i < 0:
            if (time.time() > expire_time):
                await channel.send('**TIMES OUT!**')
                break
            seconds_left = int(expire_time - time.time())
            await channel.send('**' + str(seconds_left) + '** SECONDS LEFT!')
            try:
                msg = await client.wait_for('message',
                                            timeout=4.0,
                                            check=check)
            except asyncio.TimeoutError:
                continue
            if (msg.author == client.user):
                continue
            if (msg.content.lower() == our_game_final[0].lower()):
                users_that_answerd_correctly.append(msg.author.name)
                continue
        if (len(users_that_answerd_correctly) == 0):
            await channel.send('No one Answerd Correctly')
        else:
            who_answerd_string = ' '.join(users_that_answerd_correctly)
            await channel.send(
                str(len(users_that_answerd_correctly)) +
                ' User/s Answerd Correctly and they are:')
            await channel.send(who_answerd_string)
        await channel.send('the Correct Answer is **' + our_game_final[0] +
                           '**')





keep_alive()
client.run(bot_token)

# test_if_user_exists()

#if multiple users have the same rating both can be answerd



#fix the timer
#if more than 1 line is getting posted at once do it in 1 message insted of multiple
#timeout on $play command
