# TSCAH
### By: Corey Matyas [Website](https://coreymatyas.com/)
Code licensed under the MIT License (See `COPYING`)

TSCAH is a bot designed to allow users to play Cards Against Humanity over text chat on 
TeamSpeak servers. Cards Against Humanity is more fun when you can talk to other people, and 
integrating it with TeamSpeak chat is an easy way to be able to manage the game while 
communicating with other players!

TSCAH is written in (hastily-written) Python. Refactoring is fairly high up on the priorities list.

## Use
1. Create a ServerQuery account for the bot. Most default permission sets are fine.
2. `python tscah.py <host> <username> <password> <channelid>`
3. Type `help` in the channel the bot is in for a command list.
4. OPTIONAL: modify `adminUIDs` and `bot_nickname` to limit those who can start and end games and to change the bot's name, respectively.

## Example Session
```
Player 1: join
Player 2: join
Player 2: startgame
TSCAH: Card Czar: Player 2
TSCAH: Black Card: And I would have gotten away with it, too, if it hadn't been for  ___.
TSCAH: Type "choose <number>" to choose your card!
Player 1: choose 4
TSCAH: Black Card: And I would have gotten away with it, too, if it hadn't been for  ___.
TSCAH: White Cards:
TSCAH: 0 - German dungeon porn.
TSCAH: Player 2, type "final <number>" to choose the winner!
Player 2: final 0
TSCAH: Winner: Player 1 // And I would have gotten away with it, too, if it hadn't been for  German dungeon porn..
TSCAH: ---------------------------------------------
TSCAH: Card Czar: Player 1
TSCAH: Black Card: Why can't I sleep at night?
TSCAH: Type "choose <number>" to choose your card!
...
```
**NOTE:** Commands can be sent to the bot either in the channel or over PM.  

Also, the usability of the commands is a bit odd due to the spaghetti code that is `run_game()`. 
Suggestions to improve user experience are appreciated.

## Contributing
Feel free to fix any of the bugs listed in the GitHub Issues tracker and send a pull request. 
I check Github daily typically.

## Notes on Naming
I'm legally obligated to tell you that TSCAH merely stands for TSCAH: an arbitrary ordering 
of letters with no affiliation with any trademark holders. 
Therefore, in all official documentation, it shall be referred to as TSCAH. 
Any expanded form of the name TSCAH is invalid.

## Legalese
Cards Against Humanity is a trademark of Cards Against Humanity LLC. 
Corey Matyas is in no way affiliated with Cards Against Humanity.
All Cards Against Humanity property (used here as `blackcards.txt`, `whitecards.txt`, 
`multipick.txt`, and some game strings) are property of Cards Against Humanity LLC and 
are licensed under Creative Commons BY-NC-SA 2.0 (See `COPYING-CAH`)

TeamSpeak is a trademark of TeamSpeak Systems GmbH.
Corey Matyas is in no way affiliated with TeamSpeak Systems GmbH.
