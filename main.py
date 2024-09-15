import pygame as pg
import logging
from openai import OpenAI

client = OpenAI(api_key="API_KEY")
import sys


player_turn = True
turn_passed = True
prev_turn_passed = False
typing_active = False
typing_response = ""
num_cards_played = 0
player_move_cheating = False
bot_move_cheating = False
accusation_result = ""

player_coords = [(39, 902), (328, 902), (617, 902), (906, 902), (1195, 902), (1484, 902), (48, 852), (337, 852), (626, 852), (915, 852), (1204, 852), (1493, 852), (58, 802), (347, 802), (636, 802), (925, 802), (1214, 802), (1503, 802), (68, 752), (357, 752), (646, 752), (935, 752), (1224, 752), (1513, 752)]
bot_coords = [(39, -266), (328, -266), (617, -266), (906, -266), (1195, -266), (1484, -266), (48, -216), (337, -216), (626, -216), (915, -216), (1204, -216), (1493, -216), (58, -166), (347, -166), (636, -166), (925, -166), (1214, -166), (1503, -166),(68, -116), (357, -116), (646, -116), (935, -116), (1224, -116), (1513, -116)]

rank_order = ["Ace","2","3","4","5","6","7","8","9","10","Jack","Queen","King"]
rank_order_lower = ["ace","2","3","4","5","6","7","8","9","10","jack","queen","king"]
rank_index = 0

player_rects = []
for i in range(len(player_coords)):
    player_rects.append(pg.Rect(player_coords[i][0],player_coords[i][1],250,363))

recently_played_cards = []
prev_recently_played_cards = []
discard_pile = ["4_of_hearts", "7_of_hearts", "king_of_spades", "6_of_hearts"]
player_hand = ["3_of_diamonds", "6_of_clubs", "8_of_hearts", "7_of_diamonds", "9_of_diamonds", "ace_of_spades", "7_of_spades", "3_of_hearts", "queen_of_hearts", "4_of_spades", "2_of_spades", "2_of_hearts", "5_of_hearts", "9_of_hearts", "10_of_hearts", "king_of_hearts", "king_of_clubs", "6_of_spades", "5_of_spades", "10_of_diamonds", "2_of_clubs", "9_of_clubs", "5_of_diamonds", "jack_of_hearts"]
bot_hand = ["8_of_diamonds", "king_of_diamonds", "6_of_diamonds", "3_of_spades", "4_of_clubs", "jack_of_clubs", "3_of_clubs", "jack_of_spades", "ace_of_diamonds", "ace_of_hearts", "2_of_diamonds", "jack_of_diamonds", "5_of_clubs", "queen_of_clubs", "7_of_clubs", "queen_of_spades", "ace_of_clubs", "4_of_diamonds", "10_of_spades", "9_of_spades", "8_of_clubs", "10_of_clubs", "8_of_spades", "queen_of_diamonds"]



def generate_text(prompt):
    response = client.chat.completions.create(model="gpt-4-turbo",
    messages=[
        {"role": "user", "content": prompt}
    ])
    return response.choices[0].message.content


def drawPlayerHand(player_hand):
    player_hand = player_hand[:24]
    for i in range(len(player_hand)-1, -1, -1):
        current_card = pg.image.load("/Users/jack/Desktop/PygameCards/CardFronts/" + player_hand[i] + ".png")
        current_card = pg.transform.scale(current_card, (250,363))
        screen.blit(current_card, player_coords[i])

def drawBotHand(bot_hand):
    bot_hand = bot_hand[:24]
    for i in range(len(bot_hand)-1, -1, -1):
        current_card = pg.image.load("/Users/jack/Desktop/PygameCards/CardBack.png")
        current_card = pg.transform.scale(current_card, (250,363))
        screen.blit(current_card, bot_coords[i])

def drawDiscardPile(discard_pile):
    text_surface = caption.render("Rank to beat: " + rank_order[rank_index], True, (255,255,255))
    screen.blit(text_surface, (415, 360))
    if len(discard_pile) != 0:
        current_card = pg.image.load("/Users/jack/Desktop/PygameCards/CardBack.png")
        current_card = pg.transform.scale(current_card, (250,363))
        current_card = pg.transform.rotate(current_card, 90)
        screen.blit(current_card, (400,400))
        number_surface = numbertext.render(str(len(discard_pile)), True, (255,255,255))
        screen.blit(number_surface, (323, 430))

def drawEndButton():
    global end_button
    end_button = pg.Rect(210,490,170,60)
    if player_turn == True:
        pg.draw.rect(screen,(0,0,0), end_button)
        pg.draw.rect(screen,(255,255,0), (213,493,164,54))
        text_surface = caption.render('End turn', True, (0,0,0))
        screen.blit(text_surface, (220, 498))
    if player_turn == False:
        pg.draw.rect(screen,(0,0,0), end_button)
        pg.draw.rect(screen,(128,128,128), (213,493,164,54))
        text_surface = caption.render("Bot's turn", True, (255,255,255))
        screen.blit(text_surface, (220, 498))

def drawAccuseButton():
    global accuse_button
    accuse_button = pg.Rect(177,565,203,60)
    pg.draw.rect(screen,(0,0,0), accuse_button)
    if player_turn == True:
        pg.draw.rect(screen,(255,255,0), (180,568,199,54))
        text_surface = caption.render('Accuse Bot', True, (0,0,0))
    if player_turn == False:
        pg.draw.rect(screen,(128,128,128), (180,568,199,54))
        text_surface = caption.render('Accuse Bot', True, (255,255,255))
    screen.blit(text_surface, (187, 575))

def refreshScreen(player_hand,bot_hand,discard_pile):
    screen.fill((0,50,50))
    drawEndButton()
    drawAccuseButton()
    drawPlayerHand(player_hand)
    drawBotHand(bot_hand)
    drawDiscardPile(discard_pile)
    if player_turn == True:
        if num_cards_played == 1:
            text_surface = caption.render("You've played 1 card", True, (255,255,255))
        else:
            text_surface = caption.render("You've played "+str(num_cards_played)+" cards", True, (255,255,255))
    if player_turn == False:
        if num_cards_played == 1:
            text_surface = caption.render("The bot played 1 card", True, (255,255,255))
        else:
            text_surface = caption.render("The bot played "+str(num_cards_played)+" cards", True, (255,255,255))     
    screen.blit(text_surface, (1400, 275))
    text_surface = caption.render(accusation_result, True, (255,255,255))
    screen.blit(text_surface, (1236,690))



def botPlaysCard(index):
    """
    This function allows the bot to play a card from their hand into the pile. A single input, index, indicates the position in the 
    list "bot_hand" a card is to played from. If ANY card that has been played in this way does not have the rank (ace, 2, 3, 4, etc) matching
    what is declared at the end of a turn, the bot will be cheating, and will have to pick up the central pile if accused
    """
    global rank_order
    global rank_index
    global num_cards_played
    global discard_pile
    global bot_hand 
    global turn_passed
    if len(bot_hand)-1 >= index:
        num_cards_played += 1
        discard_pile.append(bot_hand[index])
        recently_played_cards.append(bot_hand[index])
        bot_hand.pop(index)
        refreshScreen(player_hand,bot_hand,discard_pile)
        turn_passed = False

def botAccusesPlayer():
    """
    This function allows the bot to call cheat and accuse the player of cheating. If the player was actually cheating, the player will be forced to pick 
    up all the cards in the pile. However, if this function is called when the player is not actually cheating, the bot will be forced to pick up the
    cards in the pile.
    """
    global player_move_cheating
    global accusation_result
    global discard_pile
    global player_hand
    global bot_hand
    global discard_pile
    global turn_passed
    if player_move_cheating == True:
        accusation_result = "The bot caught you cheating!"
        for card in discard_pile:
            player_hand.append(card)
        player_hand = player_hand[:24]
        discard_pile = []
    if player_move_cheating == False:
        accusation_result = "The bot incorrectly accused you!"
        for card in discard_pile:
            bot_hand.append(card)
            bot_hand = bot_hand[:24]
        discard_pile = []
    refreshScreen(player_hand,bot_hand,discard_pile)
    turn_passed = False

def botEndsTurn(declaration_index):
    """
    This function alllows the bot to end their turn. The function requires a single input: a string indicating the rank they claim the cards they played 
    are worth. The string must belong to the set (ace, 1, 2, 3 , 4, 5, 6 ,7 ,8 ,9, 10, jack, queen, king). Lying about the rank of played cards is allowed, 
    but is a risk. If this function is called without accusing the player or playing any cards, it is a pass, which is a safe play, as there is no risk of 
    taking more cards.
    """
    global accusation_result
    global prev_turn_passed
    global turn_passed
    global discard_pile
    global rank_index
    global player_turn
    global player_move_cheating
    global num_cards_played
    global recently_played_cards
    declaration_index = int(declaration_index)
    accusation_result = ""
    if prev_turn_passed == True and turn_passed == True:
        discard_pile = []
        rank_index += 1
        rank_index = rank_index % 13
    if turn_passed == True:
        prev_turn_passed = True
    else:
        prev_turn_passed = False
    for card in recently_played_cards:
        if rank_order_lower[declaration_index] not in card:
            bot_move_cheating = True
    player_turn = True
    player_move_cheating = False
    num_cards_played = 0
    prev_recently_played_cards = recently_played_cards
    recently_played_cards = []
    turn_passed = True
    refreshScreen(player_hand,bot_hand,discard_pile)

#/You are playing a two player version of the card game cheat. Your objective is to win the game by getting rid of the cards in your hand before your opponent, the user. When playing cards with the  botPlaysCard function, you may follow the rules and play a card of an equal or higher "rank" than what is currently on the pile. You may play multiple cards of the same rank legally. When play cards, you also have another option, to cheat. You are allowed to play whatever cards you like to the pile, but if you are caught by the user, you will be forced to pick up all the cards in the pile, setting you further away from winning by removing all cards from their hands. If you suspect the user has cheated and played cards of a lower or mixed rank, you may call the botAccusesPlayer function and accuse them of cheating. If they are actually cheating, they will be forced to pick up the entire pile, which is good for you. If the user was not cheating however, you will be forced to pick up the entire pile of cards. You finally option is to end your turn with the botEndsTurn function. You will end every turn by calling this function, or use it when you feel you have exhausted your options on the current term, or wish to avoid risking gaining more cards./#

pg.init()

caption = pg.font.SysFont('Arial', 36)
numbertext = pg.font.SysFont('Arial', 48)
smalltext = pg.font.SysFont('Arial', 18)
screen = pg.display.set_mode((1792, 1120), pg.RESIZABLE)
pg.display.set_caption("Card bot demo")

refreshScreen(player_hand,bot_hand,discard_pile)

running = True
while running:
    for ev in pg.event.get():
        if typing_active == True:
            if ev.type == pg.KEYDOWN:
                if ev.key == pg.K_RETURN:
                    valid_answer_found = False
                    for entry in rank_order:
                        if entry.lower() in typing_response.lower() and valid_answer_found == False:
                            valid_answer_found = True
                            for card in recently_played_cards:
                                if entry.lower() not in card:
                                    player_move_cheating = True
                            rank_index = rank_order_lower.index(entry.lower())
                            accusation_result = ""
                            player_turn = False
                            bot_move_cheating = False
                            num_cards_played = 0
                            turn_passed = True
                            prev_recently_played_cards = recently_played_cards
                            recently_played_cards = []
                            typing_active = False
                            refreshScreen(player_hand,bot_hand,discard_pile)
                    if valid_answer_found == False:
                        text_ask_surface = smalltext.render('Try again', True, (255,255,255))
                        screen.blit(text_ask_surface, (1000, 464))
                        typing_response = ""
                        pg.draw.rect(screen,(0,50,50),(1000,518,500,100))
                elif ev.key == pg.K_BACKSPACE:
                    typing_response = typing_response[:-1]
                    pg.draw.rect(screen,(0,50,50),(1000,518,500,100))
                    text_answer_surface = caption.render(typing_response, True, (255,255,255))
                    screen.blit(text_answer_surface, (1000, 518))
                else:
                    typing_response += ev.unicode
                    pg.draw.rect(screen,(0,50,50),(1000,518,500,100))
                    text_answer_surface = caption.render(typing_response, True, (255,255,255))
                    screen.blit(text_answer_surface, (1000, 518))
        if ev.type == pg.MOUSEBUTTONDOWN and player_turn == True and typing_active == False:
            mouse_pos = pg.mouse.get_pos()
            if end_button.collidepoint(mouse_pos):
                if prev_turn_passed == True and turn_passed == True:
                    discard_pile = []
                    rank_index += 1
                    rank_index = rank_index % 13
                if turn_passed == True:
                    accusation_result = ""
                    prev_turn_passed = True
                    player_turn = False
                    bot_move_cheating = False
                    num_cards_played = 0
                    recently_played_cards = []
                    refreshScreen(player_hand,bot_hand,discard_pile)
                else:
                    prev_turn_passed = False
                    typing_active = True
                    text_ask_surface = caption.render('What rank card did you play?', True, (255,255,255))
                    screen.blit(text_ask_surface, (1000, 478))
            if accuse_button.collidepoint(mouse_pos):
                turn_passed = False
                if bot_move_cheating == True:
                    accusation_result = "You caught the bot cheating!"
                    for card in discard_pile:
                        bot_hand.append(card)
                    bot_hand = bot_hand[:24]
                    discard_pile = []
                if bot_move_cheating == False:
                    accusation_result = "You incorrectly accused the bot!"
                    for card in discard_pile:
                        player_hand.append(card)
                        player_hand = player_hand[:24]
                        player_rects = player_rects[:24]
                        player_rects.append(pg.Rect(player_coords[len(player_hand)-1][0],player_coords[len(player_hand)-1][1],250,363))
                    discard_pile = []
                refreshScreen(player_hand,bot_hand,discard_pile)
            click_resolved = False
            for i in range(len(player_hand)):
                if click_resolved == False:
                    if player_rects[i].collidepoint(mouse_pos):
                        turn_passed = False
                        num_cards_played += 1
                        discard_pile.append(player_hand[i])
                        recently_played_cards.append(player_hand[i])
                        player_rects.pop(-1)
                        player_hand.pop(i)
                        refreshScreen(player_hand,bot_hand,discard_pile)
                        click_resolved = True
        if ev.type == pg.QUIT:
            running = False
        if player_turn == False:
            if num_cards_played > 2:
                fallback_bluff = rank_index +1 
                fallback_bluff = fallback_bluff % 13
                botEndsTurn(rank_order[int(fallback_bluff)])
            function_choice = generate_text("You are playing a 2 player version of the card game cheat - you win by getting rid of all your cards from your hand. You have played the following cards already: "+str(recently_played_cards)+" You have the following cards in your hand "+str(bot_hand)+" the current card rank you must play above to avoid cheating "+str(rank_order[rank_index])+" cards are ranked like normal play cards: aces are low. Your opponent has played "+str(len(prev_recently_played_cards))+" cards on their turn. if you think they have cheated, you can call them out, which will force them to take the discard pile of "+str(len(discard_pile))+" cards. If they are not cheating and accuse them, YOU will have to take the discard. If you do not wish to play a card or accuse the player of cheating, you may end your turn. If you wish to play a card, respond with 1. If you wish to accuse the player of cheating, respond with 2. If you wish to end your turn, respond with 3. Respond with ONLY a SINGLE NUMBER")
            if function_choice == "1":
                card_to_play = generate_text("You are playing a 2 player version of the card game cheat - you win by getting all your cards out of your hand. You have decided to play a card into the pile of "+str(len(discard_pile))+" cards. Since we are playing cheat, you have 2 options: you can play honestly, playing a card that is greater in value than "+str(rank_order[rank_index])+" and matches previously played cards "+str(recently_played_cards)+" if applicable. If you wish, you may also cheat and play cards that do not follow the above rules. This can be beneficial, but is also risky, as the player can call you out for cheating, in which case you must take "+str(len(discard_pile))+" extra cards. Respond with an index to this python list of the cards in your hand "+str(bot_hand)+". The card with the index you select will be played. Repond ONLY with a SINGLE integer index to the list, DO NOT use words")
                if int(card_to_play) in range(len(bot_hand)-1):
                    botPlaysCard(int(card_to_play))
                else:
                    botPlaysCard(0)
            if function_choice == "2":
                botAccusesPlayer()
            if function_choice != "1" and function_choice != "2":
                card_rank_bot_claims = generate_text("You are playing a 2 player version of the card game cheat, you win by getting all cards out of your hand. You have chosen to end your turn. Your goal is to state (truthfully or otherwise) the rank of the cards you have played. The rank of card you must have played above is "+str(rank_order[rank_index])+". You have previously chosen to play the following cards: "+str(recently_played_cards)+" Note that if the cards you have played are legal and you correctly state their rank then the user will be forced to gain cards, as opposed to how you be forced to if you were caught lying about the cards you have played. Respond ONLY with a SINGLE string from the following set, where each entry indicates a value you are claiming the cards you played have: {ace, 1, 2, 3 ,4 ,5 ,6 ,7 ,8 ,9, 10, jack, queen, king} DO NOT respond with words")
                if card_rank_bot_claims.lower() in {"ace", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen"}:
                    botEndsTurn(card_rank_bot_claims.lower())
                else:
                    fallback_bluff = rank_index + 1 
                    fallback_bluff = fallback_bluff % 13
                    botEndsTurn(rank_order[int(fallback_bluff)])
    pg.display.flip()
pg.quit()
