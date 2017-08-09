import os
import numpy as np
import operator
import sys
sys.path.append(os.pardir)
sys.path.append('.')


#POS_3x3 = ['cc', 'ca', 'ac', 'aa', 'cb', 'bc', 'ba', 'ab', 'bb']
POS_3x3 = ['dd', 'db', 'bd', 'bb', 'dc', 'cd', 'cb', 'bc', 'cc']
POS_12d = ['ec', 'dd', 'dc', 'db', 'ce', 'cd', 'cb', 'ca', 'bd', 'bc', 'bb', 'ac', 'aa']
POS_nakade = ['ee', 'ed', 'ec', 'eb', 'ea', 'de', 'dd', 'dc', 'db', 'da', 'ce', 'cd', 'cb', 'ca', 'be', 'bd', 'bc', 'bb', 'ba', 'ae', 'ad', 'ac', 'ab', 'aa', 'cc']
#POS_3x3 = ['aa', 'ab', 'ac', 'ba', 'bc', 'ca', 'cb', 'cc', 'bb']
#POS_12d = ['ac', 'bb', 'bc', 'bd', 'ca', 'cb', 'cd', 'ce', 'db', 'dc', 'dd', 'ec', 'cc']


def go():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--output", default='./snapshot/')
    args = parser.parse_args()

    if not os.path.exists(args.output):
        os.makedirs(args.output)

    if args.input:

        sorted_dict = []
        try:
            pattern_dict = np.load(args.input).item()
            print 'pattern count:', len(pattern_dict)

            sorted_dict = sorted(pattern_dict.items(), key=operator.itemgetter(1), reverse=False)
        except:
            sorted_dict.append((int(args.input), 0))
            print 'pattern :', sorted_dict

        num = 0
        for x in sorted_dict:

            if num == 10000:
                break

            if x[1] != num:
                continue
            num += 1

            key = x[0]
            c = key % 5
            key /= 5
            sgf = ''
            if x[0] < 1000000000000000L:

                if c == 3:      # WHITE 
                   sgf += ';W[' + POS_3x3[-1] + ']'
                elif c == 4:    # BLACK
                   sgf += ';B[' + POS_3x3[-1] + ']'

                print c
                x1, x2, y1, y2 = 128, 0, 128, 0
                for i in xrange(8):
                    key /= 5        # LIBERTY
                    c = key % 5
                    print i, c
                    if c == 3:      # WHITE 
                        sgf += ';W[' + POS_3x3[i] + ']'
                    elif c == 4:    # BLACK
                        sgf += ';B[' + POS_3x3[i] + ']'
                    key /= 5
                    if c == 1:
                        if i == 7:
                            x1 = 90
                            x2 = 38
                        elif i == 6:
                            y1 = 90
                            y2 = 38 
                        elif i == 5:
                            y1 = 90
                        elif i == 4:
                            x1 = 90
                        print i
                print x[0]

                with open(os.path.join(args.output, str(id(sorted_dict))), "w") as f:
                    f.write('(;GM[1]SZ[5]' + sgf + ')')
                os.system("gogui-thumbnailer {}{} {}{}_{}.png".format(args.output, str(id(sorted_dict)), args.output, x[1], x[0])) 
                #os.system("gm convert {}{}_{}.png -crop {}x{}+{}+{} {}{}_{}.png".format(args.output, x[1], x[0], x1, y1, x2, y2, args.output, x[1], x[0])) 

            elif x[0] > 5000000000000000000L:

                if c == 3:      # WHITE
                   sgf += ';W[' + POS_nakade[-1] + ']'
                elif c == 4:    # BLACK
                   sgf += ';B[' + POS_nakade[-1] + ']'

                for i in xrange(24):
                    key /= 5        # LIBERTY
                    c = key % 5
                    if c == 3:      # WHITE
                       sgf += ';W[' + POS_nakade[i] + ']'
                    elif c == 4:    # BLACK
                       sgf += ';B[' + POS_nakade[i] + ']'
                    key /= 5
                    #print key, i, c

                with open(os.path.join(args.output, str(id(sorted_dict))), "w") as f:
                    f.write('(;GM[1]SZ[5]' + sgf + ')')
                os.system("gogui-thumbnailer {}{} {}{}_{}.png".format(args.output, str(id(sorted_dict)), args.output, x[1], x[0]))

            else:

                if c == 3:      # WHITE
                   sgf += ';W[' + POS_12d[-1] + ']'
                elif c == 4:    # BLACK
                   sgf += ';B[' + POS_12d[-1] + ']'

                for i in xrange(12):
                    key /= 5        # LIBERTY
                    c = key % 5
                    if c == 3:      # WHITE
                       sgf += ';W[' + POS_12d[i] + ']'
                    elif c == 4:    # BLACK
                       sgf += ';B[' + POS_12d[i] + ']'
                    key /= 5

                with open(os.path.join(args.output, str(id(sorted_dict))), "w") as f:
                    f.write('(;GM[1]SZ[5]' + sgf + ')')
                os.system("gogui-thumbnailer {}{} {}{}_{}.png".format(args.output, str(id(sorted_dict)), args.output, x[1], x[0]))


if __name__ == '__main__':
    go()
