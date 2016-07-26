import Interface
import sys

def main():
    app = Interface.QtGui.QApplication(sys.argv)
    window = Interface.Interface()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
