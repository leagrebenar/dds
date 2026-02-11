#! /usr/bin/python

import handsLeads
import functions
import dds
import ctypes
import csv
import time
start_time = time.time()

bo = dds.boardsPBN()
DDplays = dds.playTracesPBN()
solved = dds.solvedPlays()

chunkSize = 1

dds.SetMaxThreads(0)

bo.noOfBoards = 13
DDplays.noOfBoards = 13

tablica = [["N",["NT"],["S"],["H"],["D"],["C"]],
           ["E",["NT"],["S"],["H"],["D"],["C"]],
           ["S",["NT"],["S"],["H"],["D"],["C"]],
           ["W",["NT"],["S"],["H"],["D"],["C"]]]

# N E S W
# NT S H D C

trumps = ["S","H","D","C","NT"]
declarers = ["N", "E", "S", "W"]
##PBN = b"N:QJ6.K652.J85.T98 873.J97.AT764.Q4 K5.T83.KQ9.A7652 AT942.AQ4.32.KJ3"

PBNs = []

with open("PBNs.csv", newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        redni_broj = int(row["board"])
        raspored = row["PBN"].encode("utf-8")

        PBNs.append((redni_broj, raspored))

all_tables = []

for board in PBNs:
    PBN = board[1]

    tablica = [["N",["NT"],["S"],["H"],["D"],["C"]],
           ["E",["NT"],["S"],["H"],["D"],["C"]],
           ["S",["NT"],["S"],["H"],["D"],["C"]],
           ["W",["NT"],["S"],["H"],["D"],["C"]]]

    dealer = bytes([PBN[0]])

    all_cards_unordered = PBN[2:].split(b" ")
    all_cards = []

    if dealer == b'N':
        all_cards = all_cards_unordered
    elif dealer == b'E':
        all_cards = [all_cards_unordered[-1]] + all_cards_unordered[0:3]
    elif dealer == b'S':
        all_cards = all_cards_unordered[2:] + all_cards_unordered[0:2]
    else: #W
        all_cards = all_cards_unordered[1:] + [all_cards_unordered[0]]

    possible_ranks = []
    possible_leads = [[],[],[],[]]

    for i in all_cards:
        possible_ranks += [i.split(b".")]

    for i in range(4):
        for j in range(4):
            for c in possible_ranks[i][j]:

                if j == 0:
                    possible_leads[i] += [b"S" + bytes([c])]
                elif j == 1:
                    possible_leads[i] += [b"H" + bytes([c])]
                elif j == 2:
                    possible_leads[i] += [b"D" + bytes([c])]
                else:
                    possible_leads[i] += [b"C" + bytes([c])]

    for first in range(4):

        j = -1

        for i in [4,0,1,2,3]:  # NT, S, H, D, C
            j += 1
            
            leads = possible_leads[first]

            for handno in range(13):
                    bo.deals[handno].trump = i
                    bo.deals[handno].first = first

                    bo.deals[handno].currentTrickSuit[0] = 0
                    bo.deals[handno].currentTrickSuit[1] = 0
                    bo.deals[handno].currentTrickSuit[2] = 0

                    bo.deals[handno].currentTrickRank[0] = 0
                    bo.deals[handno].currentTrickRank[1] = 0
                    bo.deals[handno].currentTrickRank[2] = 0

                    bo.deals[handno].remainCards = PBN

                    DDplays.plays[handno].number = 1 #hands.playNo[handno]
                    DDplays.plays[handno].cards =  leads[handno] #handsLeads.play[handno]

            res = dds.AnalyseAllPlaysPBN(ctypes.pointer(bo), ctypes.pointer(DDplays), ctypes.pointer(solved), chunkSize)

            line = ctypes.create_string_buffer(80)

            if res != dds.RETURN_NO_FAULT:
                    dds.ErrorMessage(res, line)
                    print("DDS error: {}".format(line.value.decode("utf-8")))

            for handno in range(13):

                    tablica[first][j+1] += [ctypes.pointer(solved.solved[handno]).contents.tricks[1]]


##    print()
##    print("BORD:", board)
##    print()
    
##    functions.PrintPBNHand(line, bo.deals[0].remainCards)
    

    all_tables += [(board[0], tablica)]

    # PRINT tablica (moze bit izdvojeno u funkciju

##    for ataker in range(4):
##        print("-------------------------------")
##        print()
##        print("DECLARER:", declarers[declarers.index(tablica[ataker][0])-1])
##        print("ATAKER:", tablica[ataker][0])
##        print()
##        print("      NT  S  H  D  C")
##        print()
##        for i in range(13):
##            print(possible_leads[ataker][i], end = "  ")
##            for j in range(1, 6):
##                print(tablica[ataker][j][i+1], end = "  ")
##            print()

##print(all_tables)

print()
print("--- %s seconds ---" % (time.time() - start_time))

# 30 bordova
#       bez printa      20.640312910079956 seconds
#       s printom       39.615628242492676 seconds

