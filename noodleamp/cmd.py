import argparse
import gobject

from noodleamp import NoodleAmp


parser = argparse.ArgumentParser(description=globals()['__doc__'],
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--file', help='File to play.')
parser.add_argument('--http', help='Launch HTTP server to control player.',
                    action='store_true')


def server():
    from noodleamp.server import app
    app.run(debug=True, port=8000)


def play(filename):
    noodleamp = NoodleAmp()
    main = gobject.MainLoop()

    noodleamp.on_end(lambda n: main.quit())
    noodleamp.play('file://{0}'.format(filename))
    try:
        main.run()
    except KeyboardInterrupt:
        main.quit()


def main():
    args = parser.parse_args()

    if args.http:
        server()
    elif args.file:
        play(args.file)


if __name__ == '__main__':
    main()
