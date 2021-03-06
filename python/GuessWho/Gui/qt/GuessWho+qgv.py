from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys, os
import charactersLib
import random, weakref
from collections import defaultdict
from qgv import PeopleGraphicsView

CB_STYLE = R"""
QCheckBox::indicator { width: 3px; height: 3px; }
"""

class GameData():
    def __init__(self):
        self.characters, self.characters2 = charactersLib.parse_characters()
        
        people = list()
        for key in self.characters.keys():
            people.append( key )
        self.people = sorted(people)
        
        attributes = set()
        for key in self.characters:
            attributes = attributes | self.characters[key]
        self.attributes = attributes

        attributes2 = set()
        for key in self.characters2:
            attributes2 = attributes2 | self.characters2[key]
        self.attributes2 = attributes2

    def random(self):
        import random
        return self.people[random.randint(0,  len(self.people)-1)]


class GameState:
    def __init__(self):
        self.checkboxLabelTuples = list()
        self.AND_Attributes = None

    def restart(self):
        person = game_data.random()
        self.answersModel.clear()
        self.peopleView.selectAll()

    def personClicked(self, item):
        print "personClicked", item
        print game_state.peopleView

    def clearQuestionsModel(self):
        for item in self.questionItems:
            item.setCheckState( Qt.Unchecked )

    def answer(self, attributes, strAndOr):
        person = self.person
        attribsOfPerson = self.game_data.characters[person]
        if strAndOr=='OR':
            for attrib in attributes:
                if attrib[1]=='attribute' and str(attrib[0]) in attribsOfPerson:
                    return "yes"
                if attrib[1]=='name' and attrib[0]==person:
                    return "yes"
        if strAndOr=='AND':
            for attrib in attributes:
                if not str(attrib[0]) in attribsOfPerson:
                    return "no"
                if not (attrib[1]=='name' and attrib[0]==person):
                    return "no"
            return "yes"
        return "no"

    def rowFromAttributes(self, attributes, strAndOr):
        questionStr = ''
        for x in attributes:
            if len(questionStr)!=0:
                questionStr += ' {} {}'.format(strAndOr, x[0])
            else:
                questionStr = '{}'.format(x[0])
        items = [QStandardItem("{}".format(self.answersModel.rowCount() + 1)),
                 QStandardItem(questionStr + "?"),  QStandardItem(self.answer(attributes, strAndOr))]
        for item in items:
            item.setSelectable(False)
        return items

    def askOR_AND(self, attributes, strAND_OR):
        if not attributes:
           return
        items = self.rowFromAttributes( attributes, strAND_OR )
        self.answersModel.appendRow( items )
        self.answersView.resizeColumnsToContents()
        self.AND_Attributes = None
        self.clearQuestionsModel()

    def askOR(self,  ev):
        self.askOR_AND(self.AND_Attributes, 'OR')

    def askAND(self,  ev):
        self.askOR_AND(self.AND_Attributes, 'AND')

    def questionsListItemChanged(self,  qStandardItem):
        attributes = []
        for item in self.questionItems:
            if item.checkState()==Qt.Checked:
                attributes.append( (item.text(),  item.data().toString()) )
        if len(attributes)==0:
            self.btnOR.setDescription('')
            self.btnAND.setDescription('')
        else:
            strOR = attributes[0][0]
            strAND = attributes[0][0]
            self.AND_Attributes = attributes[:]
            for x in attributes[1:]:
                strOR = strOR + " OR " + x[0]
                strAND = strAND + " AND " + x[0]
            self.btnOR.setDescription(strOR)
            self.btnAND.setDescription(strAND)


game_data = GameData()


def makeQuestionsView():
    qi = list()
    lv = QTreeView()
    model = QStandardItemModel(lv)

    dCategories = defaultdict(list)
    for attribCat, attribute in sorted(game_data.attributes2):
        dCategories[attribCat].append(attribute)
    for attribCat, attribs in dCategories.iteritems():
        rootItem = QStandardItem(attribCat)
        for attribute in attribs:
            item = QStandardItem(attribute)
            item.type = "attribute"
            item.setData( QVariant("attribute") )
            item.setCheckable(True)
            rootItem.appendRow(item)
            qi.append(item)
        model.appendRow(rootItem)
    
    for name in game_data.people:
        item = QStandardItem(name)
        item.type = "name"
        item.setData( QVariant("name") )
        item.setCheckable(True)
        model.appendRow(item)
        qi.append(item)
    lv.setWindowTitle('Example List')
    lv.setMinimumSize(200,200)

    lv.setModel(model)
    lv.expandAll()

    return (lv, model, qi)


def makeAnswersView(game_state):
    answersView = QTableView(None)
    answersView.setShowGrid(False)
    answersView.horizontalHeader().setVisible(False)
    answersView.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
    answersView.verticalHeader().setVisible(False)
    answersView.setColumnWidth(0, 200)
    model = QStandardItemModel(None)
    game_state.answersModel = model
    answersView.setModel( model )
    answersView.resizeColumnsToContents()
    game_state.answersView = answersView
    return (answersView,  model)


def make_AND_OR_VBoxLayout(window):
    layout = QVBoxLayout()
    
    btnOR = QCommandLinkButton('Is The Person...')
    btnOR.setMaximumSize( 300,  10000 )
    layout.addWidget( btnOR )
    btnOR.clicked.connect( window.askOR )
    window.btnOR = btnOR
 
    btnAND = QCommandLinkButton("...")
    btnAND.setMaximumSize( 300,  10000 )
    layout.addWidget( btnAND )
    btnAND.clicked.connect( window.askAND )
    window.btnAND = btnAND
    btnAND.setEnabled(False)
    
    return layout


def makeTopRowLayout(game_state):
    hbox = QHBoxLayout()
    questionsView, questionsModel, qi = makeQuestionsView()
    game_state.questionItems = qi
    questionsModel.itemChanged.connect( game_state.questionsListItemChanged )
    game_state.questionsModel_ = questionsModel
    hbox.addWidget(questionsView)
    layout_AND_OR = make_AND_OR_VBoxLayout(game_state)
    hbox.addLayout( layout_AND_OR )
    answersView, answersModel = makeAnswersView(game_state)
    game_state.answersModel = answersModel
    hbox.addWidget(answersView)

    btnRestart = QCommandLinkButton("Restart")
    btnRestart.clicked.connect( game_state.restart )
    hbox.addWidget( btnRestart )

    return hbox


def makeButtonGridLayout(game_data, game_state):
    buttonGridLayout = QGridLayout()
    x = PeopleGraphicsView.GraphicsView(lambda x: "../tiles/{}.jpg".format(x), None)
    x.setSelectionDidChange( game_state.personClicked )
    x.setPeople( 6, 70, 80, game_data.people )
    buttonGridLayout.addWidget(x)
    game_state.peopleView = x
    return buttonGridLayout

    
def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    game_state = GameState()
    game_state.game_data = game_data
    palette = QPalette()
    centralWidget = QWidget()
    mainLayout = QVBoxLayout()
    game_state.person = game_data.random()

    
    #print game_data.characters[ game_state.person ]
    #print game_state.person

    mainLayout.addLayout( makeTopRowLayout(game_state) )

    buttonGridLayout = makeButtonGridLayout(game_data, game_state)
    mainLayout.addLayout( buttonGridLayout )
    
    window.setCentralWidget(centralWidget)
    centralWidget.setLayout(mainLayout)

    window.resize(200,200)
    window.setWindowTitle('PyQt QGridLayout Add Item Example')
    window.show()

    app.exec_()


if __name__ == '__main__':
    dirOfMe = os.path.dirname(sys.argv[0])
    if dirOfMe:
      os.chdir( dirOfMe )
    main()
